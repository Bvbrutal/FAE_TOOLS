import subprocess
import sys
import os
from pathlib import Path

def get_embedded_addr2line_path():
    base_dir = Path(__file__).resolve().parent.parent
    tools_dir = base_dir / "bin"

    if sys.platform.startswith("win"):
        exe_path = tools_dir / "addr2line.exe"
    elif sys.platform.startswith("linux"):
        exe_path = tools_dir / "addr2line"
    elif sys.platform == "darwin":
        exe_path = tools_dir / "addr2line"  # macOS 同 Linux
    else:
        raise RuntimeError("Unsupported platform")

    if not exe_path.exists():
        raise FileNotFoundError(f"Embedded addr2line not found: {exe_path}")
    return str(exe_path)

def addr2line(binary, addr):
    addr2line_path = get_embedded_addr2line_path()
    cmd = [addr2line_path, "-e", binary, addr, "-f", "-C","-p"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# 示例
if __name__ == "__main__":
    print(addr2line(r"D:\PSH\tomato_clock\pythonProject\test.exe", "0x1146"))
