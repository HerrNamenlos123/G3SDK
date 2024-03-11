import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
from typing import Optional, Dict, Tuple, Union
import mathutils

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

def do():
    xmot = XMot()
    xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot"
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Tool_P0_SawLog_Ambient_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_SitThrone_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    with open(xmot_file, 'rb') as f:
        xmot.decode(f.read())

    file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.3db"
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Paladin.3db"
    # Invoke the import method provided by the other plugin
    getattr(bpy.ops.import_scene, "3db")(filepath=file)
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.xact"
    #bpy.ops.g3blend.io_import_xact(filepath=file)
    
    obj = bpy.context.active_object
    if not obj:
        raise Exception("No active object, something must have gone wrong")
    
    for i in range(len(xmot.chunks)):
        chunk = xmot.chunks[i]
        print(type(chunk))
        if chunk.get_id() == XMot.AnimationChunkV1.ID:
            if chunk.interpolation_kind == "R":
                bone = GenomeBones[-1]
                for i in range(len(chunk.frames)):
                    bone.rotation_keyframes.append(chunk.frames[i])
            elif chunk.interpolation_kind == "P":
                bone = GenomeBones[-1]
                for i in range(len(chunk.frames)):
                    bone.position_keyframes.append(chunk.frames[i])
        elif chunk.get_id() == XMot.MotionPartChunkV3.ID:
            bone = GenomeBone()
            bone.name = chunk.bone
            bone.resting_pos = chunk.pose_location
            bone.resting_rot = chunk.pose_rotation
            GenomeBones.append(bone)
            
    
    def findTwoKeyframesToInterpolate(frames, time):
        lower = None
        upper = frames[0]       # The first keyframe is the upper one

        index = 1
        while time > upper["time"] and index < len(frames):  # Find the first keyframe that is larger than the time
            lower = upper
            upper = frames[index]
            index += 1

        if lower is None:       # If we are at the beginning of the animation, we just take the first keyframe
            lower = upper

        if time > upper["time"]:     # If we are at the end of the animation, we just take the last keyframe
            lower = upper

        return lower, upper

    def map(value, inMin, inMax, outMin, outMax):
        if value < inMin:
            return outMin
        if value > inMax:
            return outMax
        if inMin == inMax:
            return outMin
        return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
            
    #return
    bpy.ops.object.mode_set(mode='EDIT')
    
    root = BoneNode()
    root.root_matrix = Matrix.Rotation(math.radians(-90), 4, 'Y') @ Matrix.Rotation(math.radians(180), 4, 'X')
    build_bone_tree(root, obj.data.edit_bones[0])
    #root_matrix = obj.data.edit_bones[0].matrix
    #root_matrix = Matrix.Identity(4)
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_end = 0
    root.apply(obj.pose.bones)

    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set display mode to Material Preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    break

class ImportCustomFileOperator(bpy.types.Operator):
    """Import Custom File Format"""
    bl_idname = "import_custom_file.import_file"
    bl_label = "Import Custom File"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        do()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportCustomFileOperator.bl_idname, text="Custom File (.custom)")

def register():
    bpy.utils.register_class(ImportCustomFileOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportCustomFileOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

model_object = bpy.data.objects.get("Armature_Player")
if model_object is not None:
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    model_object.select_set(True)
    bpy.ops.object.delete()
else:
    print("Not found")

model_object = bpy.data.objects.get("G3_Hero_Body_Player")
if model_object is not None:
    bpy.ops.object.mode_set(mode='OBJECT')
    model_object.select_set(True)

    def select_children(obj):
        for child in obj.children:
            bpy.ops.object.select_hierarchy(direction='CHILD')
            select_children(child)

    select_children(model_object)
    bpy.ops.object.delete()
    model_object.select_set(True)
    bpy.ops.object.delete()
else:
    print("Not found")
    
do()