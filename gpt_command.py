import time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import TimeoutException

# === 설정 ===
from config import DEBUG_PORT, CHROMEDRIVER_PATH

def connect_driver():
    options = Options()
    # 실행 중인 크롬 인스턴스에 붙기
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    service = Service(CHROMEDRIVER_PATH) if CHROMEDRIVER_PATH else Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)
    return driver, wait

assistant_sel = "div[data-message-author-role='assistant']"
input_sel     = "div#prompt-textarea.ProseMirror[contenteditable='true']"
plus_btn_sel  = "button[data-testid='composer-plus-btn']"
file_sel      = "input[type='file']"
send_btnsel   = "button[data-testid='send-button']"

def wait_until_static(driver, timeout=120, idle_sec=2, poll=0.4):
    """
    assistant 카드가 idle_sec 동안 변하지 않으면 완료.
    card 엘리먼트가 교체·삭제돼도 안전하게 재탐색.
    """
    first_card = driver.find_elements(By.CSS_SELECTOR, assistant_sel)[-1]
    msg_id   = first_card.get_attribute("data-message-id") or ""
    selector = f"[data-message-id='{msg_id}']" if msg_id else assistant_sel

    last_len      = -1
    stable_since  = time.time()
    deadline      = time.time() + timeout

    while time.time() < deadline:
        # ── ① 카드 엘리먼트 다시 얻기 ──────────────────────────
        try:
            card = driver.find_element(By.CSS_SELECTOR, selector)
        except Exception:
            # placeholder 가 교체되면 id 가 달라지므로
            cards = driver.find_elements(By.CSS_SELECTOR, assistant_sel)
            if not cards:                    # 아직 아무것도 없다면 ↺
                time.sleep(poll)
                continue
            card     = cards[-1]             # 가장 마지막 assistant
            selector = assistant_sel            # 다음 loop 부턴 이 셀렉터

        # ── ② 스크롤 & 길이 측정 ───────────────────────────────
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", card
        )
        cur_len = driver.execute_script(
            "return arguments[0].innerText.length;", card
        )

        # ── ③ idle 판정 ───────────────────────────────────────
        if cur_len != last_len:
            last_len     = cur_len
            stable_since = time.time()
        elif time.time() - stable_since >= idle_sec:
            return card                      # ✅  스트리밍 끝!

        time.sleep(poll)

    raise TimeoutException("assistant reply not finished in time")


# === 메시지 및 이미지 전송 함수 정의 ===
def send_message(driver, wait, text: str, image_path: str | None = None) -> dict:
    """텍스트/이미지 전송 후 응답 반환 (ProseMirror 입력 대응)"""
    driver.get("https://chatgpt.com/?model=gpt-4o")
    wait.until(lambda d: 'chatgpt.com' in d.current_url)

    inp = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, input_sel)))
    inp.click()
    ActionChains(driver).send_keys(text).perform()
    
    if image_path:
        # plus 버튼이 가려져 있을 수 있으므로 시도
        try:
            plus_btn = driver.find_element(By.CSS_SELECTOR, plus_btn_sel)
            plus_btn.click()
        except Exception:
            pass  # 이미 열려 있으면 무시

        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, file_sel)))
        file_input.send_keys(os.path.abspath(image_path))
        time.sleep(1)  # 썸네일 로드 대기 (간단히)
    
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    prev = len(driver.find_elements(By.CSS_SELECTOR, assistant_sel))
    
    
    # ② Enter 키 이벤트를 강제로 디스패치  ▶ ProseMirror 가 ‘전송’ 으로 인식
    time.sleep(1)  # UI 가 버튼을 활성화할 시간
    try:
        send_btn = driver.find_element(By.CSS_SELECTOR, send_btnsel)
        if send_btn.is_enabled():
            send_btn.click()
    except Exception:
        pass 

    # ③ 새 assistant 턴 등장 대기
    
    wait_long = WebDriverWait(driver, 10)
    def ready(drv):
        cards = drv.find_elements(By.CSS_SELECTOR, assistant_sel)
        
        if len(cards) <= prev:
            return False
        last = cards[-1]
        drv.execute_script("arguments[0].scrollIntoView({block:'center'});", last)
        return True
    
    wait_long.until(ready) 

    
    wait_until_static(driver) 
    reply = driver.find_elements(By.CSS_SELECTOR, assistant_sel)[-1]
    return reply.text

