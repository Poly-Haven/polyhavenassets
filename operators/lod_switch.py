import bpy
import logging

log = logging.getLogger(__name__)


class PHA_OT_lod_switch(bpy.types.Operator):
    bl_idname = "pha.lod_switch"
    bl_label = "LOD Switch"
    bl_description = (
        "Change the level of detail for this asset. LOD0 is the most detailed, LOD1 is less detailed, and so on"
    )
    bl_options = {"INTERNAL"}

    lod: bpy.props.StringProperty()  # LOD0, LOD1, etc

    def set_collection(self, context, ref_id_name):
        # We can't just find it in bpy.data.collections since there may be name conflicts,
        # we need to iterate over the collections, find those with the same library filepath,
        # and check the reference id_name (which is 'GR' plus the collection name in the original file).
        for col in bpy.data.collections:
            ref = col.library_weak_reference
            if (
                ref
                and ref.filepath == context.object.instance_collection.library_weak_reference.filepath
                and ref.id_name == ref_id_name
            ):
                context.object.instance_collection = col
                context.object.name = col.name  # Update the object name to avoid confusion
                return True
        return False

    def execute(self, context):
        ref_id_name = context.object.instance_collection.library_weak_reference.id_name[:-4] + self.lod
        collection_exists = self.set_collection(context, ref_id_name)
        if collection_exists:
            return {"FINISHED"}

        # Append the collection
        log.debug(f"Appending collection {ref_id_name}")
        collection_name = ref_id_name[2:]  # Remove 'GR' prefix for collection instances
        filepath = context.object.instance_collection.library_weak_reference.filepath
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.collections = [collection_name]

        # Set the new collection
        success = self.set_collection(context, ref_id_name)
        if not success:
            self.report({"ERROR"}, f"Cannot find collection {ref_id_name}")
            return {"CANCELLED"}

        return {"FINISHED"}
