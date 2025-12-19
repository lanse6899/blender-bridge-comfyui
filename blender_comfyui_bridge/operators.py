import bpy
import bpy.utils.previews
import requests
import json
import base64
import io
from bpy.types import Operator
from bpy.props import StringProperty

class COMFYUI_OT_Connect(Operator):
    """连接到ComfyUI服务器"""
    bl_idname = "comfyui.connect"
    bl_label = "连接服务器"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_bridge
        try:
            # 测试连接
            response = requests.get(f"{props.server_url}/system_stats", timeout=5)
            if response.status_code == 200:
                props.is_connected = True
                self.report({'INFO'}, f"成功连接到 {props.server_url}")
                return {'FINISHED'}
            else:
                props.is_connected = False
                self.report({'ERROR'}, "连接失败：服务器响应异常")
                return {'CANCELLED'}
        except Exception as e:
            props.is_connected = False
            self.report({'ERROR'}, f"连接失败：{str(e)}")
            return {'CANCELLED'}

class COMFYUI_OT_Disconnect(Operator):
    """断开ComfyUI服务器连接"""
    bl_idname = "comfyui.disconnect"
    bl_label = "断开连接"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_bridge
        props.is_connected = False
        self.report({'INFO'}, "已断开连接")
        return {'FINISHED'}

class COMFYUI_OT_SendCameraView(Operator):
    """发送当前摄像机视图到ComfyUI"""
    bl_idname = "comfyui.send_camera_view"
    bl_label = "发送摄像机视图"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_bridge
        
        if not props.is_connected:
            self.report({'ERROR'}, "请先连接到ComfyUI服务器")
            return {'CANCELLED'}
        
        # 获取活动摄像机
        scene = context.scene
        if not scene.camera:
            self.report({'ERROR'}, "场景中没有摄像机")
            return {'CANCELLED'}
        
        # 渲染摄像机视图
        try:
            # 保存当前渲染设置
            old_engine = scene.render.engine
            old_resolution_x = scene.render.resolution_x
            old_resolution_y = scene.render.resolution_y
            old_file_format = scene.render.image_settings.file_format
            
            # 使用当前渲染尺寸和相机宽高比，不再强制改成方图
            scene.render.image_settings.file_format = 'PNG'
            
            # 渲染图像到内存
            bpy.ops.render.render(write_still=False)
            render_image = bpy.data.images['Render Result']
            
            # 将图像转换为PNG字节
            # 使用临时文件路径
            import tempfile
            import os
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "blender_comfyui_temp.png")
            
            # 保存为临时文件
            render_image.save_render(filepath=temp_file)
            
            # 读取图像数据
            with open(temp_file, 'rb') as f:
                image_data = f.read()
            
            # 清理临时文件
            try:
                os.remove(temp_file)
            except:
                pass
            
            # 转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 恢复渲染设置
            scene.render.engine = old_engine
            scene.render.resolution_x = old_resolution_x
            scene.render.resolution_y = old_resolution_y
            scene.render.image_settings.file_format = old_file_format
            
            # 发送到ComfyUI
            success, msg = self._send_to_comfyui(context, image_base64, image_data)
            
            if success:
                self.report({'INFO'}, "图像已发送到ComfyUI")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"发送失败：{msg}")
                return {'CANCELLED'}
            
        except Exception as e:
            import traceback
            self.report({'ERROR'}, f"发送失败：{str(e)}")
            print(traceback.format_exc())
            return {'CANCELLED'}
    
    def _send_to_comfyui(self, context, image_base64, image_data):
        """发送图像到ComfyUI"""
        props = context.scene.comfyui_bridge
        
        # 直接发送到自定义节点（推荐方式）
        ok, msg = self._send_to_custom_node(context, image_base64)
        if not ok:
            return False, msg
        
        # 可选：同时尝试通过ComfyUI的API上传图像
        try:
            files = {
                'image': ('blender_camera.png', image_data, 'image/png')
            }
            response = requests.post(
                f"{props.server_url}/upload/image",
                files=files,
                timeout=10
            )
            
            if response.status_code == 200:
                upload_data = response.json()
                image_path = upload_data.get('name', '')
                # 通知ComfyUI节点更新（如果支持）
                self._notify_comfyui_node(context, image_path)
        except:
            pass  # 如果上传API不存在，忽略错误
        
        return True, "sent"
    
    def _notify_comfyui_node(self, context, image_path):
        """通知ComfyUI节点更新图像路径"""
        props = context.scene.comfyui_bridge
        
        if not props.node_id:
            return
        
        data = {
            "node_id": props.node_id,
            "image_path": image_path
        }
        
        try:
            response = requests.post(
                f"{props.server_url}/blender/update_image",
                json=data,
                timeout=5
            )
        except:
            pass  # 如果API不存在，忽略错误
    
    def _send_to_custom_node(self, context, image_base64):
        """直接发送图像数据到自定义节点"""
        props = context.scene.comfyui_bridge
        
        if not props.node_id:
            return False, "未设置节点ID"
        
        data = {
            "node_id": props.node_id,
            "image_data": image_base64,
            "format": "png"
        }
        
        try:
            response = requests.post(
                f"{props.server_url}/blender/receive_image",
                json=data,
                timeout=10
            )
            if response.status_code != 200:
                print(f"[ComfyUI Bridge] POST /blender/receive_image status={response.status_code} resp={response.text}")
                return False, f"HTTP {response.status_code}"
            return True, "ok"
        except Exception as e:
            print(f"[ComfyUI Bridge] 发送到自定义节点失败：{str(e)}")
            return False, str(e)

def register():
    bpy.utils.register_class(COMFYUI_OT_Connect)
    bpy.utils.register_class(COMFYUI_OT_Disconnect)
    bpy.utils.register_class(COMFYUI_OT_SendCameraView)

def unregister():
    bpy.utils.unregister_class(COMFYUI_OT_SendCameraView)
    bpy.utils.unregister_class(COMFYUI_OT_Disconnect)
    bpy.utils.unregister_class(COMFYUI_OT_Connect)

