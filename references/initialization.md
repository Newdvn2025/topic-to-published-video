# 首次初始化：先选择，再安装

## 用户选择

检查已有工具后，询问：推荐组合（AutoDL+HyperFrames）、全部安装（追加Remotion+ChatCut）、自选。用户已经明确选择时不重复问。推荐组合用于B-roll成本控制和本地包装，不承诺固定单价或始终比其他服务便宜。

AutoDL与HyperFrames推荐基础安装，Remotion适合React制作，ChatCut适合可视化编辑。缺推荐工具也可用现有素材或交付计划。安装选择不授权付费生成。

## 交互与代理执行

需要Python 3.10+，在本技能目录运行：

```bash
python3 scripts/setup.py
```

选择后显示范围再确认。默认项目级Codex安装；其他宿主可用--agent claude-code或cursor，但ChatCut连接包仅支持Codex。用户在对话中已明确选择，代理可直接执行：

```bash
python3 scripts/setup.py --profile recommended --yes --workspace ./my-video
python3 scripts/setup.py --profile all --yes --workspace ./my-video
python3 scripts/setup.py --select autodl,hyperframes,remotion --yes --workspace ./my-video
```

加--dry-run只展示计划；加--global选择用户级安装。自定义CODEX_HOME时使用项目安装或由代理按实际目录安装，第三方安装器不保证遵循CODEX_HOME。

AutoDL从本包复制。HyperFrames核心技能、Remotion官方技能和ChatCut官方连接技能通过npx skills安装，需要Node/npm、网络与Git；HyperFrames要求Node.js22+。命令源见config/dependencies.json。已有同名技能不会自动覆盖：AutoDL保留并标待检查，--replace显式备份替换；远程组合若已有部分技能，由代理核对并只补缺失项。

脚本记录项目.video-workflow/setup-state.json，只安装技能，不自动安装系统运行时、不改MCP配置、不登录、不生成视频。失败如实记录。新技能可能需要宿主重新加载。

## AutoDL Key配置

用AutoDL Art ComfyUI工作流的API Token，不是GPU实例SSH密码或其他服务Key。[AutoDL Art入口](https://autodl.art)。账号界面以当前服务显示为准。

方案A：设置环境变量AUTODL_ART_TOKEN，重新打开代理以继承环境；环境变量优先。

方案B：本地终端隐藏输入，推荐：

```bash
python3 scripts/setup.py key
```

输入不会回显，文件不在项目仓库：

- macOS/Linux：~/.config/topic-to-published-video/autodl.env；如设置XDG_CONFIG_HOME则用该目录。
- Windows：%APPDATA%/topic-to-published-video/autodl.env。

Unix权限0600；Windows采用用户目录系统权限。不要在聊天、命令参数、manifest或公开仓库中放Key。也可复制config/autodl.env.example到该位置，在本地编辑器填写。自定义文件用生成脚本--env-file指定。不要同时维护两份不同Key。

## 检查和调用

```bash
python3 scripts/setup.py doctor
python3 addons/autodl-broll/scripts/autodl_broll.py addons/autodl-broll/references/manifest_example.json --prepare-only --output-dir ./requests-preview
```

doctor仅检查工具/凭据是否存在，不证明账户认证或余额。prepare-only校验与准备请求体，不联网生成。用户批准具体生成计划后去掉prepare-only，保留输出目录续接任务，不重复提交已有task_id。失败追加生成需要对应预算授权。

API的Authorization使用原始Token、不加Bearer。各工作流resolution枚举独立；当前文本工作流默认768p横不保证精确16:9，下载后实测并派生。

## 编辑工具的后续步骤

- HyperFrames：检查Node.js22+、FFmpeg和浏览器渲染环境；创建项目时安装项目依赖并运行doctor。见[官方仓库](https://github.com/heygen-com/hyperframes)。
- Remotion：技能安装后，创建视频项目时再按官方技能初始化React/Remotion依赖并检查预览/渲染。见[官方技能](https://github.com/remotion-dev/skills)。
- ChatCut：加载安装后的connect-chatcut-desktop，检测平台、按官方说明安装签名应用、打开并连接；应用同步编辑技能，用户完成登录。已有chatcut_desktop工具时复用，不重装。当前桌面支持macOS/Windows，Linux应报告不支持。见[官方连接包](https://github.com/ChatCut-Inc/agent-plugin/tree/main/chatcut-desktop-codex-plugin)。

ChatCut安装器只准备连接技能，应用安装由代理按该技能完成；不可用时给官方安装步骤，不能把技能已安装报告成应用已连接。桌面版不改用hosted MCP；用户明确选择网页版时另按官方对应流程。

## 初始化验收

分别记录skills_installed、runtime_ready、credential_configured、authenticated（适用时），并列出缺口。只有所选能力可用或用户明确跳过余项时才记录initialization_complete及限制。已有初始化复用选择，后续只补缺口。

安装器依据[skills官方说明](https://github.com/vercel-labs/skills)。来源核对：2026-10-07。上游更新时以官方内容为准，缺失或更名不能盲目转第三方镜像。
