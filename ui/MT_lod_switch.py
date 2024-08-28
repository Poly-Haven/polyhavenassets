import bpy
import logging

log = logging.getLogger(__name__)


class PHA_MT_lod_switch(bpy.types.Menu):
    bl_label = "LOD"
    bl_description = (
        "Change the level of detail for this asset. LOD0 is the most detailed, LOD1 is less detailed, and so on"
    )

    def draw(self, context):
        ref = context.object.instance_collection.library_weak_reference
        filepath = ref.filepath
        lods = []
        log.debug(f"Getting LODs for {filepath}")
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            for col in data_from.collections:
                if col[:-1] == ref.id_name[2:-1] and col[-1].isdigit():
                    lods.append(col[-4:])
        lods.sort()

        for lod in lods:
            op = self.layout.operator(
                "pha.lod_switch",
                text=lod,
            )
            op.lod = lod
