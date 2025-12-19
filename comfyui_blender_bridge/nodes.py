import torch
import numpy as np
from PIL import Image
import io
import base64
import json
import folder_paths
from datetime import datetime

# 全局存储：按node_id存储接收到的图像
_blender_images = {}

def register_api_routes():
    """注册API路由以接收Blender图像（只注册一次）"""
    try:
        from server import PromptServer
        from aiohttp import web

        @PromptServer.instance.routes.post("/blender/receive_image")
        async def receive_image(request):
            try:
                data = await request.json()
                node_id = data.get("node_id")
                image_data = data.get("image_data")
                image_format = data.get("format", "png")

                if not node_id or not image_data:
                    return web.json_response({"error": "缺少必要参数"}, status=400)

                # 解码base64图像
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

                # 转换为RGB格式
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # 存储图像（按node_id）
                _blender_images[node_id] = image

                print(f"[Blender Bridge] receive_image node_id={node_id} size={image.size} ts={datetime.now().isoformat(timespec='seconds')}")

                return web.json_response({
                    "status": "success",
                    "message": f"图像已接收（节点ID: {node_id}）"
                })

            except Exception as e:
                print(f"[Blender Bridge] receive_image error: {e}")
                return web.json_response({
                    "error": str(e)
                }, status=500)

        @PromptServer.instance.routes.post("/blender/update_image")
        async def update_image(request):
            """通过图像路径更新（如果ComfyUI支持上传）"""
            try:
                data = await request.json()
                node_id = data.get("node_id")
                image_path = data.get("image_path")

                if not node_id or not image_path:
                    return web.json_response({"error": "缺少必要参数"}, status=400)

                # 从ComfyUI输入目录加载图像
                try:
                    full_path = folder_paths.get_annotated_filepath(image_path)
                    image = Image.open(full_path)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    _blender_images[node_id] = image
                    print(f"[Blender Bridge] update_image node_id={node_id} size={image.size} ts={datetime.now().isoformat(timespec='seconds')}")

                    return web.json_response({
                        "status": "success",
                        "message": f"图像已更新（节点ID: {node_id}）"
                    })
                except Exception as e:
                    print(f"[Blender Bridge] update_image load error: {e}")
                    return web.json_response({
                        "error": f"无法加载图像: {str(e)}"
                    }, status=400)

            except Exception as e:
                print(f"[Blender Bridge] update_image error: {e}")
                return web.json_response({
                    "error": str(e)
                }, status=500)
    except Exception as e:
        print(f"[Blender Bridge] 注册API路由失败: {str(e)}")

# 尝试注册API路由
try:
    register_api_routes()
except:
    pass  # 如果PromptServer还未初始化，稍后会在节点加载时重试

class BlenderCameraInputNode:
    """接收来自Blender的摄像机视图图像"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "节点唯一ID，用于接收Blender图像"
                }),
            },
            "optional": {
                "fallback_image": ("IMAGE", {
                    "tooltip": "如果未收到Blender图像，使用此图像"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "process"
    CATEGORY = "🔵BB blender"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        告诉ComfyUI：每次执行都视为“已变化”，不要使用缓存。
        这样同一个 node_id 多次接收图像也会重新计算。
        """
        return float("NaN")
    
    def __init__(self):
        # 确保API路由已注册
        try:
            register_api_routes()
        except:
            pass
    
    def process(self, node_id, fallback_image=None):
        """处理图像输入"""
        # 从全局存储中获取图像
        if node_id and node_id in _blender_images:
            image = _blender_images[node_id]
        elif fallback_image is not None:
            # 使用备用图像
            image = Image.fromarray(np.clip(fallback_image[0].cpu().numpy() * 255, 0, 255).astype(np.uint8))
        else:
            # 创建默认黑色图像
            image = Image.new('RGB', (512, 512), color='black')

        print(f"[Blender Bridge] process node_id={node_id} use_image_size={image.size} has_fallback={fallback_image is not None}")
        
        # 转换为numpy数组
        image_np = np.array(image).astype(np.float32) / 255.0
        
        # 转换为torch tensor并添加批次维度
        image_tensor = torch.from_numpy(image_np)[None,]
        
        return (image_tensor,)

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "BlenderCameraInput": BlenderCameraInputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderCameraInput": "🔵BB blender图像加载"
}

