---
name: autodl-broll
description: "通过AutoDL Art API生成、续接和下载B-roll视频；支持文字、参考图和首尾帧输入。用于用户已授权生成的视频素材任务。"
---
# AutoDL B-roll

先检查真实口播、素材缺口与用户预算，生成manifest。用户只要计划时不要提交。默认文字生成工作流minimax_h3_lightx2v_no_pic、4–5秒、768p横；动作演示可按用户要求延长。生成画幅可能非精确16:9，下载后实测并按项目要求派生，保留原片。

## 配置与执行

Python 3.10+，无第三方Python依赖。优先从环境变量AUTODL_ART_TOKEN读取，其次从用户配置目录的topic-to-published-video/autodl.env读取；可用--env-file指定另一个文件。环境变量优先。不要在聊天、命令参数、manifest、状态文件中放Key。

相对参考图路径从manifest目录解析；本地图转data URL。

```bash
python3 scripts/autodl_broll.py manifest.json --prepare-only --output-dir output
```

此命令仅校验和落盘请求体，不调用API。用户授权后：

```bash
python3 scripts/autodl_broll.py manifest.json --output-dir output
```

任务ID立即保存，重复运行相同输出目录续接已记录任务，不重新付费提交。失败任务不自动重试；追加生成使用新ID和新输出目录，并取得相应预算授权。勿更改已提交的同一ID请求内容。

## 工作流与验收

文字：minimax_h3_lightx2v_no_pic。参考图：minimax_h3_z0902，至少ref_image_0。首尾帧：minimax_h3_b99_002，first_frame和last_frame必填。更多工作流与精确枚举见[API说明](references/autodl_api.md)，不能在不同工作流之间混用resolution值。

接口可用性与价格由当前账户和服务决定；不承诺固定单价或始终比其他服务便宜。请求返回SUCCESS后仍核对非空文件、参数和完整动作；流程导演负责语义验收。

需要构建提示词时读[提示词指南](references/broll_prompting.md)，开始时可复制[文字示例](references/manifest_example.json)或[首尾帧示例](references/first_last_manifest_example.json)。
