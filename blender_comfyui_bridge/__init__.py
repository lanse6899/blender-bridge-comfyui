bl_info = {
    "name": "Blender ComfyUI Bridge",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),  # 最低版本要求：Blender 3.0，支持更高版本（3.6, 4.0, 4.1等）
    "location": "View3D > Sidebar > ComfyUI",
    "description": "将Blender摄像机视图发送到ComfyUI",
    "category": "Render",
}

import bpy
from . import operators
from . import panels
from . import properties

def register():
    properties.register()
    operators.register()
    panels.register()

def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()

