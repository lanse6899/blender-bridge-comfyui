import bpy
from bpy.types import Panel

class COMFYUI_PT_MainPanel(Panel):
    """ComfyUI桥接主面板"""
    bl_label = "ComfyUI Bridge"
    bl_idname = "COMFYUI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"
    
    def draw(self, context):
        layout = self.layout
        
        # 先显示一个测试标签，确保面板能正常绘制
        layout.label(text="ComfyUI Bridge 插件")
        layout.separator()
        
        # 检查属性是否存在
        try:
            props = context.scene.comfyui_bridge
        except AttributeError:
            layout.label(text="错误: 插件属性未初始化", icon='ERROR')
            layout.label(text="请禁用并重新启用插件")
            return
        
        # 服务器设置
        box = layout.box()
        box.label(text="服务器设置")
        box.prop(props, "server_url")
        
        # 连接状态
        row = box.row()
        if props.is_connected:
            row.label(text="状态: 已连接", icon='CHECKMARK')
            row.operator("comfyui.disconnect", text="断开")
        else:
            row.label(text="状态: 未连接", icon='X')
            row.operator("comfyui.connect", text="连接")
        
        layout.separator()
        
        # 摄像机设置
        box = layout.box()
        box.label(text="摄像机", icon='CAMERA_DATA')
        
        scene = context.scene
        if scene.camera:
            box.label(text=f"活动摄像机: {scene.camera.name}")
        else:
            box.label(text="无活动摄像机", icon='ERROR')
        
        layout.separator()
        
        # 发送控制
        box = layout.box()
        box.label(text="发送图像")
        box.prop(props, "send_on_render")
        box.prop(props, "image_quality")
        
        row = box.row()
        row.scale_y = 1.5
        op = row.operator("comfyui.send_camera_view", text="发送摄像机视图")
        if hasattr(op, 'enabled'):
            op.enabled = props.is_connected and scene.camera is not None
        
        layout.separator()
        
        # 节点设置
        box = layout.box()
        box.label(text="节点设置", icon='NODETREE')
        box.prop(props, "node_id")
        box.label(text="在ComfyUI中创建Blender Camera Input节点", icon='INFO')
        box.label(text="并将节点ID填入上方")

def register():
    bpy.utils.register_class(COMFYUI_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(COMFYUI_PT_MainPanel)

