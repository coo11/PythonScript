# ASS 字幕相关的批量处理脚本

### [batch2utf8.py](batch2utf8.py)

- 使用 `chardet` 模块，将 txt，lrc，ass，ssa，srt 等 plain text 文件批量转换为 UTF-8 编码，需提供目标文件的目录。
- 接下来的脚本，务必保证处理字幕文件前已将其**转换为 UTF-8 编码**。

### [batchEditAssAssociateWithVideo.py](batchEditAssAssociateWithVideo.py)

- 将一组有序命名的 ass 文件和同目录有序命名的视频文件名相关联，即通过在 ass 中记录视频名称，以方便使用 Aegisub 等软件编辑测试。需提供目标文件的目录

### [batchOpenCC4ASS.py](batchOpenCC4ASS.py)

- 使用 `OpenCC` 模块，将 ass 字幕文本进行批量繁简互转。需提供目标文件的目录
- 有误伤日文字幕中的汉字的可能。已做匹配处理，所以需在转换前，确保日文字幕的样式名称包含 ‘jp‘ 或 ’japan‘ 等字符

### [batchOpenCC4PlainText.py](batchOpenCC4PlainText.py)

- 大致同上，但适用性更广泛，可将 txt，lrc，ass，ssa，srt 等 plain text 文件进行繁简互转
- 包含的日文被误伤的可能性较大，使用前需仔细检查

### [batchRemoveRedundantStyle.py](batchRemoveRedundantStyle.py)

- 批量将 ass 字幕文件中的冗余样式移除。需提供目标文件的目录

### [GenerateAllFontsNeeded.py](GenerateAllFontsNeeded.py)

- 获取并汇总一组 ass 字幕所需的所有字体名称，可导出一份文本清单。需提供目标文件的目录
