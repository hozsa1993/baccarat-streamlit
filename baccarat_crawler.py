import time
import sqlite3
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 設定 ---
URL = "https://new-dd-cn.izogcnj.com/ddnewpc/index.html?token=362f1fd8c2b2441d8e76216c25a635b0&language=cn&back=1&gameId=0&showapp=off&type=5&return=dggw.vip"

DB_PATH = "baccarat_history.db"

# --- 初始化 DB ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS baccarat_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT,
        result TEXT,
        game_time TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# --- 儲存資料 ---
def save_to_db(table_name, result, game_time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO baccarat_results (table_name, result, game_time)
        VALUES (?, ?, ?)
    """, (table_name, result, game_time))
    conn.commit()
    conn.close()
    print(f"[已儲存] 桌號:{table_name}, 結果:{result}, 時間:{game_time}")

# --- 主爬蟲 ---
def baccarat_crawler():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)
    driver.get(URL)

    wait = WebDriverWait(driver, 60)

    print("[啟動] 正在監控百家樂最新結果...")

    last_result = None

    while True:
        try:
            # 等待結果元素出現 (依據實際網站調整 XPath)
            result_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'roadBeadWrap')]//li[last()]")
            ))

            # 取得最新結果文字（依實際 class 調整）
            result_text = result_element.text.strip()

            # 取得桌號（依實際位置調整）
            table_element = driver.find_element(By.XPATH, "//div[contains(@class,'table-name')]")
            table_name = table_element.text.strip()

            # 取得時間（或用當前時間）
            game_time = time.strftime("%Y-%m-%d %H:%M:%S")

            # 去除重複
            if result_text != last_result and result_text != "":
                last_result = result_text
                save_to_db(table_name, result_text, game_time)

            time.sleep(5)  # 每 5 秒抓一次

        except Exception as e:
            print(f"[錯誤] {e}")
            time.sleep(5)

if __name__ == "__main__":
    init_db()
    baccarat_crawler()
