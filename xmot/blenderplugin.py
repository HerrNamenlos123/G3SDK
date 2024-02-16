import bpy
import math
import json
from mathutils import Quaternion

class ImportCustomFileOperator(bpy.types.Operator):
    """Import Custom File Format"""
    bl_idname = "import_custom_file.import_file"
    bl_label = "Import Custom File"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.3db"
        # Invoke the import method provided by the other plugin
        getattr(bpy.ops.import_scene, "3db")(filepath=file)
        
        obj = bpy.context.active_object
        if not obj:
            raise Exception("No active object, something must have gone wrong")
            
        # Load the xmot animation
        #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\playerambient.xmot.json"
        xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\xmot.json"
        with open(xmot_file, 'r') as f:
            file = f.read()
            data = json.loads(file)

        # We want this frametime and that many frames
        frametime = 1/25
        framecount = 21
        bone_rotations = {}
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

        # Now we interpolate keyframes
        for section in sections:

            if section["rotation"]:                     # Interpolate rotation keyframes
                section["rotation"]["new_keyframes"] = []

                # We do it for every keyframe we want to have
                bone_name = section["chunk"]["chunk_content"]["label"]
                chunk = section["chunk"]["chunk_content"]
                bone_rotations[bone_name] = []
                for i in range(framecount):
                    time = i * frametime
                    
                    # Find the two keyframes we want to interpolate between
                    lower, upper = findTwoKeyframesToInterpolate(section["rotation"]["chunk_content"]["keyframes"], time)

                    x = map(time, lower["time"], upper["time"], lower["rotation"]["x"], upper["rotation"]["x"])
                    y = map(time, lower["time"], upper["time"], lower["rotation"]["y"], upper["rotation"]["y"])
                    z = map(time, lower["time"], upper["time"], lower["rotation"]["z"], upper["rotation"]["z"])
                    w = map(time, lower["time"], upper["time"], lower["rotation"]["w"], upper["rotation"]["w"])

                    #x = section["chunk"]["chunk_content"]["rotation"][0]
                    #y = section["chunk"]["chunk_content"]["rotation"][1]
                    #z = section["chunk"]["chunk_content"]["rotation"][2]
                    #w = section["chunk"]["chunk_content"]["rotation"][3]

                    # section["rotation"]["new_keyframes"].append([time, w, z, y, x])       # CHANGE THIS
                    # section["rotation"]["new_keyframes"].append([time, y, x, z, -w])       # CHANGE THIS
                    # section["rotation"]["new_keyframes"].append([time, x, y, z, w])       # CHANGE THIS
                    
                    px = chunk["rotation"][0]
                    py = chunk["rotation"][1]
                    pz = chunk["rotation"][2]
                    pw = chunk["rotation"][3]
                    
                    x, y, z, w = x, y, z, w
                    px, py, pz, pw = px, py, pz, pw
                    
                    res = Quaternion((pw, px, py, pz)) * Quaternion((w, x, y, z))
                    res = Quaternion((-res.w, res.y, res.x, res.z))
                    
                    bone_rotations[bone_name].append(res)

            if section["position"]:                     # Interpolate position keyframes
                section["position"]["new_keyframes"] = []

                # We do it for every keyframe we want to have
                for i in range(framecount):
                    time = i * frametime
                    
                    # Find the two keyframes we want to interpolate between
                    lower, upper = findTwoKeyframesToInterpolate(section["position"]["chunk_content"]["keyframes"], time)

                    x = map(time, lower["time"], upper["time"], lower["position"]["x"], upper["position"]["x"])
                    y = map(time, lower["time"], upper["time"], lower["position"]["y"], upper["position"]["y"])
                    z = map(time, lower["time"], upper["time"], lower["position"]["z"], upper["position"]["z"])

                    #section["position"]["new_keyframes"].append([time, x / 1000, y / 1000, z / 1000])

            
        if obj.type == 'ARMATURE':
            for bone in obj.pose.bones:
                print(bone.name)
                for framenum in range(framecount):
                    if bone.name in bone_rotations:
                        bpy.context.scene.frame_set(framenum)
                        bone.rotation_quaternion = bone_rotations[bone.name][framenum]
                        bone.keyframe_insert(data_path="rotation_quaternion", index=-1)  # -1 is for all quaternion components
                    
        bpy.context.scene.frame_end = framecount
        
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
