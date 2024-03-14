import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
from typing import Optional, Dict, Tuple, Union
import mathutils

from .xmot import XMot
from .chunks import AnimationChunkV1, MotionPartChunkV3

FRAMETIME = 0.04
        
class GenomeBone:
    def __init__(self):
        self.name = None
        self.resting_pos = None
        self.resting_rot = None
        self.rotation_keyframes = []
        self.position_keyframes = []

GenomeBones = []
def getGenomeBone(name):
    for bone in GenomeBones:
        if bone.name == name:
            return bone
    return None

def calculate_local_matrix(bone):
    if bone is None:
        return Matrix.Identity(4)
    
    if bone.parent:
        local_resting_matrix = bone.parent.global_resting_matrix.inverted() @ bone.global_resting_matrix
        trans = local_resting_matrix.translation
        rot = local_resting_matrix.to_3x3().to_quaternion()
    else:
        local_resting_matrix = bone.global_resting_matrix
        trans = local_resting_matrix.translation
        rot = local_resting_matrix.to_3x3().to_quaternion()

    if bone.genome_quat:
        rot = Quaternion((-bone.genome_quat[3], bone.genome_quat[0], bone.genome_quat[2], bone.genome_quat[1]))
    else:
        rot = Quaternion((1, 0, 0, 0))

    if bone.genome_vec:
        trans = Vector((bone.genome_vec[0], bone.genome_vec[2], bone.genome_vec[1])) / 100
    else:
        trans = Vector((0, 0, 0))
        
    boneOrientationFix = mathutils.Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
    local_matrix = Matrix.LocRotScale(trans, rot, None)
    local_matrix = boneOrientationFix.inverted() @ local_matrix @ boneOrientationFix
    return local_matrix

class BoneNode:
    def __init__(self):
        self.children = []
        self.name = None
        self.parent = None
        self.genome_resting_vec = None
        self.genome_resting_quat = None
        self.genome_vec = None
        self.genome_quat = None
        self.genomeBone = None
        self.root_matrix = None
        self.resting_diff_inv = None
        self.global_resting_matrix = None # The global matrix from Edit mode
        self.startpose_matrix = None      # The local matrix for Pose mode
        self.local_matrix_keyframes = []  # The local matrix for Pose mode
    
    def apply(self, bones):
        posebone = bones.get(self.name)
        if self.startpose_matrix:
            posebone.matrix_basis = self.startpose_matrix
        posebone.keyframe_insert(data_path="location", frame=0)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=0)

        if self.genomeBone:
            for f in self.genomeBone.rotation_keyframes:
                framenum = round(f.time / FRAMETIME)
                if (framenum > bpy.context.scene.frame_end):
                    bpy.context.scene.frame_end = framenum
                
                if f.rotation:
                    self.genome_quat = f.rotation
                    posebone.matrix_basis = self.resting_diff_inv @ calculate_local_matrix(self)
                    posebone.keyframe_insert(data_path="rotation_quaternion", frame=framenum)
        
        if self.genomeBone:
            for f in self.genomeBone.position_keyframes:
                framenum = round(f.time / FRAMETIME)
                if (framenum > bpy.context.scene.frame_end):
                    bpy.context.scene.frame_end = framenum
                
                if f.location:
                    self.genome_vec = f.location
                    posebone.matrix_basis = self.resting_diff_inv @ calculate_local_matrix(self)
                    posebone.keyframe_insert(data_path="location", frame=framenum)
        
        for child in self.children:
            child.apply(bones)
    
def build_bone_tree(bone, editbone, parent = None):
    bone.name = editbone.name
    bone.parent = parent
    bone.global_resting_matrix = editbone.matrix
    
    boneOrientationFix = mathutils.Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
    genomeBone = getGenomeBone(bone.name)
    if bone.parent:
        bone.resting_diff_inv = (bone.parent.global_resting_matrix.inverted() @ bone.global_resting_matrix).inverted()
    else:
        bone.resting_diff_inv = bone.global_resting_matrix.inverted() @ boneOrientationFix
        
    if genomeBone:
        bone.genome_quat = genomeBone.resting_rot
        bone.genome_vec = genomeBone.resting_pos
        bone.genome_resting_vec = bone.genome_vec
        bone.genome_resting_rot = bone.genome_quat
        bone.genomeBone = genomeBone
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    else:
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    
    for next in editbone.children:
        bone.children.append(BoneNode())
        build_bone_tree(bone.children[-1], next, bone)

def load_xmot(filepath):
    xmot = XMot()
    with open(filepath, 'rb') as f:
        xmot.decode(f.read())
    
    obj = bpy.context.active_object
    if not obj:
        raise Exception("No active object, something must have gone wrong")
    
    for i in range(len(xmot.chunks)):
        chunk = xmot.chunks[i]
        print(type(chunk))
        if chunk.get_id() == AnimationChunkV1.ID:
            if chunk.motion == "R":
                bone = GenomeBones[-1]
                for i in range(len(chunk.keyframes)):
                    bone.rotation_keyframes.append(chunk.keyframes[i])
            elif chunk.motion == "P":
                bone = GenomeBones[-1]
                for i in range(len(chunk.keyframes)):
                    bone.position_keyframes.append(chunk.keyframes[i])
        elif chunk.get_id() == MotionPartChunkV3.ID:
            bone = GenomeBone()
            bone.name = chunk.bone
            bone.resting_pos = chunk.pose_location
            bone.resting_rot = chunk.pose_rotation
            GenomeBones.append(bone)
            
    bpy.ops.object.mode_set(mode='EDIT')
    root = BoneNode()
    root.root_matrix = Matrix.Rotation(math.radians(-90), 4, 'Y') @ Matrix.Rotation(math.radians(180), 4, 'X')
    build_bone_tree(root, obj.data.edit_bones[0])
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_end = 0
    root.apply(obj.pose.bones)
    bpy.ops.object.mode_set(mode='OBJECT')
    