
import socket
from pathlib import Path
import subprocess, socket, tempfile, time
from config import DEBUG_PORT

def launch_chrom_debug_linux():
    # 1) 기존 크롬 완전 종료
    subprocess.call(["pkill", "-f", "chrome"])

    # 2) 디버깅 모드 크롬 실행
    
    # ▶ 기본 프로필 대신 임시 전용 프로필 디렉터리 사용
    debug_profile = Path(tempfile.gettempdir()) / "chrome_debug_profile"
    debug_profile.mkdir(exist_ok=True)

    args = [
        "google-chrome",
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={debug_profile}",         # ★ 필수
        "--profile-directory=Default",
        "--remote-allow-origins=*",
        "--no-first-run", "--no-default-browser-check"
    ]
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 포트 열릴 때까지 최대 10초 대기
    for _ in range(20):
        try:
            with socket.create_connection(("127.0.0.1", DEBUG_PORT), timeout=0.5):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("DevTools 포트가 열리지 않았습니다.")

def launch_chrome_debug_window():
    chrome_path = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not chrome_path.exists():
        chrome_path = Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")

    # ▶ 기본 프로필 대신 임시 전용 프로필 디렉터리 사용
    debug_profile = Path(tempfile.gettempdir()) / "chrome_debug_profile"
    debug_profile.mkdir(exist_ok=True)

    args = [
        str(chrome_path),
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={debug_profile}",         # ★ 필수
        "--profile-directory=Default",
        "--remote-allow-origins=*",
        "--no-first-run", "--no-default-browser-check"
    ]
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 포트 열릴 때까지 최대 10초 대기
    for _ in range(20):
        try:
            with socket.create_connection(("127.0.0.1", DEBUG_PORT), timeout=0.5):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("DevTools 포트가 열리지 않았습니다.")

