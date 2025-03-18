bl_info = {
    "name": "Auto Rig Addon",
    "blender": (4, 3, 0),
    "category": "Rigging",
    "description": "Creates an armature with bones aligned to every object in a selected collection and parents the objects to their corresponding bones, preserving transforms."
}

import bpy
from mathutils import Vector

def get_collection_items(self, context):
    items = []
    for coll in bpy.data.collections:
        items.append((coll.name, coll.name, ""))
    return items

class AUTO_RIG_OT_operator(bpy.types.Operator):
    bl_idname = "object.auto_rig_operator"
    bl_label = "Auto Rig"
    bl_description = "Create an armature with a bone for each object in the selected collection and parent each object to its corresponding bone."

    def execute(self, context):
        scene = context.scene
        coll_name = scene.auto_rig_collection
        
        if coll_name not in bpy.data.collections:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}
            
        collection = bpy.data.collections[coll_name]

        # Create a new armature data and object at the origin.
        armature_data = bpy.data.armatures.new("AutoRigArmature")
        armature_obj = bpy.data.objects.new("AutoRigArmature", armature_data)
        armature_obj.location = (0, 0, 0)
        scene.collection.objects.link(armature_obj)
        
        # Set the armature as active and switch to Edit mode to create bones.
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones
        
        # Get the inverse of the armature's world matrix.
        inv_matrix = armature_obj.matrix_world.inverted()
        
        # Create a bone for each object in the selected collection.
        for obj in collection.objects:
            bone = edit_bones.new(obj.name)
            # Convert the object's world location into the armature's local space.
            local_loc = inv_matrix @ obj.location
            bone.head = local_loc
            bone.tail = local_loc + Vector((0, 0.5, 0))  # Slight offset to define bone length
        
        # Return to Object mode.
        bpy.ops.object.mode_set(mode='OBJECT')

        # Parent each object to its corresponding bone while preserving its world transform.
        for obj in collection.objects:
            obj.parent = armature_obj
            obj.parent_type = 'BONE'
            obj.parent_bone = obj.name
            # Calculate the bone's rest matrix in world space and invert it.
            bone_rest = armature_obj.data.bones[obj.name].matrix_local.copy()
            obj.matrix_parent_inverse = (armature_obj.matrix_world @ bone_rest).inverted()
        
        self.report({'INFO'}, "Armature created and objects parented to corresponding bones.")
        return {'FINISHED'}

class AUTO_RIG_PT_panel(bpy.types.Panel):
    bl_label = "Auto Rig Addon"
    bl_idname = "AUTO_RIG_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AutoRig"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "auto_rig_collection")
        if scene.auto_rig_collection != "":
            layout.operator("object.auto_rig_operator", text="Auto Rig")

def register():
    bpy.utils.register_class(AUTO_RIG_OT_operator)
    bpy.utils.register_class(AUTO_RIG_PT_panel)
    bpy.types.Scene.auto_rig_collection = bpy.props.EnumProperty(
        name="Group",
        description="Select a collection to rig",
        items=get_collection_items
    )

def unregister():
    bpy.utils.unregister_class(AUTO_RIG_OT_operator)
    bpy.utils.unregister_class(AUTO_RIG_PT_panel)
    del bpy.types.Scene.auto_rig_collection

if __name__ == "__main__":
    register()
