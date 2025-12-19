"""
ComfyUI Blender Bridge - 自定义节点
接收来自Blender的摄像机视图图像
"""

from .nodes import BlenderCameraInputNode, register_api_routes

# 注册API路由
try:
    register_api_routes()
except:
    pass  # 如果PromptServer还未初始化，会在节点加载时重试

NODE_CLASS_MAPPINGS = {
    "BlenderCameraInput": BlenderCameraInputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderCameraInput": "🔵BB blender图像加载"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

