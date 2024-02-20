import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
import mathutils

class BoneNode:
    __init__(self, edit_bones = None, parent = None):
        self.children = []
        self.parent = parent
        self.genome_vec = None
        self.genome_quat = None
        self.edit_matrix = None
        self.edit_bone = None
        self.pose_bone = None
        if edit_bones is not None:
            self.build_bone_tree()
    
    def build_bone_tree(self):
        self.build_bone_tree()


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

    # We want this frametime and that many frames
    frametime = 1/25
    framecount = 21
    bone_rotations = {}
    resting_positions = {}
    sections = []
    for i in range(len(data['content']['lma_file']['chunks'])):
        chunk = data['content']['lma_file']['chunks'][i]
        if chunk["chunk_type"] == "Animation":      # This asset is a frame asset, so we merge it into the last asset, which was a MotionPart
            if chunk["chunk_content"]["frame_type"] == "LR":          # Rotation asset
                sections[-1]["rotation"] = chunk
            elif chunk["chunk_content"]["frame_type"] == "LP":        # Position asset
                sections[-1]["position"] = chunk
        else: # A MotionPart
            sections.append({ "chunk": chunk, "rotation": None, "position": None })
            
    
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
    
    def calculate_global_matrix(bone):
        if bone is None:
            return Matrix.Identity(4)
              
        vec = Vector((bone["genome_vec"][1], bone["genome_vec"][0], bone["genome_vec"][2]))
        quat = Quaternion((-bone["genome_quat"][3], bone["genome_quat"][1], bone["genome_quat"][0], bone["genome_quat"][2]))
        
        local_matrix = quat.to_matrix().to_4x4()
        local_matrix.translation = vec / 100
        
        parent_global_matrix = calculate_global_matrix(bone["parent"])
        global_matrix = parent_global_matrix @ local_matrix
        return global_matrix

    bones = {}
    for section in sections:
        chunk = section["chunk"]["chunk_content"]
        label = chunk["label"]
        bones[label] = {}
        bones[label]["position"] = chunk["position"]
        bones[label]["rotation"] = chunk["rotation"]
    
    def build_bone_tree(editbone, current_bone, root_matrix):
        print("Building bone " + editbone.name)
        current_bone["name"] = editbone.name
        current_bone["editbone"] = editbone
        current_bone["edit_matrix"] = editbone.matrix
        
        if current_bone["name"] not in bones:
            current_bone["genome_quat"] = [0, 0, 0, 1]
            current_bone["genome_vec"] = [0, 0, 0]
            current_bone["pose_matrix"] = root_matrix.inverted() @ calculate_global_matrix(current_bone)
            #current_bone["pose_matrix"] = Matrix.Identity(4)
        else:
            current_bone["genome_quat"] = bones[current_bone["name"]]["rotation"]
            current_bone["genome_vec"] = bones[current_bone["name"]]["position"]
            current_bone["pose_matrix"] = root_matrix.inverted() @ calculate_global_matrix(current_bone)
        
        if current_bone["parent"] is not None:
            print(current_bone["parent"]["pose_matrix"])
            current_bone["edit_diff"] = current_bone["parent"]["edit_matrix"].inverted() @ current_bone["edit_matrix"]
            current_bone["pose_diff"] = current_bone["parent"]["pose_matrix"].inverted() @ current_bone["pose_matrix"]
            current_bone["diff"] = current_bone["edit_diff"].inverted() @ current_bone["pose_diff"]
            #editbone.matrix = current_bone["pose_matrix"]
        else:
            current_bone["edit_diff"] = Matrix.Identity(4)
            current_bone["pose_diff"] = Matrix.Identity(4)
            current_bone["diff"] = Matrix.Identity(4)
            
        #current_bone["diff"] = current_bone["edit_matrix"].inverted() @ current_bone["pose_matrix"]
        #current_bone["diff"] = current_bone["diff"].to_3x3().to_4x4()
        #current_bone["diff"] = Quaternion((1, 0.1, 0, 0)).to_matrix().to_4x4()
        #editbone.matrix = Matrix.Identity(4)
        #editbone.matrix = current_bone["pose_matrix"]
        #if ("Hero_Right_Leg_Leg_2" in current_bone["name"]):
            #print(current_bone["edit_matrix"])
        #editbone.matrix = Matrix.Identity(4)
        #editbone.matrix = Matrix.Rotation(math.radians(90), 4, 'X') @ editbone.matrix
        
        current_bone["children"] = []
        for child in editbone.children:
            current_bone["children"].append({})
            current_bone["children"][-1]["parent"] = current_bone
            build_bone_tree(child, current_bone["children"][-1], root_matrix)
    
    def apply_bone_tree(current_bone):
        posebone = obj.pose.bones.get(current_bone["name"])
        parent = current_bone["parent"]
        posebone.matrix_basis = current_bone["diff"]
        for child in current_bone["children"]:
            apply_bone_tree(child)
            
    #return
    bpy.ops.object.mode_set(mode='EDIT')
    root = BoneNode(obj.data.edit_bones)
    #root_matrix = obj.data.edit_bones[0].matrix
    #root_matrix = Matrix.Identity(4)
    
    bpy.ops.object.mode_set(mode='POSE')
    apply_bone_tree(root_bone)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    bpy.context.scene.frame_end = framecount

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