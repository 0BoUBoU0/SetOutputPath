bl_info = {
    "name": "Set Output Path",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "This addon will set your render output in the same location where your file is. It will set the folder depending of your file name, the scene name, and if you have get the Snap Files addon, the current version of the scene",
    "location": "PROPERTIES > RENDER PANEL > OUTPUT PANEL",
    "doc_url": "",
    "warning": "",
    "category": "Render",
    "blender": (2,90,0),
    "version": (1,3,342)
}

# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"]).replace(",",".").replace("(","").replace(")","")

# import modules
import os
import bpy

# define global variables
debug_mode = False
separator = "-" * 20
snap_folder = "Snap_Files"

### create property ###
class RENDER_setoutputpathprop (bpy.types.PropertyGroup):
    scenes_selection_options = [("ALL SCENES","ALL SCENES","ALL SCENES",0),("CURRENT SCENE","CURRENT SCENE","CURRENT SCENE",1),("ALL SCENES WITH CURRENT SETTINGS","ALL SCENES WITH CURRENT SETTINGS","ALL SCENES WITH CURRENT SETTINGS",2)]
    scenes_selection : bpy.props.EnumProperty (items = scenes_selection_options,name = "Change outputs",description = "choose selection type",default=1)

    output_customfield_a_prop : bpy.props.StringProperty (default = "",name="", description='first user custom field (A)')
    output_customfield_b_prop : bpy.props.StringProperty (default = "",name="", description='second user custom field (B)')
    output_customfield_c_prop : bpy.props.StringProperty (default = "",name="", description='third user custom field (C)')

    output_custom_filepath : bpy.props.StringProperty (default = "//Output",name="Root Output Folder", description='OutputFolder filepath')
    output_path_previs : bpy.props.StringProperty (default = "[Output Folder]**\\",name="path", description='')

    filepath_options = [("Absolute","Absolute","Absolute",0),("Relative","Relative","Relative",1)]
    filepath_selection : bpy.props.EnumProperty (items = filepath_options,name = "",description = "Default File path format",default=1)

# create panel UPPER_PT_lower
class RENDER_PT_setoutputpath(bpy.types.Panel):
    bl_label = f"{Addon_Name} - {Addon_Version}"
    bl_idname = "RENDER_PT_setoutputpath"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'
    #bl_parent_id = "RENDER_PT_output"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='FILE_FOLDER')

    def draw(self, context):
        layout = self.layout
        setoutputpath_props = context.scene.setoutputpath_props
        output_pathprevis = setoutputpath_props.output_path_previs.replace("**","")

        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.85)
        split.operator('render.setoutputpath', text=Addon_Name, icon="FILE_FOLDER")
        split.prop(setoutputpath_props, "filepath_selection")
        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.9)
        split.label(text=f"path : {output_pathprevis}")
        split.operator('sop.dellastcharacter', text ="", icon="TRIA_LEFT_BAR")
           
class RENDER_PT_setoutputpathfieldsoptions(bpy.types.Panel):
    bl_label = "Fields Options"
    bl_idname = "RENDER_PT_setoutputpathfieldsoptions"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'
    bl_parent_id = "RENDER_PT_setoutputpath"
    #bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='OPTIONS')

    def draw(self, context):
        layout = self.layout
        setoutputpath_props = context.scene.setoutputpath_props
        

        box = layout.box()
        row = box.row()
        row.operator('sop.addcharacter1', text="\\")
        row.operator('sop.addcharacter2', text="_")
        row.operator('sop.addcharacter3', text="-")
        row.operator('sop.addcharacter4', text=".")
        row = box.row()
        row.operator('sop.addcharacteroutputfolder', text="Output Folder")
        row.operator('sop.addcharacterfilename', text="File Name")
        row.operator('sop.addcharacterscenename', text="Scene Name")
        row.operator('sop.addcharacteractivecamera', text="Active Camera")
        row = box.row()
        row.operator('sop.addcharactercustoma', text="Custom A")
        row.operator('sop.addcharactercustomb', text="Custom B")
        row.operator('sop.addcharactercustomc', text="Custom C")
        if 'Snapshots_History' in bpy.data.texts.keys():
            row.operator('sop.addcharacterfileversion', text="File Version")
        else:
            row.operator('sop.addcharacterfileversion', text="File Version (v001)")
        row.separator
        box = layout.box()
        row = box.row()
        row.prop(setoutputpath_props, "output_custom_filepath")
        row = box.row()
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="A Custom")
        split.prop(setoutputpath_props, "output_customfield_a_prop")
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="B Custom")
        split.prop(setoutputpath_props, "output_customfield_b_prop")
        col = row.column()
        split = col.split(factor=2/5)
        split.label(text="C Custom")
        split.prop(setoutputpath_props, "output_customfield_c_prop")

class RENDER_PT_setoutputpathoptions(bpy.types.Panel):
    bl_label = "Advanced Options"
    bl_idname = "RENDER_PT_setoutputpathoptions"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'
    bl_parent_id = "RENDER_PT_setoutputpath"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='MEMORY')

    def draw(self, context):
        layout = self.layout
        setoutputpath_props = context.scene.setoutputpath_props

        
        box = layout.box()
        row = box.row()
        row.prop(setoutputpath_props, "scenes_selection")

        
### create functions ###
def set_element(prop_in,attribute_list):
    prop_out = ()
    if prop_in == attribute_list[0][0]: # none, so nothing
        prop_out = ''
    elif prop_in == attribute_list[0][1]: # OutputFolder file name
        prop_out = attribute_list[1]
    elif prop_in == attribute_list[0][2]: # scene name
        prop_out = attribute_list[2]
    elif prop_in == attribute_list[0][3]: # file version
        prop_out = attribute_list[3]
    elif prop_in == attribute_list[0][4]: # custom a
        prop_out = attribute_list[4]
    elif prop_in == attribute_list[0][5]: # camera name
        prop_out = attribute_list[5]
    elif prop_in == attribute_list[0][6]: # custom b
        prop_out = attribute_list[6]
    #print(f"{prop_out=}")
    return prop_out

def addcharacter(character):
    bpy.context.scene.setoutputpath_props.output_path_previs += f"**{character}"
    return

### operators
class SOP_OT_dellastcharacter(bpy.types.Operator):
    bl_idname = 'sop.dellastcharacter'
    bl_label = "SOP_OT_dellastcharacter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        output_path_previs = bpy.context.scene.setoutputpath_props.output_path_previs
        output_split = output_path_previs.split("**")
        #print(output_split)
        bpy.context.scene.setoutputpath_props.output_path_previs = ""
        for i in range(0,len(output_split)-1):
            if output_split[i]!= "":
                addcharacter(output_split[i])
        
        # if bpy.context.scene.setoutputpath_props.output_path_previs == "":
        #     bpy.context.scene.setoutputpath_props.output_path_previs = "**OutputFolder\\"
        
        return {"FINISHED"}  

class SOP_OT_addcharacter1(bpy.types.Operator):
    bl_idname = 'sop.addcharacter1'
    bl_label = "SOP_OT_addcharacter1"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("\\")
        return {"FINISHED"}  

class SOP_OT_addcharacter2(bpy.types.Operator):
    bl_idname = 'sop.addcharacter2'
    bl_label = "SOP_OT_addcharacter2"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("_")
        return {"FINISHED"}  

class SOP_OT_addcharacter3(bpy.types.Operator):
    bl_idname = 'sop.addcharacter3'
    bl_label = "SOP_OT_addcharacter3"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("-")
        return {"FINISHED"}
    
class SOP_OT_addcharacter4(bpy.types.Operator):
    bl_idname = 'sop.addcharacter4'
    bl_label = "SOP_OT_addcharacter4"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter(".")
        return {"FINISHED"}  

class SOP_OT_addcharactersoutputfolder(bpy.types.Operator):
    bl_idname = 'sop.addcharacteroutputfolder'
    bl_label = "SOP_OT_addcharacteroutputfolder"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Output Folder]")
        return {"FINISHED"}  

class SOP_OT_addcharacterscenename(bpy.types.Operator):
    bl_idname = 'sop.addcharacterscenename'
    bl_label = "SOP_OT_addcharacterscenename"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Scene Name]")
        return {"FINISHED"}  
    
class SOP_OT_addcharacterfilename(bpy.types.Operator):
    bl_idname = 'sop.addcharacterfilename'
    bl_label = "SOP_OT_addcharacterfilename"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[File Name]")
        return {"FINISHED"}  

class SOP_OT_addcharacteractivecamera(bpy.types.Operator):
    bl_idname = 'sop.addcharacteractivecamera'
    bl_label = "SOP_OT_addcharacteractivecamera"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Camera Name]")
        return {"FINISHED"}  

class SOP_OT_addcharactercustoma(bpy.types.Operator):
    bl_idname = 'sop.addcharactercustoma'
    bl_label = "SOP_OT_addcharactercustoma"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Custom A]")
        return {"FINISHED"}  

class SOP_OT_addcharactercustomb(bpy.types.Operator):
    bl_idname = 'sop.addcharactercustomb'
    bl_label = "SOP_OT_addcharactercustomb"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Custom B]")
        return {"FINISHED"} 
    
class SOP_OT_addcharactercustomc(bpy.types.Operator):
    bl_idname = 'sop.addcharactercustomc'
    bl_label = "SOP_OT_addcharactercustomc"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[Custom C]")
        return {"FINISHED"} 
    
class SOP_OT_addcharacterfileversion(bpy.types.Operator):
    bl_idname = 'sop.addcharacterfileversion'
    bl_label = "SOP_OT_addcharacterfileversion"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        addcharacter("[File Version]") 
        return {"FINISHED"}  

### operators
class RENDER_OT_setoutputpath(bpy.types.Operator):
    bl_idname = 'render.setoutputpath'
    bl_label = Addon_Name
    bl_description = "it will set the render scene output at the same location as your file"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):    
        print(f"\n {separator} Begin {Addon_Name} {separator} \n")

        # check which scene to change
        scenes_to_change = []
        scene_ref = bpy.context.scene
        if bpy.context.scene.setoutputpath_props.scenes_selection == "ALL SCENES" or bpy.context.scene.setoutputpath_props.scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
            for scene in bpy.data.scenes:
                scenes_to_change.append(scene)
        else:
            scenes_to_change = [bpy.context.scene]

        print(scenes_to_change)
        print(scene_ref)
        # change output path 
        for scene in scenes_to_change:
            if scene_ref.setoutputpath_props.scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
                scene.setoutputpath_props.output_path_previs = scene_ref.setoutputpath_props.output_path_previs
                scene.setoutputpath_props.output_custom_filepath = scene_ref.setoutputpath_props.output_custom_filepath
                scene.setoutputpath_props.output_customfield_a_prop = scene_ref.setoutputpath_props.output_customfield_a_prop
                scene.setoutputpath_props.output_customfield_b_prop = scene_ref.setoutputpath_props.output_customfield_b_prop
                scene.setoutputpath_props.scenes_selection = scene_ref.setoutputpath_props.scenes_selection

            output_path = bpy.context.scene.setoutputpath_props.output_path_previs
            print(f"{output_path=}")
            output_split = output_path.split("**")
            print(f"{output_split=}")
            
            clean_filepath = ""
            for elem in output_split:
                print(f"{elem=}")
                if elem == "[Output Folder]":
                    print("hey !")
                    if bpy.context.scene.setoutputpath_props.filepath_selection == "Relative":
                        print("rel")
                        elem = f"//{bpy.context.scene.setoutputpath_props.output_custom_filepath}"
                    elif bpy.context.scene.setoutputpath_props.filepath_selection == "Absolute" :
                        print("abs")
                        filename = bpy.data.filepath.split("\\")[-1]
                        filepath_abs = bpy.data.filepath.replace(filename,"")
                        elem = f"{filepath_abs}{bpy.context.scene.setoutputpath_props.output_custom_filepath}"
                    elem += "\\"
                elif elem == "[File Name]":
                    elem = bpy.data.filepath.split("\\")[-1].split(".")[0]
                elif elem == "[Scene Name]":
                    print("scene")
                    elem = scene.name
                elif elem == "[Camera Name]":
                    if scene.camera != None:
                        elem = scene.camera.name
                    else:
                        elem = ""
                elif elem == "[Custom A]":
                    elem = scene.setoutputpath_props.output_customfield_a_prop
                elif elem == "[Custom B]":
                    elem = scene.setoutputpath_props.output_customfield_b_prop
                elif elem == "[Custom C]":
                    elem = scene.setoutputpath_props.output_customfield_c_prop
                elif elem == "[File Version]":
                    last_version_str = '001'
                    if 'Snapshots_History' in bpy.data.texts.keys():
                        snap_history_1st_line = bpy.data.texts['Snapshots_History'].lines[0].body
                        file_version = snap_history_1st_line.replace("--","").split(":")[-1].replace(" ","")
                    else:
                        file_version = last_version_str
                    del last_version_str  
                    elem = file_version 
                
                clean_filepath += elem

            scene.render.filepath =  clean_filepath.replace("\\\\","\\").replace("\\//","\\").replace("////","//")
            
        print(f"\n {separator} {Addon_Name} Finished {separator} \n")
        
        return {"FINISHED"}

# list all classes
classes = (
    RENDER_setoutputpathprop,
    RENDER_PT_setoutputpath,
    RENDER_PT_setoutputpathfieldsoptions,
    RENDER_PT_setoutputpathoptions,
    SOP_OT_dellastcharacter,
    SOP_OT_addcharacter1,
    SOP_OT_addcharacter2,
    SOP_OT_addcharacter3,
    SOP_OT_addcharacter4,
    SOP_OT_addcharactersoutputfolder,
    SOP_OT_addcharacterscenename,
    SOP_OT_addcharacterfilename,
    SOP_OT_addcharacteractivecamera,
    SOP_OT_addcharactercustoma,
    SOP_OT_addcharactercustomb,
    SOP_OT_addcharactercustomc,
    SOP_OT_addcharacterfileversion,
    RENDER_OT_setoutputpath,
    )

sopaddon_keymaps = []

# register classes
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.setoutputpath_props = bpy.props.PointerProperty (type = RENDER_setoutputpathprop)
    # add keymap
    if bpy.context.window_manager.keyconfigs.addon:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")
        keymapitem = keymap.keymap_items.new('render.setoutputpath', #operator
                                             "P", #key
                                            "PRESS", # value
                                            ctrl=True, alt=True
                                            )
        sopaddon_keymaps.append((keymap, keymapitem))

#unregister classes 
def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.setoutputpath_props
    # remove keymap
    for keymap, keymapitem in sopaddon_keymaps:
        keymap.keymap_items.remove(keymapitem)
    sopaddon_keymaps.clear()

