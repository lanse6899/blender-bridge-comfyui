## Blender ComfyUI Bridge

将 Blender 摄像机视图直接发送到 ComfyUI 的小工具。

### 功能

- 在 Blender 中捕获当前摄像机画面  
- 通过 HTTP 发送到 ComfyUI  
- 在 ComfyUI 中用专用节点 `Blender Camera Input` 接收图像并接入任意工作流  

### 安装

**Blender 插件（推荐手动复制）**

1. 按 `Win + R` 输入 `%APPDATA%\Blender Foundation\Blender` 回车  
2. 进入你正在使用的 Blender 版本目录（例如 `3.6`、`4.0` 等）  
3. 依次进入 `scripts\addons\` 文件夹  
4. 将整个 `blender_comfyui_bridge` 文件夹复制到 `addons` 目录中  
5. 打开 Blender → `编辑` → `偏好设置` → `插件`  
6. 搜索 `Blender ComfyUI Bridge` 并勾选启用  

**ComfyUI 插件**

1. 将 `comfyui_blender_bridge` 文件夹复制到 `ComfyUI/custom_nodes/`
2. 重启 ComfyUI（重新打开网页）

### 使用

**在 ComfyUI 中**

1. 添加节点：`Add Node → blender → Blender Camera Input`
2. 记住并设置节点上的 `node_id`（例如：`1`），保持和 Blender 一致

**在 Blender 中**

1. 在 3D 视图右侧面板找到 `ComfyUI` 标签
2. 服务器地址填：`http://127.0.0.1:8188`（或你的 ComfyUI 地址），点击“连接”
3. 在“节点设置”中填入和 ComfyUI 节点相同的 `节点ID`
4. 点击“发送摄像机视图”，再到 ComfyUI 点击 `Queue Prompt` 执行工作流，即可在工作流中使用 Blender 的画面

### 使用与许可证

- 个人用户：**免费使用**，包括学习、创作和发布作品  
- 商用使用：平台方、公司、机构或团体如用于商业目的（含对外提供服务、内部生产项目等），**需事先联系作者获得授权**  
- 许可证：本项目采用 **MIT License**，你可以不可修改和分发本项目代码，但在再发布时需保留原始版权与许可声明
