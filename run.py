"""
Video Analysis - One-click video analysis tool
Usage:
  1. Put MP4 files into the "视频" folder next to this script
  2. Edit API Key in config.py
  3. Run: python run.py
"""

import os
import sys
sys.dont_write_bytecode = True
import shutil
import subprocess
import time
from pathlib import Path

# ====== Paths ======
SCRIPT_DIR = Path(__file__).resolve().parent
VIDEO_DIR = SCRIPT_DIR / "视频"
OUTPUT_DIR = VIDEO_DIR / "分析结果"

# ====== Load config ======
sys.path.insert(0, str(SCRIPT_DIR))
from config import DEEPSEEK_API_KEY, FFMPEG_BIN_DIR, WHISPER_MODEL

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MAX_ANALYSIS_CHARS = 6000

# ====== I18N: Read language from env var or lang.txt ======
def _load_lang():
    """Load language setting: 1=EN 2=ZH 3=JA 4=KO 5=ES 6=FR"""
    lang_key = os.environ.get("VIDEO_ANALYSIS_LANG", "")
    if not lang_key:
        lang_file = SCRIPT_DIR / "lang.txt"
        if lang_file.exists():
            lang_key = lang_file.read_text(encoding="utf-8").strip()
    return lang_key if lang_key in {str(i) for i in range(1, 7)} else "1"

LANG_KEY = _load_lang()
LANG_IDX = int(LANG_KEY) - 1  # 0-based

# i18n messages: [EN, ZH, JA, KO, ES, FR]
MSG = {
    "ffmpeg_not_found": [
        "ffmpeg not found! Install and set FFMPEG_BIN_DIR in config.py",
        "找不到 ffmpeg！请安装后在 config.py 中设置 FFMPEG_BIN_DIR",
        "ffmpegが見つかりません！インストールしてconfig.pyでFFMPEG_BIN_DIRを設定してください",
        "ffmpeg를 찾을 수 없습니다! 설치 후 config.py에서 FFMPEG_BIN_DIR를 설정하세요",
        "¡ffmpeg no encontrado! Instale y configure FFMPEG_BIN_DIR en config.py",
        "ffmpeg introuvable ! Installez et configurez FFMPEG_BIN_DIR dans config.py"
    ],
    "found_videos": [
        "Found {n} video(s)",
        "找到 {n} 个视频",
        "{n}件の動画が見つかりました",
        "{n}개의 비디오를 찾았습니다",
        "Se encontraron {n} video(s)",
        "{n} vidéo(s) trouvée(s)"
    ],
    "no_videos": [
        "No videos! Put MP4 files into: {path}",
        "没有视频！请把 MP4 放到: {path}",
        "動画がありません！MP4を {path} に入れてください",
        "비디오가 없습니다! MP4를 {path}에 넣어주세요",
        "¡No hay videos! Ponga MP4 en: {path}",
        "Aucune vidéo ! Mettez les MP4 dans : {path}"
    ],
    "extracting_audio": [
        "  Extracting audio ... ",
        "  提取音频 ... ",
        "  音声を抽出中 ... ",
        "  오디오 추출 중 ... ",
        "  Extrayendo audio ... ",
        "  Extraction audio ... "
    ],
    "failed": ["Failed", "失败", "失敗", "실패", "Falló", "Échec"],
    "done": ["Done", "完成", "完了", "완료", "Hecho", "Terminé"],
    "done_mb": [
        "Done ({size:.1f} MB)",
        "完成 ({size:.1f} MB)",
        "完了 ({size:.1f} MB)",
        "완료 ({size:.1f} MB)",
        "Hecho ({size:.1f} MB)",
        "Terminé ({size:.1f} MB)"
    ],
    "transcribing": [
        "  Transcribing ... ",
        "  语音转文字 ... ",
        "  文字起こし中 ... ",
        "  음성 → 텍스트 변환 중 ... ",
        "  Transcribiendo ... ",
        "  Transcription ... "
    ],
    "done_chars": [
        "Done ({n} chars)",
        "完成 ({n} 字)",
        "完了 ({n}文字)",
        "완료 ({n}자)",
        "Hecho ({n} caracteres)",
        "Terminé ({n} caractères)"
    ],
    "api_fail": [
        "  API failed: {code}",
        "  API 失败: {code}",
        "  API失敗: {code}",
        "  API 실패: {code}",
        "  API falló: {code}",
        "  API échoué: {code}"
    ],
    "api_error": [
        "  Request error: {e}",
        "  请求异常: {e}",
        "  リクエストエラー: {e}",
        "  요청 오류: {e}",
        "  Error de solicitud: {e}",
        "  Erreur de requête: {e}"
    ],
    "title": [
        "  Video One-Click Analysis",
        "  视频一键分析",
        "  動画ワンクリック分析",
        "  비디오 원클릭 분석",
        "  Análisis de Video en Un Click",
        "  Analyse Vidéo en Un Clic"
    ],
    "loading_whisper": [
        "Loading Whisper ({model}) ... ",
        "加载 Whisper ({model}) ... ",
        "Whisper ({model}) をロード中 ... ",
        "Whisper ({model}) 로드 중 ... ",
        "Cargando Whisper ({model}) ... ",
        "Chargement de Whisper ({model}) ... "
    ],
    "step1_title": [
        "  Step 1: Transcribe Audio",
        "  第一步：转录音频",
        "  ステップ1：音声の文字起こし",
        "  1단계: 오디오转录",
        "  Paso 1: Transcribir Audio",
        "  Étape 1 : Transcrire l'audio"
    ],
    "step2_title": [
        "  Step 2: DeepSeek Analysis",
        "  第二步：DeepSeek 分析",
        "  ステップ2：DeepSeek分析",
        "  2단계: DeepSeek 분석",
        "  Paso 2: Análisis DeepSeek",
        "  Étape 2 : Analyse DeepSeek"
    ],
    "step3_title": [
        "  Step 3: Global Summary",
        "  第三步：全局总结",
        "  ステップ3：全体要約",
        "  3단계: 전체 요약",
        "  Paso 3: Resumen Global",
        "  Étape 3 : Résumé global"
    ],
    "skip_existing": [
        "  Transcription exists, skipping",
        "  已有转录，跳过",
        "  文字起こし済み、スキップ",
        " 转录 존재, 건너뜀",
        "  Transcripción existente, omitiendo",
        "  Transcription existante, ignorée"
    ],
    "transcribe_fail": [
        "  Transcription failed: {e}",
        "  转录失败: {e}",
        "  文字起こし失敗: {e}",
        "  转录 실패: {e}",
        "  Transcripción fallida: {e}",
        "  Échec de la transcription: {e}"
    ],
    "transcribe_complete": [
        "Transcription complete: {done}/{total}",
        "转录完成: {done}/{total}",
        "文字起こし完了: {done}/{total}",
        "转录 완료: {done}/{total}",
        "Transcripción completa: {done}/{total}",
        "Transcription terminée: {done}/{total}"
    ],
    "analyzing": [
        "[Analyzing] {name}",
        "[分析] {name}",
        "[分析] {name}",
        "[분석] {name}",
        "[Analizando] {name}",
        "[Analyse] {name}"
    ],
    "calling_api": [
        "  Calling DeepSeek ... ",
        "  调用 DeepSeek ... ",
        "  DeepSeekを呼び出し中 ... ",
        "  DeepSeek 호출 중 ... ",
        "  Llamando a DeepSeek ... ",
        "  Appel de DeepSeek ... "
    ],
    "all_done": [
        "  All done -> {path}",
        "  全部完成 → {path}",
        "  全て完了 → {path}",
        "  전부 완료 → {path}",
        "  Todo listo → {path}",
        "  Tout terminé → {path}"
    ],
}

# Language-specific prompts
PROMPT_SYSTEM = {
    "1": "Professional video content analyst, skilled at summarizing and extracting key points.",
    "2": "专业视频内容分析助手，擅长总结和提炼要点。",
    "3": "プロの動画コンテンツ分析アシスタント、要約と要点抽出が得意。",
    "4": "전문 비디오 콘텐츠 분석 도우미, 요약 및 핵심 포인트 추출에 능숙.",
    "5": "Asistente profesional de análisis de contenido de video, experto en resumir y extraer puntos clave.",
    "6": "Assistant professionnel d'analyse de contenu vidéo, expert en synthèse et extraction de points clés.",
}

PROMPT_SINGLE = {
    "1": (
        "Analyze the following video transcript:\n"
        "1. [Content Summary] Summarize the main content\n"
        "2. [Key Points] Extract key knowledge points or steps\n\n"
        "Video: {name}\nContent: {text}\n\n"
        "Format:\n## Content Summary\n(content)\n## Key Points\n- Point 1\n- Point 2\n- ..."
    ),
    "2": (
        "分析以下视频转录内容：\n"
        "1. 【内容总结】概括主要内容\n"
        "2. 【关键要点】提取关键知识点或操作步骤\n\n"
        "视频：{name}\n内容：{text}\n\n"
        "格式：\n## 内容总结\n（内容）\n## 关键要点\n- 要点1\n- 要点2\n- ..."
    ),
    "3": (
        "以下の動画文字起こしを分析してください：\n"
        "1. 【内容要約】主な内容を要約\n"
        "2. 【重要ポイント】重要な知識や手順を抽出\n\n"
        "動画：{name}\n内容：{text}\n\n"
        "形式：\n## 内容要約\n（内容）\n## 重要ポイント\n- ポイント1\n- ポイント2\n- ..."
    ),
    "4": (
        "다음 비디오转录을 분석하세요:\n"
        "1. 【내용 요약】주요 내용 요약\n"
        "2. 【핵심 포인트】주요 지식 또는 단계 추출\n\n"
        "비디오: {name}\n내용: {text}\n\n"
        "형식:\n## 내용 요약\n(내용)\n## 핵심 포인트\n- 포인트1\n- 포인트2\n- ..."
    ),
    "5": (
        "Analice la siguiente transcripción de video:\n"
        "1. [Resumen de Contenido] Resuma el contenido principal\n"
        "2. [Puntos Clave] Extraiga puntos clave o pasos\n\n"
        "Video: {name}\nContenido: {text}\n\n"
        "Formato:\n## Resumen de Contenido\n(contenido)\n## Puntos Clave\n- Punto 1\n- Punto 2\n- ..."
    ),
    "6": (
        "Analysez la transcription vidéo suivante :\n"
        "1. [Résumé du Contenu] Résumez le contenu principal\n"
        "2. [Points Clés] Extrayez les points clés ou étapes\n\n"
        "Vidéo: {name}\nContenu: {text}\n\n"
        "Format:\n## Résumé du Contenu\n(contenu)\n## Points Clés\n- Point 1\n- Point 2\n- ..."
    ),
}

PROMPT_GLOBAL = {
    "1": "The following video transcripts are on the same topic. Provide a global summary, extracting core content and knowledge framework:\n\n",
    "2": "以下视频转录是同一主题，做全局总结，提炼核心内容和知识体系：\n\n",
    "3": "以下の動画文字起こしは同じテーマです。全体要約を作成し、核心的内容と知識体系を抽出してください：\n\n",
    "4": "다음 비디오转录은 동일한 주제입니다. 전체 요약을 작성하고 핵심 내용과 지식 체계를 추출하세요:\n\n",
    "5": "Las siguientes transcripciones de video son del mismo tema. Proporcione un resumen global, extrayendo el contenido central y el marco de conocimiento:\n\n",
    "6": "Les transcriptions vidéo suivantes portent sur le même sujet. Fournissez un résumé global, en extrayant le contenu central et le cadre de connaissances :\n\n",
}

def t(key, **kwargs):
    """Get translated message"""
    msg = MSG[key][LANG_IDX]
    if kwargs:
        return msg.format(**kwargs)
    return msg


def find_ffmpeg():
    """Auto-find ffmpeg: config > PATH > common locations"""
    if FFMPEG_BIN_DIR:
        path = Path(FFMPEG_BIN_DIR) / "ffmpeg.exe"
        if path.exists():
            return str(path)
        path = Path(FFMPEG_BIN_DIR) / "ffmpeg"
        if path.exists():
            return str(path)

    found = shutil.which("ffmpeg")
    if found:
        return found

    common = [
        Path.home() / "AppData/Local/Microsoft/WinGet/Packages",
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
    ]
    for base in common:
        if base.exists():
            if base.is_dir():
                for exe in base.rglob("ffmpeg.exe"):
                    return str(exe)
            else:
                return str(base)

    print(f"❌ {MSG['ffmpeg_not_found'][LANG_IDX]}")
    return None


FFMPEG_PATH = find_ffmpeg()
if not FFMPEG_PATH:
    sys.exit(1)

os.environ["PATH"] = str(Path(FFMPEG_PATH).parent) + os.pathsep + os.environ.get("PATH", "")
import whisper


def find_videos():
    videos = sorted(VIDEO_DIR.glob("*.mp4"))
    print(f"\n{t('found_videos', n=len(videos))}")
    for v in videos:
        print(f"  {v.name}  ({v.stat().st_size / 1024 / 1024:.1f} MB)")
    return videos


def extract_audio(video_path, audio_path):
    print(t("extracting_audio"), end="", flush=True)
    cmd = [
        FFMPEG_PATH, "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-y", "-loglevel", "error", str(audio_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(t("failed"))
        return False
    print(t("done_mb", size=audio_path.stat().st_size / 1024 / 1024))
    return True


def transcribe(model, audio_path):
    print(t("transcribing"), end="", flush=True)
    result = model.transcribe(str(audio_path), language="zh", verbose=False, fp16=False)
    text = result["text"].strip()
    print(t("done_chars", n=len(text)))
    return text


def call_deepseek(prompt, max_retries=3):
    import requests
    for i in range(max_retries):
        try:
            resp = requests.post(DEEPSEEK_API_URL, headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }, json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": PROMPT_SYSTEM.get(LANG_KEY, PROMPT_SYSTEM["1"])},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            print(t("api_fail", code=resp.status_code))
        except Exception as e:
            print(t("api_error", e=e))
        if i < max_retries - 1:
            time.sleep(2)
    return None


def main():
    print("=" * 50)
    print(t("title"))
    print(f"  ffmpeg: {FFMPEG_PATH}")
    print("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    videos = find_videos()
    if not videos:
        print(f"\n{t('no_videos', path=VIDEO_DIR)}")
        return

    # Load Whisper
    print(f"\n{t('loading_whisper', model=WHISPER_MODEL)}", end="", flush=True)
    model = whisper.load_model(WHISPER_MODEL)
    print(t("done"))

    # Step 1: Transcribe
    print(f"\n{'='*50}")
    print(t("step1_title"))
    print(f"{'='*50}")

    transcriptions = {}
    for i, vp in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] {vp.name}")
        txt_path = OUTPUT_DIR / f"{vp.stem}_转录.txt"

        if txt_path.exists():
            print(t("skip_existing"))
            transcriptions[vp.name] = txt_path.read_text(encoding="utf-8")
            continue

        audio_path = OUTPUT_DIR / f"{vp.stem}_音频.wav"
        if not extract_audio(vp, audio_path):
            continue
        try:
            text = transcribe(model, audio_path)
        except Exception as e:
            print(t("transcribe_fail", e=e))
            continue
        txt_path.write_text(text, encoding="utf-8")
        transcriptions[vp.name] = text
        audio_path.unlink(missing_ok=True)

    print(f"\n{t('transcribe_complete', done=len(transcriptions), total=len(videos))}")

    # Step 2: Analyze
    print(f"\n{'='*50}")
    print(t("step2_title"))
    print(f"{'='*50}")

    for vname, text in transcriptions.items():
        print(f"\n{t('analyzing', name=vname)}")
        if len(text) > MAX_ANALYSIS_CHARS:
            text = text[:MAX_ANALYSIS_CHARS] + "\n...(truncated)"

        prompt = PROMPT_SINGLE.get(LANG_KEY, PROMPT_SINGLE["1"]).format(name=vname, text=text)

        print(t("calling_api"), end="", flush=True)
        result = call_deepseek(prompt)
        if result:
            path = OUTPUT_DIR / f"{Path(vname).stem}_分析.md"
            path.write_text(result, encoding="utf-8")
            print(t("done"))
        else:
            print(t("failed"))

    # Step 3: Global Summary
    if len(transcriptions) > 1:
        print(f"\n{'='*50}")
        print(t("step3_title"))
        print(f"{'='*50}")

        parts = [f"### {v}\n{t[:800]}..." for v, t in transcriptions.items()]
        prompt = PROMPT_GLOBAL.get(LANG_KEY, PROMPT_GLOBAL["1"]) + "\n\n".join(parts)

        print(t("calling_api"), end="", flush=True)
        r = call_deepseek(prompt)
        if r:
            (OUTPUT_DIR / "全局总结.md").write_text(r, encoding="utf-8")
            print(t("done"))

    print(f"\n{'='*50}")
    print(t("all_done", path=OUTPUT_DIR))
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
