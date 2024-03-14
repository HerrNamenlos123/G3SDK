import bpy

from bpy_extras.io_utils import ImportHelper, ExportHelper, orientation_helper, axis_conversion
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, StringProperty
from mathutils import Matrix, Vector

from .import_xmot import load_xmot

bl_info = {
    "name": "Gothic 3",
    "author": "HerrNamenlos123",
    "version": (0, 0, 1),
    "description": "Gothic 3 Import/Export Character animations",
    "blender": (4, 0, 0),
    "location": "File > Import-Export",
    "warning": "",
    "doc_url": "https://github.com/HerrNamenlos123/G3SDK",
    "tracker_url": "https://github.com/HerrNamenlos123/G3SDK/issues",
    "category": "Import-Export",
}

class ImportXmot(bpy.types.Operator, ImportHelper):
    """Import from xmot file format (.xmot)"""
    bl_idname = "g3sdk.io_import_xmot"
    bl_label = 'Import Motion (xmot)'
    bl_options = {'UNDO'}

    filename_ext = ".xmot"
    filter_glob: StringProperty(default="*.xmot", options={'HIDDEN'})

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    def execute(self, context):
        try:
            load_xmot(self.filepath)
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            print('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


# class ExportXmot(bpy.types.Operator, ExportHelper):
#     """Export to xmot file format (.xmot)"""
#     bl_idname = "g3sdk.io_export_xmot"
#     bl_label = 'Export Motion (xmot)'

#     filename_ext = ".xmot"
#     filter_glob: StringProperty(
#         default="*.xmot",
#         options={'HIDDEN'},
#     )

#     use_selection: BoolProperty(
#         name="Selection Only",
#         description="Export selected objects only",
#         default=False,
#     )

#     def execute(self, context):
#         try:
#             write_xmot(self.filepath)
#         except Exception as e:
#             self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
#             print('Error while exporting {}', self.filepath)
#             return {'CANCELLED'}

#         return {'FINISHED'}


# Add to a menu
def menu_func_export(self, context):
    # self.layout.operator(ExportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")
    pass


def menu_func_import(self, context):
    self.layout.operator(ImportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")


def register():
    bpy.utils.register_class(ImportXmot)
    # bpy.utils.register_class(ExportXmot)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportXmot)
    # bpy.utils.unregister_class(ExportXmot)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
