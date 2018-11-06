
bl_info = {
    "name": "Import Sub Rosa .cmo",
    "author": "jnz",
    "version": (1, 0, 0),
    "blender": (2, 76, 1),
    "location": "File > Import-Export",
    "description": "",
    "warning": "",
    "category": "Import-Export"
}

tex_table = {
    "(default)": "tex_1.png",
    "ak47": "gun_tex.png",
    "m16": "gun_tex.png",
    "mp5": "gun_tex.png",
    #"9mm": "gun_tex.png",
    "9mm": None,
    "ak47_magazine": "gun_tex.png",
    "m16_magazine": "gun_tex.png",
    "mp5_magazine": "gun_tex.png",
    #"9mm_magazine": "gun_tex.png",
    "9mm_magazine": None,
    "mhead1": "face_tex.png",
    "mhead2": "face_tex.png",
    "mhead3": "face_tex.png",
    "mhead4": "face_tex.png",
    "mhead5": "face_tex.png",
    "fhead1": "face_tex.png",
    "fhead2": "face_tex.png",
    "fhead3": "face_tex.png",
    "fhead4": "face_tex.png",
    "fhead5": "face_tex.png",
    "cellphone": "tex_2.png",
    "grenade": "grenade.png",
    "soccerball": "soccerball.png",
}


import math
import struct

if "bpy" in locals():
    import importlib
    if "stl_utils" in locals():
        importlib.reload(stl_utils)
    if "blender_utils" in locals():
        importlib.reload(blender_utils)

import os

import bpy
from bpy.props import (
        StringProperty,
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        axis_conversion,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )
import bmesh
import mathutils


def readInt(f):
  return struct.unpack('i', f.read(4))[0]

def readFloat(f):
  return struct.unpack('f', f.read(4))[0]

def writeInt(f, n):
  f.write(struct.pack("i", n))

def writeFloat(f, n):
  f.write(struct.pack("f", n))


def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    #return None
    return [0.0, 0.0]






class importCMO(Operator, ImportHelper):
  """Load CMO mesh data"""
  bl_idname = "import_mesh.cmo"
  bl_label = "Import CMO"
  bl_options = {'UNDO'}
  filename_ext = ".cmo"
  
  filter_glob = StringProperty(
          default="*.cmo",
          options={'HIDDEN'},
          )
  filepath = StringProperty(
          subtype='FILE_PATH',
          )
  directory = StringProperty(
          subtype='DIR_PATH',
          )
  global_scale = FloatProperty(
          name="Scale",
          soft_min=0.001, soft_max=1000.0,
          min=1e-6, max=1e6,
          default=10.0,
          )
  shadeless = BoolProperty(
          name="Unshaded material",
          default=True,
          )
  
  def execute(self, context):
    cmo_name = bpy.path.display_name_from_filepath(self.filepath)
    f = open(self.filepath, 'rb')
    readInt(f) #CMod
    version = readInt(f)
    
    #=== vertices ===
    
    verts = []
    verts_uv = []
    vertices_n = readInt(f)
    #print("vertices:")
    #print(vertices_n)
    for i in range(vertices_n):
      if version == 3:
        verts.append([readFloat(f),readFloat(f),readFloat(f)])
        verts_uv.append([readFloat(f),readFloat(f)])
        readFloat(f)
      elif version < 3:
        verts.append([readFloat(f),readFloat(f),readFloat(f)])
        verts_uv.append([0.0, 0.0])
        readInt(f)
    
    #==== faces ====
    
    triangles = []
    triangle_mat = []
    triangles_n = readInt(f)
    #print("tris:")
    #print(triangles_n)
    for i in range(triangles_n):
      t = []
      for i2 in range(readInt(f)):
        t.append(readInt(f))
      if(version > 1):
        readInt(f)
      triangle_mat.append(readInt(f))
      triangles.append(t)
    
    
    mesh = bpy.data.meshes.new(cmo_name)
    mesh.from_pydata(verts, [], triangles)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    #=== texture coordinates ===
    
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()
    for t in bm.faces:
      t.material_index = triangle_mat[t.index]
      for l in t.loops:
        luv = l[uv_layer]
        luv.uv = verts_uv[l.vert.index]
    
    
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    mesh.update()
    mesh.validate()
    
    #==== material ====
    
    tex_file = tex_table[ ["(default)", cmo_name][(cmo_name in tex_table)] ]
    if tex_file and (version >= 3):
      material = bpy.data.materials.new(cmo_name)
      material.use_shadeless = self.shadeless
      mesh.materials.append(material)
      texture = bpy.data.textures.new('MP', 'IMAGE')
      texture.image = bpy.data.images.load(os.path.dirname(self.filepath)+"\\"+tex_file, check_existing=True)
      mtex = material.texture_slots.add()
      mtex.texture = texture
      mtex.texture_coords = 'UV'
      mtex.use_map_color_diffuse = True
    
    #=== object creation ===
    
    scn = bpy.context.scene
    obj = bpy.data.objects.new(cmo_name, mesh)
    obj.scale *= self.global_scale
    obj.rotation_euler = [math.pi*0.5, 0.0, 0.0]
    scn.objects.link(obj)
    scn.objects.active = obj
    obj.select = True
    
    f.close()
    print('\nSuccessfully imported %r' % (self.filepath))
    return {'FINISHED'}











class exportCMO(Operator, ExportHelper):
  """Load CMO mesh data"""
  bl_idname = "export_mesh.cmo"
  bl_label = "Export CMO"
  bl_options = {'PRESET'}
  filename_ext = ".cmo"
  
  filter_glob = StringProperty(
          default="*.cmo",
          options={'HIDDEN'},
          )
  filepath = StringProperty(
          subtype='FILE_PATH',
          )
  directory = StringProperty(
          subtype='DIR_PATH',
          )
  global_scale = FloatProperty(
          name="Scale",
          soft_min=0.001, soft_max=1000.0,
          min=1e-6, max=1e6,
          default=0.1,
          )
  global_coords = BoolProperty(
          name="Use global coordinates",
          description="As opposed to local (object space) vertex positions",
          default=True,
          )
  use_selection = BoolProperty(
          name="Selection Only",
          description="Export selected objects only",
          default=False,
          )
  
  def execute(self, context):
    f = open(self.filepath, 'wb')
    writeInt(f, 1685015875) #CMod
    writeInt(f, 3) #version
    
    scene = context.scene
    scene.update()
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    
    if self.use_selection:
        objects = context.selected_objects
    else:
        objects = scene.objects
    
    for obj in objects:
      if(obj.type == "MESH"):
        mat_world = obj.matrix_world
        #mat_world_inv = mat_world.inverted()
        
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
        
        #uv_layer = bm.loops.layers.uv.active
        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()
        
        writeInt(f, len(bm.verts))
        for v in bm.verts:
          uv = uv_from_vert_first(uv_layer, v)
          vp = v.co
          if self.global_coords:
            vp0 = (mat_world * vp)
            vp = mathutils.Vector((vp0.x, vp0.z, -vp0.y))
          vp *= self.global_scale
          writeFloat(f, vp.x)
          writeFloat(f, vp.y)
          writeFloat(f, vp.z)
          writeFloat(f, uv[0])
          writeFloat(f, uv[1])
          writeFloat(f, 0.0)
        
        
        writeInt(f, len(bm.faces))
        for t in bm.faces:
          writeInt(f, 3)
          writeInt(f, t.verts[0].index)
          writeInt(f, t.verts[1].index)
          writeInt(f, t.verts[2].index)
          writeInt(f, 0)
          writeInt(f, t.material_index)
    
    
    f.close()
    print('\nSuccessfully exported %r' % (self.filepath))
    return {'FINISHED'}










def menu_import(self, context):
    self.layout.operator(importCMO.bl_idname, text="Sub Rosa (.cmo)")

def menu_export(self, context):
    self.layout.operator(exportCMO.bl_idname, text="Sub Rosa (.cmo)")

def register():
    bpy.utils.register_class(importCMO)
    bpy.utils.register_class(exportCMO)
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)

def unregister():
    bpy.utils.unregister_class(importCMO)
    bpy.utils.unregister_class(exportCMO)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
  register()
