# 文件、状态与交付契约

项目唯一真源：01-script.md（实录前口播稿；实录后记录最终文字）、02-transcript.json（真实文字与时间）、03-design.md（视觉）、04-storyboard.md（时间轴）、05-asset-manifest.json（正式素材版本）。02-transcript.srt是字幕导出，不独立改写。

已有项目使用不同名称时，在production-state.json.artifacts记录规范映射；别名为只读导出，不能同时维护两套。

其余产物：00-brief.md、06-review.md、07-cover-copy.md、08-social-copy.md、09-comment-prompts.md（仅承诺提示词时需要）、creator.json、production-log.md、out/review、out/final、out/covers。模板提供最小结构，可按项目增加字段。

## 状态

production-state.json只保留最新值。每次完成阶段或收到明确确认后原位更新，历史追加到production-log.md。记录确认对应产物与用户原话，不把“继续”无限延伸为发布授权。

上游变更时在pending记录受影响的字幕、分镜、素材或渲染，不把旧确认当新版本确认。review_approved要求对应具体文件。cover_approved独立记录。

## 时间精度

transcript.precision：segment或word；没有音频时timing_status为pending_audio，segments为空。真实SRT可标ready_segment；词级事件只有对齐工具证据时才标ready_word。没有词时间时words为null，不能均分填充。

## 收尾

delivery_ready之前核对视频、字幕、源项目、封面、发布文案和承诺评论资料。每个路径指向实际文件，缺项列入pending并说明原因；published需另有发布URL/ID等证据。
