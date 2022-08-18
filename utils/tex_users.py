import bpy


def tex_users(context):
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            for mslot in obj.material_slots:
                if mslot.material == context.material:
                    yield obj
                    break
