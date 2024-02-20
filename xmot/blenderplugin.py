import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
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
          
    if bone.genome_vec:
        vec = Vector((bone.genome_vec[1], bone.genome_vec[0], bone.genome_vec[2]))
    else:
        vec = Vector((0, 0, 0))
        
    if bone.genome_quat:
        quat = Quaternion((-bone.genome_quat[3], bone.genome_quat[1], bone.genome_quat[0], bone.genome_quat[2]))
    else:
        quat = Quaternion((1, 0, 0, 0))
    
    local_matrix = quat.to_matrix().to_4x4()
    local_matrix.translation = vec / 100
    return local_matrix

class Frame:
    def __init__(self):
        self.time = 0
        self.position = None
        self.rotation = None

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
        '''
        posebone.matrix_basis = Matrix.Identity(4)
        posebone.keyframe_insert(data_path="location", frame=0)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=0)
        if self.startpose_matrix:
            posebone.matrix_basis = self.startpose_matrix
        posebone.keyframe_insert(data_path="location", frame=500)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=500)
        bpy.context.scene.frame_end = 500
        A'''
        
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
                
                if f.position:
                    self.genome_vec = f.position
                    posebone.matrix_basis = self.resting_diff_inv @ calculate_local_matrix(self)
                    posebone.keyframe_insert(data_path="location", frame=framenum)
        
        for child in self.children:
            child.apply(bones)
    
def build_bone_tree(bone, editbone, parent = None):
    bone.name = editbone.name
    bone.parent = parent
    bone.global_resting_matrix = editbone.matrix
    
    genomeBone = getGenomeBone(bone.name)
    if bone.parent:
        bone.resting_diff_inv = (bone.parent.global_resting_matrix.inverted() @ bone.global_resting_matrix).inverted()
    else:
        bone.resting_diff_inv = Matrix.Identity(4)
        
    if bone.root_matrix:
        bone.resting_diff_inv = bone.root_matrix @ bone.resting_diff_inv
        
    if genomeBone:
        bone.genome_quat = genomeBone.resting_rot
        bone.genome_vec = genomeBone.resting_pos
        bone.genome_resting_vec = bone.genome_vec
        bone.genome_resting_rot = bone.genome_quat
        bone.genomeBone = genomeBone
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    else:
        bone.genome_quat = [0, 0, 0, 1]
        bone.genome_vec = [0, 0, 0]
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    
    for next in editbone.children:
        bone.children.append(BoneNode())
        build_bone_tree(bone.children[-1], next, bone)

def do():
    file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.3db"
    # Invoke the import method provided by the other plugin
    getattr(bpy.ops.import_scene, "3db")(filepath=file)
    
    obj = bpy.context.active_object
    if not obj:
        raise Exception("No active object, something must have gone wrong")
        
    # Load the xmot animation
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\playerambient.xmot.json"
    xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\xmot.json"
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\piercehit.json"
    with open(xmot_file, 'r') as f:
        file = f.read()
        data = json.loads(file)

    for i in range(len(data['content']['lma_file']['chunks'])):
        chunk = data['content']['lma_file']['chunks'][i]
        if chunk["chunk_type"] == "Animation":      # This asset is a frame asset, so we merge it into the last asset, which was a MotionPart
            if chunk["chunk_content"]["frame_type"] == "LR":          # Rotation asset
                bone = GenomeBones[-1]
                for i in range(chunk["chunk_content"]["frame_count"]):
                    frame = Frame()
                    frame.time = chunk["chunk_content"]["keyframes"][i]["time"]
                    frame.rotation = chunk["chunk_content"]["keyframes"][i]["rotation"]
                    bone.rotation_keyframes.append(frame)
            elif chunk["chunk_content"]["frame_type"] == "LP":        # Position asset
                bone = GenomeBones[-1]
                for i in range(chunk["chunk_content"]["frame_count"]):
                    frame = Frame()
                    frame.time = chunk["chunk_content"]["keyframes"][i]["time"]
                    frame.position = chunk["chunk_content"]["keyframes"][i]["position"]
                    bone.position_keyframes.append(frame)
        else: # A MotionPart: Create a new bone
            bone = GenomeBone()
            bone.name = chunk["chunk_content"]["label"]
            bone.resting_pos = chunk["chunk_content"]["position"]
            bone.resting_rot = chunk["chunk_content"]["rotation"]
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
do()