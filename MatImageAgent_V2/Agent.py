import os
import re
import sys
import argparse
import subprocess
from openai import OpenAI
import wave
import json
import shutil

CONFIG = {
    'api_base': 'https://tbnx.plus7.plus/v1',
    'api_key': 'sk-VUh0cVQe6Jbtl0OND3LfghynsQFcYeEZP2snb0RwIsDm2lwb',
    'model': 'claude-3-7-sonnet-20250219',
    'max_tokens': 8192,
    'error_limit': 5,
    'pyfile_limit': 12,
    'encoding': 'UTF-8'
}

class ScriptExecutor:
    def __init__(self):
        self.client = OpenAI(
            base_url=CONFIG['api_base'],
            api_key=CONFIG['api_key']
        )
        self.conversation = []
        self.N_py = 1
        self.kk = 0

    def get_file_names(self):
        """Get file names in current directory"""
        files_and_dirs = os.listdir('.')
        files = [f for f in files_and_dirs if os.path.isfile(f)]
        return ' '.join(files)

    @staticmethod
    def pystr_extract(str1):
        """Extract Python code block from text"""
        match = re.search(r'```python\n(.*?)```', str1, re.DOTALL | re.IGNORECASE)
        return match.group(1) if match else "No Python code found."

    @staticmethod
    def pynotrun_check(str1):
        """Check if code execution is not required"""
        return re.search(r'NO-RUN-PY', str1, re.DOTALL | re.IGNORECASE)

    def execute_script(self, pystr):
        """Execute Python script and return output and errors"""
        filename = f"py{self.N_py}.py"
        with open(filename, "w", encoding=CONFIG['encoding']) as f:
            f.write(pystr)

        process = subprocess.Popen(
            [sys.executable, filename],  # 使用当前解释器，避免 'python' 指向错误版本
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process.communicate()

    def call_gpt_api(self, messages):
        """Call LLM API"""
        response = self.client.chat.completions.create(
            model=CONFIG['model'],
            messages=messages,
            max_tokens=CONFIG['max_tokens'],
            temperature=0.7,
            stream=False
        )
        # 兼容不同返回类型，统一抽取 content
        if isinstance(response, str):
            return response

        content = None
        # v1 SDK 标准对象
        if hasattr(response, "choices"):
            choices = response.choices
            if choices:
                message = getattr(choices[0], "message", None)
                if message is not None and hasattr(message, "content"):
                    content = message.content
                else:
                    text = getattr(choices[0], "text", None)
                    if text:
                        content = text
        # 字典/兼容旧接口
        if content is None and isinstance(response, dict):
            choices = response.get("choices")
            if choices:
                msg = choices[0].get("message")
                if isinstance(msg, dict):
                    content = msg.get("content") or msg.get("text")
                else:
                    content = choices[0].get("text")
            content = content or response.get("content")

        return content if content is not None else str(response)

    def error_check(self, error):
        """Handle execution errors"""
        k_error = 0
        while error and k_error < CONFIG['error_limit']:
            print(f"Error: {error}")
            Str_header = f"The previous program contained errors. [Error Details: {error}] Please rectify these issues and submit a corrected, complete, and executable program precisely tailored to the subtask requirements."
            
            self.conversation.append({"role": "user", "content": Str_header})
            str1 = self.call_gpt_api(self.conversation)
            
            print('##### correction:\n', str1)
            self.conversation.append({"role": "assistant", "content": str1})

            str_py1 = self.pystr_extract(str1)
            if str_py1 == "No Python code found.":
                print('Mission complete.')
                sys.exit()

            print(f'Begin to execute Python {k_error}')
            output, error = self.execute_script(str_py1)
            print(error, k_error, self.N_py)
            
            self.N_py += 1
            if self.N_py > CONFIG['pyfile_limit']:
                print('Mission failed.')
                sys.exit()
            
            k_error += 1

        return error

    def process_task(self, code_str):
        """Process main task"""
        print('Mission Start')
        output = ""
        files_str = ""
        
        while True:
            if self.kk > 0:
                Str_header = "Start writing the second or third program, or skip if all tasks have been completed. Follow these requirements: (1) Output a complete and executable program strictly adhering to the task instructions, avoiding sample programs. (2) Consider the output of the previous step and the file names in the current directory, as they may result from the previous program and could be utilized in writing the current program. [Previous Step Output]:"
                CONTENT = Str_header + output + ".[Current directory file names]:" + files_str + ". [previous Task Description]:" + code_str
            else:
                Str_header = "Please carefully review the task description below. You will need to create two to three Python programs. Start by crafting the first Python program to meet the following criteria: (1) Ensure the program is complete and executable, tailored precisely to the task's requirements. (2) Include print statements to display output results, aiding in subsequent tasks. Keep this in mind. (3) Begin your Python code with '```python\n' and end with '```'. (4) Check whether the program requires execution. If not, include the statement 'NO-RUN-PY' in your response.[Task Description]:"
                CONTENT = Str_header + code_str

            self.conversation.append({"role": "user", "content": CONTENT})
            str1 = self.call_gpt_api(self.conversation)
            
            print('##### answer:\n', str1)
            self.conversation.append({"role": "assistant", "content": str1})

            str_py1 = self.pystr_extract(str1)
            if str_py1 == "No Python code found.":
                print('Mission complete.')
                break

            if self.pynotrun_check(str1):
                with open(f"py{self.N_py}.py", "w", encoding=CONFIG['encoding']) as f:
                    f.write(str_py1)
                output = " "
                files_str = " "
            else:
                print('Begin to execute Python')
                output, error = self.execute_script(str_py1)
                error = self.error_check(error)
                if error:
                    continue

            self.N_py += 1
            if self.N_py > CONFIG['pyfile_limit']:
                print('Mission failed.')
                break

            files_str = self.get_file_names()
            print(f'Step {self.kk+1} is finished')
            self.kk += 1

        print('Mission Complete')

# 保留函数但注释说明不再调用，函数体无修改
def open_notepad_and_wait(file_path):
    """保留函数但项目中不再调用此功能"""
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            with open(file_path, "a", encoding=CONFIG['encoding']):
                pass
        # macOS 替换记事本命令为 TextEdit（系统自带编辑器）
        subprocess.run(["open", "-a", "TextEdit", file_path], check=False)
    except Exception as e:
        print(f"Failed to open editor: {e}")

# 模块级新增：调用外部语音转文字脚本
def run_stt_script(script_path, audio_path=None, output_txt_path=None, timeout=300):
    import shlex
    cmd = [sys.executable, script_path]
    # 优先尝试带参数形式（你的脚本如支持 --audio/--out）
    if audio_path:
        cmd += ["--audio", audio_path]
    if output_txt_path:
        cmd += ["--out", output_txt_path]
    print(f"[STT] Running: {' '.join(shlex.quote(str(c)) for c in cmd)}")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        if stderr:
            print(f"[STT] stderr: {stderr}")
        # 如果指定了输出文件且存在，则以文件内容为准
        if output_txt_path and os.path.exists(output_txt_path):
            try:
                with open(output_txt_path, "r", encoding=CONFIG['encoding']) as f:
                    transcript = f.read().strip()
                print(f"[STT] Loaded transcript from file: {output_txt_path}")
                return transcript
            except Exception as fe:
                print(f"[STT] Failed to read output file: {fe}")
        # 否则使用脚本标准输出
        if stdout and stdout.strip():
            print("[STT] Using stdout transcript")
            return stdout.strip()
        print("[STT] No transcript produced")
        return ""
    except subprocess.TimeoutExpired:
        print("[STT] Timeout expired while running the STT script")
        return ""
    except Exception as e:
        print(f"[STT] Failed to run STT script: {e}")
        return ""

# 新增：识别和音频转换所需


# 模块级新增：Vosk 语音转文字（要求：WAV/单声道/16k）
# 模块级新增：确保音频符合 WAV/单声道/16k；否则尝试用 ffmpeg 转换
def ensure_wav_mono_16k(audio_path):
    try:
        if audio_path.lower().endswith(".wav"):
            with wave.open(audio_path, "rb") as wf:
                ch, rate, width = wf.getnchannels(), wf.getframerate(), wf.getsampwidth()
            if ch == 1 and rate == 16000 and width == 2:
                return audio_path
    except Exception:
        pass
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("[Vosk] 未检测到 ffmpeg，建议安装后转换为 WAV/单声道/16k。")
        return audio_path
    out_wav = os.path.splitext(audio_path)[0] + "_mono16k.wav"
    cmd = [ffmpeg, "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", out_wav]
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(out_wav):
            print(f"[Vosk] 已转换音频为：{out_wav}")
            return out_wav
    except Exception as e:
        print(f"[Vosk] ffmpeg 转换失败：{e}")
    return audio_path

# 模块级新增：使用 Vosk 进行离线识别（简化版）
def transcribe_audio_vosk(audio_path, model_dir):
    try:
        from vosk import Model, KaldiRecognizer
    except Exception as e:
        print(f"[Vosk] 未安装 vosk，请先安装：pip install vosk。错误：{e}")
        return ""
    safe_audio = ensure_wav_mono_16k(audio_path)
    if not (os.path.exists(safe_audio) and os.path.exists(model_dir)):
        print("[Vosk] 模型目录或音频文件不存在。")
        return ""
    try:
        wf = wave.open(safe_audio, "rb")
    except Exception as e:
        print(f"[Vosk] 打开音频失败：{e}")
        return ""
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
        print("[Vosk] 音频格式不符合要求（需要单声道/16-bit PCM）。")
        return ""
    try:
        model = Model(model_dir)
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        texts = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                try:
                    texts.append(json.loads(rec.Result()).get("text", ""))
                except:
                    pass
        try:
            final_text = json.loads(rec.FinalResult()).get("text", "")
        except:
            final_text = ""
        return " ".join([t for t in texts + [final_text] if t]).strip()
    except Exception as e:
        print(f"[Vosk] 识别失败：{e}")
        return ""

# 顶层函数：运行麦克风语音采集脚本并加载转写文本
def run_mic_stt_script(script_path=None, transcript_path="transcript.txt", output_txt_path="Voice_demo.txt", timeout=120):
    # 调用现有 speech_to_text.py 并读取最新转写
    try:
        # 默认脚本路径：当前项目目录的 speech_to_text.py（已为相对路径，无需修改）
        script_path = script_path or os.path.join(os.getcwd(), "speech_to_text.py")
        if not os.path.exists(script_path):
            print(f"[STT] 脚本不存在：{script_path}")
            return ""

        print(f"[STT] 运行麦克风识别脚本：{script_path}")
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

        # 读取识别脚本生成的 transcript.txt（追加模式保存，多次识别会追加）
        trans_abs = transcript_path if os.path.isabs(transcript_path) else os.path.join(os.getcwd(), transcript_path)
        if not os.path.exists(trans_abs):
            print(f"[STT] 未找到转写文件：{trans_abs}")
            return ""

        # 取最后一条记录（最新一行），去除前缀时间戳
        try:
            with open(trans_abs, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
            last = lines[-1] if lines else ""
            # 格式示例：[2025-01-01 12:00:00] hello world
            voice_text = last.split("] ", 1)[1] if "] " in last else last
        except Exception as e:
            print(f"[STT] 读取转写文件失败：{e}")
            voice_text = ""

        # 将文本保存到 Voice_demo.txt，便于 MD 中引用或后续程序读取
        out_abs = output_txt_path if os.path.isabs(output_txt_path) else os.path.join(os.getcwd(), output_txt_path)
        if voice_text:
            try:
                with open(out_abs, "w", encoding=CONFIG['encoding']) as f:
                    f.write(voice_text)
                print(f"[STT] 已保存语音文本到：{out_abs}")
            except Exception as e:
                print(f"[STT] 保存语音文本失败：{e}")

        return voice_text
    except subprocess.TimeoutExpired:
        print("[STT] 脚本运行超时")
        return ""
    except Exception as e:
        print(f"[STT] 运行语音脚本失败：{e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description='Process some file.')
    parser.add_argument('-s', metavar='filename', type=str, default='', help='the name of the file or string to process')
    # 简化后的 Vosk 选项（移除外部脚本）
    parser.add_argument('--use-vosk', action='store_true', help='Use Vosk STT to generate Voice_demo.txt')
    parser.add_argument('--audio', type=str, help='Path to audio file for Vosk STT')
    # 修正Vosk模型默认路径为macOS相对路径
    parser.add_argument('--vosk-model', type=str, default=os.path.join(os.getcwd(), "models/vosk-model-small-en-us-0.15"), help='Path to Vosk model directory (default: ./models/vosk-model-small-en-us-0.15)')
    parser.add_argument('--stt-out', type=str, default='Voice_demo.txt', help='Where to save transcript text')
    args = parser.parse_args()

    s_value = (args.s or '').strip()
    # MD_demo.txt 路径改为当前目录相对路径（已为os.path.join(os.getcwd())，无需修改）
    md_default = os.path.join(os.getcwd(), "MD_demo.txt")

    # 1) 移除 edit 模式逻辑，不再调用 open_notepad_and_wait
    if s_value.lower() == "edit":
        print("提示：已移除编辑器调用功能，直接读取 MD_demo.txt 内容")
        s_value = md_default  # 转为直接读取文件

    # 统一处理 MD 文本读取（不再区分 edit 模式）
    if s_value.endswith(".txt") and ' ' not in s_value and os.path.exists(s_value):
        with open(s_value, "r", encoding=CONFIG['encoding']) as file:
            md_text = file.read()
    elif s_value:
        md_text = s_value
    else:
        if not os.path.exists(md_default):
            print(f"MD demo file not found: {md_default}")
            sys.exit(1)
        with open(md_default, "r", encoding=CONFIG['encoding']) as file:
            md_text = file.read()

    # 2) 恢复语音生成询问逻辑（核心修改）
    voice_text = ""
    try:
        choice = input("是否通过语音生成新的 Voice_demo.txt（覆盖原有文件）？输入 y 确认，其他键使用已有文件：").strip().lower()
        if choice in ("y", "yes"):
            print("[STT] 开始麦克风语音采集，请注意说话...")
            voice_text = run_mic_stt_script(
                script_path=os.path.join(os.getcwd(), "speech_to_text.py"),
                transcript_path="transcript.txt",
                output_txt_path="Voice_demo.txt",
                timeout=120
            )
            if not voice_text:
                print("[STT] 未获取到有效语音文本，将使用已有 Voice_demo.txt")
    except Exception as e:
        print(f"[STT] 语音采集交互失败：{e}")

    # 3) 强制读取 Voice_demo.txt 并合并（无论是否生成新文件）
    voice_demo_path = os.path.join(os.getcwd(), "Voice_demo.txt")
    try:
        with open(voice_demo_path, "r", encoding=CONFIG['encoding']) as f:
            voice_text = f.read().strip()
        print(f"[INFO] 已读取 Voice_demo.txt 内容并合并到任务描述")
    except Exception as e:
        print(f"[WARN] 读取 Voice_demo.txt 失败：{e}")
        voice_text = ""

    # 合并 MD 与语音文本
    if voice_text:
        code_str = f"[Task Description from MD_demo]:\n{md_text}\n\n[Voice Transcript]:\n{voice_text}\n"
    else:
        code_str = md_text

    executor = ScriptExecutor()
    executor.process_task(code_str)

    # 自动调用独立调试程序（DebugAgent.py），路径改为当前目录相对路径
    try:
        dbg_path = os.path.join(os.getcwd(), "DebugAgent.py")
        if os.path.exists(dbg_path):
            print("[Debug] 正在自动运行 DebugAgent.py ...")
            proc = subprocess.Popen(
                [sys.executable, dbg_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=600)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
        else:
            print("[Debug] 未找到 DebugAgent.py，跳过自动调试。")
    except Exception as e:
        print(f"[Debug] 自动调试失败：{e}")

if __name__ == "__main__":
    main()