# 视频分析总结

> 纯本地部署、无需网络（总结需 AI API）的一键视频分析工具。

将 MP4 视频丢进文件夹，一键提取音频 → Whisper 语音转文字 → DeepSeek AI 总结，生成结构化 Markdown 分析报告。

---

## 工作流程

```
MP4 视频 → ffmpeg 提取音频(.wav) → OpenAI Whisper 语音转文字 → DeepSeek API 分析总结 → 生成 .md 报告
```

## 功能特性

- **纯本地处理** - ffmpeg + Whisper 均在本地运行，不上传视频/音频到任何服务器
- **6 语言界面** - 支持中文、English、日本語、한국어、Español、Français
- **一键安装** - `setup.bat` 自动检查/安装 Python、pip 依赖、ffmpeg
- **批量处理** - 支持多个视频依次分析，最后自动生成全局总结
- **断点续传** - 已转录的视频再次运行会跳过，避免重复消耗 API
- **模型可选** - 支持 tiny / base / small / medium / large 五种 Whisper 模型

## 系统要求

- Windows 10/11
- Python 3.x（setup 会自动安装）
- ffmpeg（setup 会自动安装）
- DeepSeek API Key（需自行注册获取）

## 快速开始

### 1. 安装环境

双击 `setup.bat`，脚本会自动：
- 检查并安装 Python 3.11
- 安装 `requirements.txt` 中的 Python 依赖
- 检查并安装 ffmpeg
- 创建 `config.py` 配置文件

### 2. 配置 API Key

编辑项目根目录下的 `config.py`，填入你的 DeepSeek API Key：

```python
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

> 获取 API Key：[platform.deepseek.com](https://platform.deepseek.com)

### 3. 放入视频

将 `.mp4` 视频文件放入项目根目录下的 `视频` 文件夹。

### 4. 运行分析

双击 `run.bat` 或使用整合面板 `gui.bat` 选择"运行分析"，脚本将依次：
1. 提取音频（生成 `.wav`）
2. Whisper 语音转文字（生成 `_转录.txt`）
3. DeepSeek 分析（生成 `_分析.md`）
4. 如有多个视频，自动生成 `全局总结.md`

所有输出文件保存在 `视频/分析结果/` 目录下。

## 配置文件说明 (`config.py`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥（必填） | `""` |
| `FFMPEG_BIN_DIR` | ffmpeg 所在目录（留空自动查找） | `""` |
| `WHISPER_MODEL` | Whisper 模型大小 | `"tiny"` |

### Whisper 模型选择

| 模型 | 大小 | 内存 | 特点 |
|------|------|------|------|
| `tiny` | 39M | ~1GB | 最快，适合快速测试 |
| `base` | 74M | ~1GB | 比 tiny 稍好 |
| `small` | 244M | ~2GB | 均衡，推荐日常使用 |
| `medium` | 769M | ~5GB | 准确率高，建议有独显 |
| `large` | 1.5G | ~10GB | 准确率最高，专业级 |

## 项目结构

```
├── gui.bat / gui.ps1     # 整合面板（安装/运行/切换语言）
├── setup.bat / setup.ps1  # 环境安装
├── run.bat / run.ps1      # 运行分析
├── run.py                 # 核心分析程序
├── config.py              # 配置文件（API Key / 模型选择）
├── lang.ps1 / lang.json   # 多语言系统
├── lang.txt               # 当前语言选择（1-6）
├── requirements.txt       # Python 依赖
├── 视频/                  # 放 MP4 视频的文件夹
│   └── 分析结果/          # 分析输出目录
└── 必读.txt               # 项目说明
```

## 常见问题

**Q: 运行时提示找不到 ffmpeg？**  
A: 先运行 `setup.bat` 自动安装，或手动安装后确保 ffmpeg 在系统 PATH 中。

**Q: API 调用失败？**  
A: 检查 `config.py` 中的 `DEEPSEEK_API_KEY` 是否正确填写，确保网络能访问 DeepSeek API。

**Q: Whisper 模型下载慢？**  
A: 模型首次运行会自动下载，可设置 `HF_ENDPOINT=https://hf-mirror.com` 环境变量使用镜像加速。

## License

MIT

---

**纯本地 | 零上传 | 开源免费**
