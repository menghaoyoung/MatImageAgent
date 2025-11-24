import os
import re
import sys
import subprocess
from typing import Tuple

try:
    from openai import OpenAI
except Exception as e:
    print(f"Missing OpenAI SDK: {e}. Please install 'openai'.")
    sys.exit(1)

# 复用 Agent.py 的 CONFIG；若失败则使用环境变量或默认值
try:
    from Agent import CONFIG
except Exception:
    CONFIG = {
        'api_base': os.environ.get('OPENAI_BASE_URL', ''),
        'api_key': os.environ.get('OPENAI_API_KEY', ''),
        'model': os.environ.get('OPENAI_MODEL', ''),
        'max_tokens': 4096,
        'encoding': 'UTF-8'
    }

def pystr_extract(text: str) -> str:
    m = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else "No Python code found."

def run_script(script_path: str) -> Tuple[str, str]:
    if not os.path.exists(script_path):
        return "", f"Script not found: {script_path}"
    try:
        p = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = p.communicate(timeout=180)
        return stdout or "", stderr or ""
    except subprocess.TimeoutExpired:
        return "", "Timeout expired while running the script."
    except Exception as e:
        return "", f"Failed to run script: {e}"

def load_text(path: str) -> str:
    try:
        with open(path, "r", encoding=CONFIG.get('encoding', 'UTF-8')) as f:
            return f.read()
    except Exception as e:
        return f"[LOAD-ERROR] {path}: {e}"

def save_text(path: str, content: str) -> None:
    with open(path, "w", encoding=CONFIG.get('encoding', 'UTF-8')) as f:
        f.write(content)

def call_llm(messages):
    client = OpenAI(base_url=CONFIG['api_base'], api_key=CONFIG['api_key'])
    resp = client.chat.completions.create(
        model=CONFIG['model'],
        messages=messages,
        max_tokens=CONFIG.get('max_tokens', 4096),
        temperature=0.3,
        stream=False,
    )
    # 统一抽取 content
    if hasattr(resp, "choices") and resp.choices:
        msg = getattr(resp.choices[0], "message", None)
        if msg and hasattr(msg, "content"):
            return msg.content
        text = getattr(resp.choices[0], "text", None)
        if text:
            return text
    if isinstance(resp, dict):
        ch = resp.get("choices")
        if ch:
            m = ch[0].get("message")
            if isinstance(m, dict):
                return m.get("content") or m.get("text")
            return ch[0].get("text")
        return resp.get("content")
    return str(resp)

def build_prompt(md_text: str, py_code: str, py_stdout: str, py_stderr: str) -> list:
    sys_msg = {
        "role": "system",
        "content": (
            "You are an expert Python debugging assistant. "
            "Given the task context (MD_demo.txt), the current program, and its execution logs, "
            "produce a corrected, complete, and executable Python program."
        )
    }
    user_msg = {
        "role": "user",
        "content": (
            "Task Context (from MD_demo.txt):\n"
            "-------------------------------\n"
            f"{md_text}\n\n"
            "Current Program:\n"
            "----------------\n"
            f"{py_code}\n\n"
            "Execution Logs:\n"
            "---------------\n"
            f"STDOUT:\n{py_stdout}\n\n"
            f"STDERR:\n{py_stderr}\n\n"
            "Requirements:\n"
            "1) Return ONLY a single corrected Python program wrapped in a code fence starting with '```python' and ending with '```'.\n"
            "2) The program must be complete and executable, with necessary imports and robust error handling.\n"
            "3) Where external dependencies may be missing (e.g., Pillow), gracefully handle via optional imports or fallback logic (do not run pip).\n"
            "4) Print key results to stdout to verify success.\n"
            "5) Keep file paths relative to the current directory when reading/writing."
        )
    }
    return [sys_msg, user_msg]

def find_latest_py_script(preferred="py1.py") -> str:
    import glob
    files = glob.glob(os.path.join(os.getcwd(), "py*.py"))
    if not files:
        return os.path.join(os.getcwd(), preferred)
    def parse_num(f):
        m = re.search(r'py(\d+)\.py$', os.path.basename(f))
        return int(m.group(1)) if m else -1
    files_sorted = sorted(files, key=parse_num, reverse=True)
    return files_sorted[0]

def debug_py(md_path="MD_demo.txt", py_path="py1.py", out_path="py1a.py"):
    md_text = load_text(md_path)
    if not os.path.exists(py_path):
        py_path = find_latest_py_script(py_path)
    py_code = load_text(py_path)

    py_stdout, py_stderr = run_script(py_path)
    print("=== Current Script STDOUT ===")
    print(py_stdout)
    print("=== Current Script STDERR ===")
    print(py_stderr)

    messages = build_prompt(md_text, py_code, py_stdout, py_stderr)
    llm_reply = call_llm(messages)

    corrected = pystr_extract(llm_reply)
    if corrected == "No Python code found.":
        print("LLM did not return a Python code block. Full reply:")
        print(llm_reply)
        sys.exit(1)

    save_text(out_path, corrected)
    print(f"Saved debugged program to: {out_path}")

    # 试运行修复后的程序
    out_stdout, out_stderr = run_script(out_path)
    print("=== Debugged Script STDOUT ===")
    print(out_stdout)
    print("=== Debugged Script STDERR ===")
    print(out_stderr)

if __name__ == "__main__":
    debug_py(
        md_path=os.path.join(os.getcwd(), "MD_demo.txt"),
        py_path=os.path.join(os.getcwd(), "py1.py"),
        out_path=os.path.join(os.getcwd(), "py1a.py"),
    )