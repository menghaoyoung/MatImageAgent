# 顶部导入（改为可选导入，避免顶层崩溃）
try:
    import speech_recognition as sr
except Exception:
    sr = None
from datetime import datetime
import json
import os
import urllib.request
import zipfile

MAX_WAIT_SECONDS = 15           # 最多等待你开口 15 秒
MAX_PHRASE_SECONDS = 15         # 开口后最长录音 15 秒
SILENCE_SECONDS = 5.0           # 连续静音 5 秒自动停止
START_ENERGY_THRESHOLD = 300    # 开口判定能量阈值（int16 平均绝对值）
SILENCE_ENERGY_THRESHOLD = 200  # 静音判定能量阈值（int16 平均绝对值）

def save_text(text, file_path="transcript.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
    return os.path.abspath(file_path)

def save_audio(audio_data, wav_path="last_input.wav"):
    wav_bytes = audio_data.get_wav_data()
    with open(wav_path, "wb") as f:
        f.write(wav_bytes)
    return os.path.abspath(wav_path)

def ensure_vosk_model(model_path="models/vosk-model-small-en-us-0.15"):
    abs_dir = os.path.abspath(model_path)
    if os.path.isdir(abs_dir):
        return abs_dir

    os.makedirs(os.path.dirname(abs_dir), exist_ok=True)
    zip_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = os.path.join(os.path.dirname(abs_dir), "vosk-model-small-en-us-0.15.zip")

    try:
        print(f"Downloading Vosk model (~50MB) from {zip_url} ...")
        urllib.request.urlretrieve(zip_url, zip_path)
        print("Download complete. Extracting...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(os.path.dirname(abs_dir))
        print("Extraction done.")

        # 常见解压目录名为 'vosk-model-small-en-us-0.15'
        if os.path.isdir(abs_dir):
            return abs_dir

        # 兼容可能出现的变体目录名
        base_dir = os.path.dirname(abs_dir)
        for name in os.listdir(base_dir):
            candidate = os.path.join(base_dir, name)
            if os.path.isdir(candidate) and name.startswith("vosk-model-small-en-us"):
                return candidate

        return abs_dir
    except Exception as e:
        print(f"Auto-download failed: {e}")
        return abs_dir

# 顶部常量（新增或确认）
MAX_WAIT_SECONDS = 15           # 最多等待你开口 15 秒
MAX_PHRASE_SECONDS = 15         # 开口后最长录音 15 秒
SILENCE_SECONDS = 5.0           # 连续静音 5 秒自动停止
START_ENERGY_THRESHOLD = 300    # 开口判定的平均能量阈值（int16）
SILENCE_ENERGY_THRESHOLD = 200  # 静音判定的平均能量阈值（int16）

# 移除顶部的 vosk 导入；改为在函数内按需导入
def transcribe_offline_vosk(audio, model_path="models/vosk-model-small-en-us-0.15"):
    try:
        from vosk import Model, KaldiRecognizer
    except Exception as e:
        print(f"Offline recognizer (Vosk) not installed: {e}")
        return ""
    # Convert audio to 16kHz, 16-bit PCM for Vosk
    raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
    if not os.path.isdir(model_path):
        print(f"Vosk model not found at: {os.path.abspath(model_path)}")
        print("Download 'vosk-model-small-en-us-0.15' and extract to the path above.")
        return ""

    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)
    if rec.AcceptWaveform(raw):
        result_json = rec.Result()
    else:
        result_json = rec.FinalResult()
    result = json.loads(result_json)
    return result.get("text", "").strip()

def transcribe_offline_vosk_wav(wav_path, model_path="models/vosk-model-small-en-us-0.15"):
    try:
        from vosk import Model, KaldiRecognizer
    except Exception as e:
        print(f"Offline recognizer (Vosk) not installed: {e}")
        return ""
    import wave, json, os
    if not (os.path.isfile(wav_path) and os.path.isdir(model_path)):
        print(f"Vosk model or wav not found. wav={wav_path}, model={model_path}")
        return ""
    wf = wave.open(wav_path, "rb")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    pieces = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            try:
                pieces.append(json.loads(rec.Result()).get("text", ""))
            except:
                pass
    try:
        final_text = json.loads(rec.FinalResult()).get("text", "")
    except:
        final_text = ""
    return " ".join([t for t in pieces + [final_text] if t]).strip()

def record_until_silence_sounddevice(
    max_wait=MAX_WAIT_SECONDS,
    max_phrase=MAX_PHRASE_SECONDS,
    silence_secs=SILENCE_SECONDS,
    samplerate=16000,
    out_path="last_input.wav",
):
    import sounddevice as sd
    import numpy as np
    import time
    import wave
    import queue

    print(f"[SD] Listening: wait up to {max_wait}s for speech, record up to {max_phrase}s, stop after {int(silence_secs)}s silence.")
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(f"[SD] Status: {status}")
        q.put(indata.copy())

    stream = sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        callback=callback,
    )

    frames = []
    voice_started = False
    last_voice_time = None
    start_time = time.monotonic()
    try:
        stream.start()
        while True:
            try:
                chunk = q.get(timeout=0.5)
            except queue.Empty:
                pass
            else:
                frames.append(chunk)
                energy = float(np.abs(chunk).mean())
                now = time.monotonic()

                if not voice_started:
                    if energy >= START_ENERGY_THRESHOLD:
                        voice_started = True
                        last_voice_time = now
                        print("[SD] Speech detected, recording...")
                    elif now - start_time >= max_wait:
                        print("[SD] No speech detected within wait window.")
                        return None
                else:
                    if energy >= SILENCE_ENERGY_THRESHOLD:
                        last_voice_time = now
                    if (now - last_voice_time) >= silence_secs or (now - start_time) >= (max_wait + max_phrase):
                        print("[SD] Silence timeout or max duration reached.")
                        break

        if frames:
            data = np.concatenate(frames, axis=0)
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(samplerate)
                wf.writeframes(data.tobytes())
            return os.path.abspath(out_path)
        return None
    finally:
        try:
            stream.stop()
            stream.close()
        except:
            pass
def main():
    try:
        wav_path = record_until_silence_sounddevice(
            max_wait=MAX_WAIT_SECONDS,
            max_phrase=MAX_PHRASE_SECONDS,
            silence_secs=SILENCE_SECONDS,
            samplerate=16000,
            out_path="last_input.wav",
        )
        if not wav_path:
            print("[STT] 未检测到有效语音，已跳过。")
            return

        model_dir = ensure_vosk_model("models/vosk-model-small-en-us-0.15")
        text = transcribe_offline_vosk_wav(wav_path, model_path=model_dir)
        if not text:
            print("[STT] 离线识别未获得文本。")
            return

        text_path = save_text(text)
        print(f"[STT] 识别文本：{text}")
        print(f"[STT] 转写保存：{text_path}")
        print(f"[STT] 录音文件：{wav_path}")
    except Exception as e:
        print(f"[STT] 语音流程失败：{e}")
        return
        audio_path = save_audio(audio) if audio is not None else wav_path
        print(f"Saved transcript to: {text_path}")
        print(f"Saved audio to: {audio_path}")

if __name__ == "__main__":
    main()