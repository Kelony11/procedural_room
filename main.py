# NOTE:
# This script MUST be run inside Blender's Python environment.
# It will NOT run in a standard Python interpreter.
# 
# This file contains the example code provided in the homework. 
# However, the code is not complete and will not run as-is.
# You are expected to implement the create_block() function yourself
# and may need to modify other parts of the code

import bpy
import math
import os
from mathutils import Vector

def append_obj_from_blend(blend_path, obj_name):
    # Ensure the .blend path is absolute 
    blend_path = os.path.abspath(blend_path)
    
    # Append the object
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if obj_name not in data_from.objects:
            raise ValueError(f"Object '{obj_name}' not found in {blend_path}. Found: {data_from.objects}")
        
        data_to.objects = [obj_name]
    
    obj = data_to.objects[0]
    bpy.context.collection.objects.link(obj)
    return obj



def clear_scene():
    """Clears the scene."""
    # Make sure we are in Object Mode so we can select things
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select everything and delete
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Run it
clear_scene()

def get_material(name, color):
    """Returns a material, creating it if needed."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    # Create new material
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    # Assign color to the 'Principled BSDF' node
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = color
    return mat

def create_block(name, x, y, z, sx, sy, sz, color):
    """Spawns a cube centered at (x,y,z) with dimensions (sx,sy,sz) with color."""
    # TODO: Use the code you tested in the Console to assemble this function yourself.

    # Make sure the cube's location and scale are properly set. 
    # Make sure the material is named "Mat_" + name, where `name` is the first parameter of the function. 
    # The material color should match the `color` parameter.
    # Assign the material to the object using obj.data.materials.append(mat).
    
    # material:
    mat_name = f"Mat_{name}"
    mat = get_material(mat_name, color)
    
    # Create cube at location:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = name 
    
    # scale so dimensions become (sx, sy, sz)
    obj.scale = (sx / 2, sy / 2, sz / 2)
    
    # assign material:
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return obj

def generate_room(width=10, depth=10):
    """Generates floor and walls."""
    # 1. The floor (with checkerboard pattern)
    for i in range(width):
        for j in range(depth):
            # Alternating colors
            if (i+j) % 2 == 0:
                color = (0.8, 0.8, 0.8, 1) # Off-white
            else:
                color = (0.2, 0.2, 0.2, 1) # Dark-grey
            
            # Create tile slightly below z=0
            create_block(f"Floor_{i}_{j}", i, j, -0.05, 1, 1, 0.1, color)
            
    # 2. The walls
    wall_color = (0.9, 0.9, 0.8, 1) # Off-white
    wall_thick = 0.2
    wall_height = 3.3
    
    # Center points
    center_x = width / 2 - 0.5
    center_y = depth / 2 - 0.5
    
    # Back wall
    create_block("Wall_Back", center_x, depth - 0.5 + wall_thick/2, wall_height/2, width, wall_thick, wall_height, wall_color)
    # Left wall
    create_block("Wall_Left", -0.5 - wall_thick/2, center_y + wall_thick/2, wall_height/2, wall_thick, depth + wall_thick, wall_height, wall_color)
    # Right wall
    create_block("Wall_Right", width - 0.5 + wall_thick/2, center_y + wall_thick/2, wall_height/2, wall_thick, depth+wall_thick, wall_height, wall_color)

# Generate the room
generate_room()

def create_chair(x, y, rotation_deg=0):
    """Creates a chair at (x,y)."""
    
    # 1. Create a root object, which will be the parent of all chair parts 
    bpy.ops.object.empty_add(location=(x, y, 0))
    root = bpy.context.active_object
    root.name = f"Chair_Root_{x}_{y}"
    
    # 2. Colors 
    seat_color = (0.6, 0.2, 0.2, 1) # Red
    leg_color = (0.4, 0.2, 0.0, 1)  # Brown
    
    # 3. Dimensions
    leg_h, leg_w = 0.55, 0.08
    seat_w, seat_th = 0.60, 0.08
    back_h = 0.55
    
    # List to hold parts for parenting
    parts = []
    
    # 4. Create parts (legs, seat, backrest)
    off = (seat_w / 2) - (leg_w / 2)
    leg_z = leg_h / 2
    
    # Legs
    parts.append(create_block("Leg_FL", x-off, y-off, leg_z, leg_w, leg_w, leg_h, leg_color))
    parts.append(create_block("Leg_FR", x+off, y-off, leg_z, leg_w, leg_w, leg_h, leg_color))
    parts.append(create_block("Leg_BL", x-off, y+off, leg_z, leg_w, leg_w, leg_h, leg_color))
    parts.append(create_block("Leg_BR", x+off, y+off, leg_z, leg_w, leg_w, leg_h, leg_color))
    
    # Seat
    seat_z = leg_h + (seat_th / 2)
    parts.append(create_block("Seat", x, y, seat_z, seat_w, seat_w, seat_th, seat_color))
    
    # Backrest
    back_y = y + (seat_w/2) - (seat_th/2)
    back_z = leg_h + seat_th + (back_h/2)
    parts.append(create_block("Back", x, back_y, back_z, seat_w, seat_th, back_h, seat_color))
    
    # 5. Parenting
    for part in parts:
        part.parent = root
        # This is important for hierarchy to work.
        # TODO: Try commenting out this line and see what happens.
        part.matrix_parent_inverse = root.matrix_world.inverted()
        
    # 6. Rotate the root
    # This rotates the whole chair around its local Z axis (its vertical center).
    root.rotation_euler[2] = math.radians(rotation_deg)

# Center of the room (approx 4.5, 4.5 based on 10x10 grid)
cx, cy = 4.5, 4.5
# Create two chairs facing each other
create_chair(cx, cy + 1.5, rotation_deg=0)
create_chair(cx, cy - 1.5, rotation_deg=180)

# Using the manually created blend objects 
MANUAL_BLEND = r"/Users/kelony/Desktop/Compilers_&_VR_Tech/HW1/hw1_manual_ki120.blend"
print("exists?", os.path.exists(MANUAL_BLEND))

chair = append_obj_from_blend(MANUAL_BLEND, "Chair")
table = append_obj_from_blend(MANUAL_BLEND, "Table")


chair.location = (4.5, 4.5, 0.90)
table.location = (4.5, 3.2, 0.90)