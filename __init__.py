bl_info = {
    "name": "Set Output Path",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "This addon will set your render output in the same location where your file is.",
    "location": "PROPERTIES > RENDER PANEL > OUTPUT PANEL",
    "doc_url": "",
    "warning": "",
    "category": "Render",
    "blender": (2, 90, 0),
    "version": (2,0,31)
}


# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"])
Addon_Version = Addon_Version[1:8].replace(",",".")

import os
import bpy

# Define global variables
debug_mode = False
separator = "-" * 20
snap_folder = "Snap_Files"

# Create property group
class RENDER_setoutputpathprop(bpy.types.PropertyGroup):
    scenes_selection_options = [
        ("ALL SCENES", "ALL SCENES", "ALL SCENES"),
        ("CURRENT SCENE", "CURRENT SCENE", "CURRENT SCENE"),
        ("ALL SCENES WITH CURRENT SETTINGS", "ALL SCENES WITH CURRENT SETTINGS", "ALL SCENES WITH CURRENT SETTINGS")
    ]
    scenes_selection: bpy.props.EnumProperty(
        items=scenes_selection_options,
        name="Change outputs",
        description="Choose selection type",
        default="CURRENT SCENE"
    )

    output_customfield_a_prop: bpy.props.StringProperty(default="", name="", description='First user custom field (A)')
    output_customfield_b_prop: bpy.props.StringProperty(default="", name="", description='Second user custom field (B)')
    output_customfield_c_prop: bpy.props.StringProperty(default="", name="", description='Third user custom field (C)')

    output_custom_filepath: bpy.props.StringProperty(default="//Output", name="Root Output Folder", description='Output folder filepath')
    output_path_previs: bpy.props.StringProperty(default="[Output Folder]**\\", name="Path previs", description='')
    output_corresponding_prop : bpy.props.StringProperty(name="Translation",default="",description='translate field a to field b, separated by ",". I.E. "Image=rgba,Alpha=alpha"')

    filepath_options = [("Absolute", "Absolute", "Absolute"), ("Relative", "Relative", "Relative")]
    filepath_selection: bpy.props.EnumProperty(
        items=filepath_options,
        name="",
        description="Default file path format",
        default="Relative"
    )

# Create panel for output path
class RENDER_PT_setoutputpath(bpy.types.Panel):
    bl_label = f"Set Output Path - {Addon_Version}"
    bl_idname = "RENDER_PT_setoutputpath"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'

    def draw_header(self, context):
        self.layout.label(text="", icon='FILE_FOLDER')

    def draw(self, context):
        layout = self.layout
        setoutputpath_props = context.scene.setoutputpath_props
        output_pathprevis = setoutputpath_props.output_path_previs.replace("**", "")

        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.85)
        split.operator('render.setoutputpath', text="Set Output Path", icon="FILE_FOLDER")
        split.prop(setoutputpath_props, "filepath_selection")
        
        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.9)
        split.label(text=f"Path: {output_pathprevis}")
        split.operator('sop.dellastcharacter', text="", icon="TRIA_LEFT_BAR")

# Create panel for field options
class RENDER_PT_setoutputpathfieldsoptions(bpy.types.Panel):
    bl_label = "Fields Options"
    bl_idname = "RENDER_PT_setoutputpathfieldsoptions"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'
    bl_parent_id = "RENDER_PT_setoutputpath"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        def ui_blocs(list):
            iter = 0
            for char, label,icon in list:
                row.operator('sop.add_character_enum', text=label, icon=icon).character = char
                iter += 1
        # main options
        row = box.row()
        char_options_A = [
            ("[Output Folder]", "Output Folder","FILE_FOLDER"),
            ("[Scene Name]", "Scene Name","SCENE_DATA"),
            ("[File Name]", "File Name","FILE"),
            ("[Camera Name]", "Camera Name","CAMERA_DATA"),
            ("[File Version]", "File Version","LINENUMBERS_ON")
        ]
        ui_blocs(char_options_A)
        # separators
        row = box.row()
        char_options_B = [
            ("\\", "Backlash \\","NONE"),
            ("_", "Underscore _","NONE"),
            ("-", "Dash -","NONE"),
            (".", "Dot .","NONE"),
        ]
        ui_blocs(char_options_B)
        # customs
        row = box.row()
        char_options_C = [
            ("[Custom A]", "Custom A","NONE"),
            ("[Custom B]", "Custom B","NONE"),
            ("[Custom C]", "Custom C","NONE"),
        ]
        ui_blocs(char_options_C)
        
        box = layout.box()
        row = box.row()
        row.prop(context.scene.setoutputpath_props, "output_custom_filepath")
        row = box.row()
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="A Custom")
        split.prop(context.scene.setoutputpath_props, "output_customfield_a_prop")
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="B Custom")
        split.prop(context.scene.setoutputpath_props, "output_customfield_b_prop")
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="C Custom")
        split.prop(context.scene.setoutputpath_props, "output_customfield_c_prop")
        row = box.row()
        row.prop(VLToolbox_props, "output_corresponding_prop")

# Operator for deleting the last character
class SOP_OT_dellastcharacter(bpy.types.Operator):
    bl_idname = 'sop.dellastcharacter'
    bl_label = "Delete Last Character"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        output_path_previs = context.scene.setoutputpath_props.output_path_previs
        output_split = output_path_previs.split("**")
        context.scene.setoutputpath_props.output_path_previs = "**".join(output_split[:-1])
        return {"FINISHED"}

# Generic operator for adding characters
class SOP_OT_add_character_enum(bpy.types.Operator):
    bl_idname = 'sop.add_character_enum'
    bl_label = "Add Character"
    bl_description = "Adds a character or field to the path"
    bl_options = {"REGISTER", "UNDO"}

    character: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.setoutputpath_props.output_path_previs += f"**{self.character}"
        return {"FINISHED"}

# Operator for setting output path
class RENDER_OT_setoutputpath(bpy.types.Operator):
    bl_idname = 'render.setoutputpath'
    bl_label = "Set Output Path"
    bl_description = "Set the render output path based on current settings"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print(f"\n {separator} Begin Set Output Path {separator} \n")
        scenes_to_change = []
        scene_ref = context.scene
        if scene_ref.setoutputpath_props.scenes_selection in ["ALL SCENES", "ALL SCENES WITH CURRENT SETTINGS"]:
            scenes_to_change = bpy.data.scenes
        else:
            scenes_to_change = [scene_ref]

        for scene in scenes_to_change:
            if scene_ref.setoutputpath_props.scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
                scene.setoutputpath_props.output_path_previs = scene_ref.setoutputpath_props.output_path_previs
                scene.setoutputpath_props.output_custom_filepath = scene_ref.setoutputpath_props.output_custom_filepath
                scene.setoutputpath_props.output_customfield_a_prop = scene_ref.setoutputpath_props.output_customfield_a_prop
                scene.setoutputpath_props.output_customfield_b_prop = scene_ref.setoutputpath_props.output_customfield_b_prop
                scene.setoutputpath_props.scenes_selection = scene_ref.setoutputpath_props.scenes_selection
            output_path = scene.setoutputpath_props.output_path_previs
            output_split = output_path.split("**")
            complete_filepath = ""
            for elem in output_split:
                if elem == "[Output Folder]":
                    if scene.setoutputpath_props.filepath_selection == "Relative":
                        elem = f"//{scene.setoutputpath_props.output_custom_filepath}"
                    else:
                        filename = bpy.data.filepath.split("\\")[-1]
                        filepath_abs = bpy.data.filepath.replace(filename, "")
                        elem = f"{filepath_abs}{scene.setoutputpath_props.output_custom_filepath}"
                    elem += "\\"
                elif elem == "[File Name]":
                    elem = bpy.data.filepath.split("\\")[-1].split(".")[0]
                elif elem == "[Scene Name]":
                    elem = scene.name
                elif elem == "[Camera Name]":
                    elem = scene.camera.name if scene.camera else ""
                elif elem == "[Custom A]":
                    elem = scene.setoutputpath_props.output_customfield_a_prop
                elif elem == "[Custom B]":
                    elem = scene.setoutputpath_props.output_customfield_b_prop
                elif elem == "[Custom C]":
                    elem = scene.setoutputpath_props.output_customfield_c_prop
                elif elem == "[File Version]":
                    if 'Snapshots_History' in bpy.data.texts.keys():
                        snap_history = bpy.data.texts['Snapshots_History'].lines[0].body
                        file_version = snap_history.replace("--", "").split(":")[-1].strip()
                    else:
                        file_version = "v001"
                    elem = file_version
                
                complete_filepath += elem
            # clean the filepath
            clean_filepath = complete_filepath.replace("\\\\", "\\").replace("\\//", "\\").replace("////", "//")
            # translate filepath regarding what user needs
            if scene.setoutputpath_props.output_corresponding_prop != "":
                corresponding_list = output_corresponding_prop.split(',')
                corresponding_dict = {}
                for corres in corresponding_list:
                    corres = corres.replace(" ","")
                    corres_split = corres.split("=")
                    corresponding_dict[corres_split[0]] = corres_split[-1]
                # check if user wants to change the string
                for string in corresponding_dict.keys():
                    if string in clean_filepath :
                        corrected_filepath = clean_filepath.replace(string,corresponding_dict.get(string))
            
            # change filepath
            scene.render.filepath = corrected_filepath

        print(f"\n {separator} Set Output Path Finished {separator} \n")
        return {"FINISHED"}

# Register classes
classes = (
    RENDER_setoutputpathprop,
    RENDER_PT_setoutputpath,
    RENDER_PT_setoutputpathfieldsoptions,
    SOP_OT_dellastcharacter,
    SOP_OT_add_character_enum,
    RENDER_OT_setoutputpath,
)

sopaddon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.setoutputpath_props = bpy.props.PointerProperty(type=RENDER_setoutputpathprop)

def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.setoutputpath_props

if __name__ == "__main__":
    register()
