# 贡献指南

欢迎提交实际工作流中的改进。Issue请包含宿主、操作系统、Python/Node版本、选择的工具、复现步骤、预期与实际结果。日志先移除密钥、账号、签名下载链接和私人素材。

修改流程时说明影响的入口、确认点、真源与下游文件。不要把个人作者身份、固定风格或单期制作方案写成全局要求。修改脚本需增加覆盖真实失败行为的测试。

本地检查：

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s addons/autodl-broll/tests
```

不在CI提交付费生成或要求真实API Key。工具技能从官方来源安装，不把第三方完整源码或媒体无授权地打包。提交修改表示同意按仓库MIT许可提供该贡献。
