import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import PropertyGroup

class ComfyUIBridgeProperties(PropertyGroup):
    """ComfyUI桥接插件的属性"""
    
    # ComfyUI服务器设置
    server_url: StringProperty(
        name="服务器地址",
        description="ComfyUI服务器地址（例如：http://127.0.0.1:8188）",
        default="http://127.0.0.1:8188",
    )
    
    # 连接状态
    is_connected: BoolProperty(
        name="已连接",
        description="是否已连接到ComfyUI服务器",
        default=False,
    )
    
    # 图像发送设置
    send_on_render: BoolProperty(
        name="渲染时自动发送",
        description="渲染摄像机视图时自动发送到ComfyUI",
        default=False,
    )
    
    # 图像质量设置
    image_quality: IntProperty(
        name="图像质量",
        description="发送图像的质量（1-100）",
        default=95,
        min=1,
        max=100,
    )
    
    # 节点ID（用于ComfyUI端识别）
    node_id: StringProperty(
        name="节点ID",
        description="ComfyUI中Blender Camera Input节点的ID",
        default="",
    )

def register():
    bpy.utils.register_class(ComfyUIBridgeProperties)
    bpy.types.Scene.comfyui_bridge = bpy.props.PointerProperty(type=ComfyUIBridgeProperties)

def unregister():
    del bpy.types.Scene.comfyui_bridge
    bpy.utils.unregister_class(ComfyUIBridgeProperties)

