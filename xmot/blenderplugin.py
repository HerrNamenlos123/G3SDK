import bpy

class ImportCustomFileOperator(bpy.types.Operator):
    """Import Custom File Format"""
    bl_idname = "import_custom_file.import_file"
    bl_label = "Import Custom File"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        player = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\player.blend"
        # Open the player.blend file
        bpy.ops.wm.open_mainfile(filepath=player)

        # Custom logic after opening the file
        print("Opened the player.blend file and switched to the Layout workspace.")

        # Your custom logic here
        
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
