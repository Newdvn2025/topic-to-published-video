# GitHub首次发布

## 建议仓库信息

- 名称：topic-to-published-video
- Description：面向AI科普创作者的选题到成片Skill：AutoDL B-roll、口播/数字人、视频包装、封面与小红书发布文案。
- Topics：agent-skills, codex, ai-video, xiaohongshu, autodl, hyperframes, remotion
- 首版标签：v0.1.0

## 上传范围

只上传本目录内容，把README.md、SKILL.md、LICENSE放在仓库根目录。不要上传完整FPV制作项目、旧版本ZIP、用户录音、真人视频、缓存、Key或本地初始化状态。

首次可通过GitHub新建公开仓库，再上传本目录所有文件；已有仓库则将本目录内容放在选定位置。此步骤需要操作者确认公开范围；技能制作本身不代表已发布。

## 本地Git方式

在解压得到的topic-to-published-video目录内执行：

```bash
git init
git add .
git diff --cached --stat
git commit -m "Release initial video production skill"
git branch -M main
```

Git身份需使用你自己的配置。然后在GitHub创建仓库，把GitHub提供的真实仓库地址设为origin，再push；不使用本文虚构的地址。

## 发布前检查

运行README的三条检查命令，核对LICENSE与公开示例范围。初始化脚本只完成技能安装；远程安装、ChatCut应用连接和真实AutoDL账户仍需各用户验证，不在Release里声称已全面测试。

MIT适用于本包原创内容；第三方工具沿用其许可证与服务条款。确认接受MIT许可后再公开。

## Release与安装说明

发布v0.1.0时可附干净技能ZIP和SHA256，正文使用CHANGELOG。仓库建好后可以提供实际仓库的skills安装命令，或按README手动安装；不要在仓库地址尚未确定前宣称某条远程安装命令已经可用。
