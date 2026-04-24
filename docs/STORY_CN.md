# 项目故事

## 推文的承诺

2026年4月22日，[Zain Shah](https://x.com/zan2434/status/2046983256093163948) 在X上展示了一个名为Flipbook的原型：

> 想象你屏幕上的每一个像素，都直接从模型实时流式传输。没有HTML，没有布局引擎，没有代码。就是你想要看到的内容。

然后在线程中：

> 为了让图像生动起来，我们深度优化了 @LTXStudio 的视频模型。足以直接在屏幕上流式传输1080p@24fps的实时视频，通过WebSocket直连 @modal_labs 的无服务器GPU基础设施。

这营造了一个心理预期：**一个浏览器，页面本身就是实时视频流。** 每一帧都由神经网络绘制。你点击某个区域，视频就会变形为其他内容。没有DOM。没有按钮。只有像素。

这是一个值得追求的理念。如果成真，你终于可以摆脱自NCSA Mosaic以来一直困扰我们的"文本墙和彩色矩形"UI。

## Flipbook的实际面貌

我们打开了 [flipbook.page](https://flipbook.page) 并通过Playwright + 包检查进行了分析（启动这个仓库的浏览器实验室会话）。

现实更加朴素：

- **每个"页面"都是静态图像。** 一个 `<img src="data:image/jpeg;base64,…">` 标签持有整个UI。图像是约1376×768的JPEG，按需生成。
- **页面内的文本由图像模型绘制为像素。** 没有DOM文本覆盖。偶尔会渲染错误（"HANDLEEBRS"、"speds speeds"）。这是图像模型的特性，不是bug——推文确实说了"没有HTML"。
- **点击驱动探索。** 你在图像上任意位置点击，视觉语言模型将该点解析为主题，主题成为下一个查询，生成新图像。
- **"实时1080p@24fps视频流"** 是一个**每页面切换开关**，不是默认选项。默认关闭，因为资源消耗大。他们的网站说："你可以根据需要打开或关闭的切换开关。"

所以推文标题（"每个像素都实时流式传输"）是理想化的——它描述的是视频切换功能，而不是日常浏览体验。让Flipbook真正有趣的不是视频：而是**图像即UI**的理念加上通过视觉模型**点击导航**。

## 内部工作原理

从生产环境反向工程得出：

### 页面生成 — Server-Sent Events

```
POST /api/iteratively-generate-next-page
Body: {
  query: "蒸汽机是如何工作的",
  aspect_ratio: "16:9",
  web_search: true,
  session_id: "session_<uuid>",
  current_node_id: "",
  mode: "tap|edit",
  image: "<data url>",           // 点击时
  parent_query, parent_title,
}
```

响应是一个SSE流。一个观察到的请求在约19秒内返回了约7.7 MB——模型细化图像时的渐进式JPEG块。

最终帧是最终渲染的内容。在它到达后，浏览器将整个payload（包括完整的base64图像）POST到 `/api/nodes`，保存后返回一个 `id`。URL变为 `/n/<id>`。

包中看到的内部代号：**"Sketchapedia"**。

### 实时视频 — 自定义WebSocket协议

切换开关打开一个WebSocket到：

```
wss://tmalive--ltx-stream-diffusersltx2streamingengine-streaming-app.modal.run/ws/stream
```

这告诉你了很多信息，无需任何文档：

- Modal工作区：`tmalive`（Zain的）。
- Modal应用：`ltx-stream`。
- GPU类：`DiffusersLtx2StreamingEngine` — 一个自定义的 [Diffusers](https://huggingface.co/docs/diffusers) 管道，包装了Lightricks的LTX-2模型，直接通过WS暴露。

客户端→服务器开启帧（JSON）：

```json
{ "action": "start",
  "session_id": "ltx_stream_<uuid>",
  "prompt": "<page_title>",
  "width": 1920, "height": 1088,
  "num_frames": 49, "frame_rate": 24,
  "max_segments": 9999,
  "loopy_mode": true,
  "loopy_strategy": "anchor_loop",
  "start_image": "<data url>",
  "target_image": "<data url>",
  "position": 0 }
```

`anchor_loop` 策略是他们如何在页面之间混合的方式：每个页面是一个"锚帧"，模型生成一个动画片段，可以无缝循环回到它。

服务器→客户端帧使用我们称为 **LTXF** 的自定义二进制格式：

```
[0..3]   ASCII "LTXF"
[4..7]   uint32大端序头部长度n
[8..8+n] UTF-8 JSON头部 {media_type, sequence, is_init_segment?, final?}
[剩余]   fMP4片段字节（moov/trak用于初始化，moof/mdat用于媒体）
```

浏览器从 `moov` 解析ISOBMFF盒子，选择编解码器（观察到：`avc1.640028` — H.264 High @ L4.0），打开 `MediaSource`，在 `sequence` 模式下创建 `SourceBuffer`，并附加每个payload。这就是像素如何在不触碰普通视频URL的情况下出现在 `<video>` 标签上的。

如果浏览器缺乏MSE，他们会降级到 `degraded_to_image` — 静态JPEG。

### 持久化

- JPEG存储在R2中。URL看起来像 `/api/image-proxy?…`，但底层存储桶是S3兼容的。
- 会话图通过 `parent_id` + `session_id` 引用。
- `/n/:id` 永久链接从保存的图像重新生成，重新加载时不会重新生成任何内容。

## 这个仓库的不同之处

Endless Canvas复制了这个范式和有线协议，但在原始版本封闭的地方做出了不同选择：

- **自带密钥**。不是托管服务，而是克隆仓库并插入你自己的fal + OpenRouter + Modal + R2 + Mongo。维护者没有按用户计费。
- **两条动画路径**，不是一条：
  - 默认：调用 `fal-ai/ltx-video/image-to-video` 获取5秒MP4，约$0.02。不需要GPU基础设施。诚实标记为"动画（5秒片段）"——不是"流式"。
  - 流式路径：实现了LTXF WebSocket协议，所以你可以在你自己的Modal账户上部署 `ltx_stream.py` 并获得真正的流式传输。当 `NEXT_PUBLIC_LTX_WS_URL` 设置时UI会切换。
- **通过OpenRouter的Qwen而不是封闭LLM。** `qwen/qwen-2.5-vl-72b-instruct` 用于点击解析，`qwen/qwen-2.5-72b-instruct:online` 用于带网络搜索的页面规划。便宜、开放权重、可替换。
- **种子图像上传。** 拖放任何图像到 `/play`（或点击"上传"）。它成为起始页面；区域点击通过相同的VLM → 规划器管道。
- **可见的状态UX。** SSE流在"规划"、"绘制"等之间发出 `status` 事件。我们将它们作为图像上的覆盖层显示，这样你可以实时看到VLM解析你的点击，而不是盯着死图像15秒。
- **完整Docker compose栈。** `docker compose up` 在一个命令中启动Mongo + Python后端 + Next.js，准备好用于新笔记本克隆。

## 推文哪里对了，哪里过于理想化

**对的：**
- 图像即UI理念。看着文本作为像素渲染确实奇怪而新颖，错字也不例外。
- 点击探索比菜单更自然，用于"我想了解插图中这个特定事物的更多信息。"
- LTX-Video在Modal GPU上运行，带有自定义管道是真实的，WS协议有效。

**过于理想化：**
- "每个像素都从模型实时流式传输"描述的是演示卷轴，而不是默认体验。
- "没有HTML，没有布局引擎"对页面内容是正确的。外部框架（搜索栏、分享按钮、FAQ）是普通React。
- 视频切换慢、昂贵，且默认关闭。

## 为什么我们仍然构建它

即使透过包装，底层洞察——足够好的图像模型可以替代UI工具包——值得尝试。如果你眯起眼睛看，这就是"视觉解释器"、"交互式维基百科"、"下一代教科书"相遇的地方。工具（VLM点击解析、渐进式图像SSE、MSE fMP4流式）现在都已商品化；Flipbook封闭的唯一原因是产品策略，不是技术壁垒。

这个仓库消除了那个原因。
