bl_info = {
    "name": "Material Manager",
    "author": "Lancine Doumbia",
    "version": (0, 1, 3),
    "blender": (2, 8, 0),
    "location": "View3D > Sidebar",
    "description": "A tool to manage materials on selected objects",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}




import bpy




def set_material_to_obj(item, material_name, action):
 
    match action:
       
        #add    
        case '1':  
           
            if material_name not in item.data.materials:

                #moved it
                mat = bpy.data.materials[material_name] 
           
                item.data.materials.append(mat) #add the material to obj
       
        # delete
        case '2':
           
            for idx in reversed(range(len(item.data.materials))):
                if item.data.materials[idx].name == material_name:
                    item.data.materials.pop(index=idx)
       


##########################################################################




#duplicate entry guard. helps method list_of_materials      
def material_entry_is_found(collection, find_mat_by_name):
   
    # return true if material name is found in the collection list
    return any(item.material_name == find_mat_by_name for item in collection)                
   


### generate items for dynamic dropdowns
def list_of_materials(self, context):


    # if local items list is empty, add a default entry to prevent errors
    if bpy.data.materials:
       
        # fill the list
        return [(mat.name, mat.name, "") for mat in bpy.data.materials ]
   
    return [("NOTHING", "No items here", "")]


   
def add_the_material_to_list(self, context):    
    bpy.ops.myaddon.dropdown_add_material(option=self.material_dropdown) #call operator to add material to list collection
       
#################################################        






class MYADDON_PG_MaterialEntry(bpy.types.PropertyGroup):
    material_name: bpy.props.StringProperty(name="Material Name")


class MYADDON_PG_LookupMaterials(bpy.types.PropertyGroup):
    material_list: bpy.props.CollectionProperty(type=MYADDON_PG_MaterialEntry)
    material_index: bpy.props.IntProperty(name="Material Index", default=0)
   
    material_dropdown: bpy.props.EnumProperty(
        name="Material Dropdown",
        description="Select a material",
        items=list_of_materials,
        update=add_the_material_to_list
       
        )
    material_flush: bpy.props.BoolProperty(name="Flush Materials", description="Flush all materials from object", default=False)
    material_options: bpy.props.EnumProperty(
        name="Material Options",
        description="Choose an action for the material",
        items=[
            ('1', "Add Material", "Add the selected materials to the objects"),
            ('2', "Remove Material", "Remove the selected materials from the objects"),
        ],
        default='1'
    )
   
#################################################


class MYADDON_UL_Material_History(bpy.types.UIList):
#UIList to show search history
    def draw_item(
        self, context, layout, data, item, icon,
        active_data, active_propname, index
        ):
        # item is a SearchEntry
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=f"{item.material_name}", icon="BRUSH_DATA")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.material_name)


################################################


#add existing material to list via dropdown menu
class MYADDON_OT_dropdown_add_material(bpy.types.Operator):
    bl_idname = "myaddon.dropdown_add_material"
    bl_label = "Add Material to List"
    bl_description = "Add the selected material to the list"
    bl_options = {"REGISTER","UNDO"}
   
    option: bpy.props.StringProperty()
   
   
    def execute(self, context):
        mat_block = context.scene.mat_block
        existing_material = bpy.data.materials[self.option].name
       
        if material_entry_is_found(mat_block.material_list, existing_material):
           
            self.report({'INFO'}, "Material already added to list")
           
        else:
            new_mat = mat_block.material_list.add()
            new_mat.material_name = existing_material
            mat_block.material_index = len(mat_block.material_list) - 1  
       
            self.report({'INFO'}, "Material added to list")
   
             
        return {"FINISHED"}






#remove existing material from list
class MYADDON_OT_remove_material_from_list(bpy.types.Operator):
    bl_idname = "myaddon.remove_material_from_list"
    bl_label = "Remove Material from List"
    bl_description = "Remove the selected material from the list"
    bl_options = {"REGISTER","UNDO"}
 
   
    def execute(self, context):
 
        mat_block = context.scene.mat_block
       
        #remove entry by indice
        mat_block.material_list.remove(mat_block.material_index)
       
        #make index point to next entry
        mat_block.material_index = min(mat_block.material_index, len(mat_block.material_list)-1)
 
        self.report({'INFO'}, "Material removed from list")
        return {"FINISHED"}
   
#clear the list
class MYADDON_OT_clear_material_list(bpy.types.Operator):
    bl_idname = "myaddon.clear_material_list"
    bl_label = "Clear List"
    bl_description = "Clear the entire material list"
    bl_options = {"REGISTER","UNDO"}
 
   
 
    def execute(self, context):
        mat_block = context.scene.mat_block
       
        #clear list
        mat_block.material_list.clear()
        #reset index
        mat_block.material_index = 0


       
        self.report({'INFO'}, "Material list cleared")
        return {"FINISHED"}






################################################


class MYADDON_OT_apply_materials(bpy.types.Operator):
    bl_idname = "myaddon.apply_materials"
    bl_label = "Apply Materials"
    bl_description = "Apply material data to selected objects"
    bl_options = {"REGISTER","UNDO"}




    def execute(self, context):
        mat_block = context.scene.mat_block
        mat_ops = mat_block.material_options
       
        #edit
        new_mats = mat_block.material_list
        trash = mat_block.material_flush




        if trash:
           
            for every in context.selected_objects:
                every.data.materials.clear()
           
            self.report({'INFO'}, "Material data cleared to selected objects")
     
        else:
           
            for every in context.selected_objects:
             
                if every.type == 'MESH':
                   
                    for mat_el in mat_block.material_list:
                     
                        #core functionality
                        set_material_to_obj(every, mat_el.material_name, mat_ops)
                        bpy.ops.myaddon.clear_material_list() #clear list after applying data to objects
                    self.report({'INFO'}, "Material data applied to selected objects")
     
        return {"FINISHED"}




class MYADDON_PT_material_panel(bpy.types.Panel):
    bl_idname = "MYADDON_PT_material_panel"
    bl_label = "Material Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"


    def draw(self, context):
        layout = self.layout
        mat_block = context.scene.mat_block
       
        layout.prop(mat_block, "material_flush", text="Flush Materials", toggle=True)
       
        if mat_block.material_flush:
            layout.label(text="Are you sure?")  
        else:
            layout.prop(mat_block, "material_dropdown", text="Add Material")
            layout.operator(MYADDON_OT_remove_material_from_list.bl_idname, text="Remove Material from List")
            layout.operator(MYADDON_OT_clear_material_list.bl_idname, text="Clear List")
           
            ### design your panel here ###
            layout.template_list(
                "MYADDON_UL_Material_History", "", #List class name, list id
                mat_block, "material_list", # Collection property
                mat_block, "material_index", # Active property
                rows=4   # Number of rows to display
            )
           
           
            layout.prop(mat_block, "material_options", text="Material Action", expand=True)


        #apply
        layout.operator(MYADDON_OT_apply_materials.bl_idname, text="Apply Materials")




classes = [
    MYADDON_PG_MaterialEntry,
    MYADDON_PG_LookupMaterials,
    MYADDON_UL_Material_History ,
    MYADDON_OT_dropdown_add_material,
    MYADDON_OT_remove_material_from_list,
    MYADDON_OT_clear_material_list,
    MYADDON_OT_apply_materials,
    MYADDON_PT_material_panel
   
    ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mat_block = bpy.props.PointerProperty(type=MYADDON_PG_LookupMaterials)
   
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mat_block
   
if __name__ == "__main__":
    register()

