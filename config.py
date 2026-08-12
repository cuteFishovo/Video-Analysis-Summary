# 视频分析配置
# 搬到新电脑只需改这里

DEEPSEEK_API_KEY = ""

# ffmpeg 路径（留空则自动查找系统 PATH 中的 ffmpeg）
FFMPEG_BIN_DIR = ""

# Whisper 模型选择
#   tiny   (39M)  ─ 最快，~1GB 内存，准确率最低，适合快速测试
#   base   (74M)  ─ 较快，~1GB 内存，比 tiny 稍好
#   small  (244M) ─ 均衡，~2GB 内存，推荐日常使用
#   medium (769M) ─ 较慢，~5GB 内存，准确率很好，建议有独显
#   large  (1.5G) ─ 最慢，~10GB 显存，准确率最高，专业级
WHISPER_MODEL = "tiny"
