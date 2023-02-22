# Taken from Campbell's 3D-Print Toolbox add-on <3

import bmesh
import numpy as np


def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """Returns a transformed, triangulated copy of the mesh"""

    assert obj.type == "MESH"

    if apply_modifiers and obj.modifiers:
        import bpy

        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        me = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        obj_eval.to_mesh_clear()
    else:
        me = obj.data
        if obj.mode == "EDIT":
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # TODO. remove all customdata layers.
    # would save ram

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm


def bmesh_from_object(obj):
    """Object/Edit Mode get mesh, use bmesh_to_object() to write back."""
    me = obj.data

    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)

    return bm


def bmesh_to_object(obj, bm):
    """Object/Edit Mode update the object."""
    me = obj.data

    if obj.mode == "EDIT":
        bmesh.update_edit_mesh(me, loop_triangles=True)
    else:
        bm.to_mesh(me)
        me.update()


def bmesh_calc_area(bm):
    """Calculate the surface area."""
    return sum(f.calc_area() for f in bm.faces)


def polygon_area(vertices):
    """Calculate the area of a polygon given a list of 2D vertex coordinates."""
    # Ensure that the vertices are in the correct format
    vertices = np.array(vertices)
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError("Input vertices must be a 2D array with shape (n, 2).")

    # Calculate the area of the polygon using the Shoelace formula
    x = vertices[:, 0]
    y = vertices[:, 1]
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    return area
