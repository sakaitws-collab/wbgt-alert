import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

URL = "https://www.wbgt.env.go.jp/graph_ref_td.php?region=03&prefecture=44&point=44132&refId=3"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_tomorrow_max_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.find_all("tr")

    # ✅ 明日の日付を作る（例: 6月26日）
    tomorrow = datetime.now() + timedelta(days=1)
    target_str = f"{tomorrow.month}月{tomorrow.day}日"

    values = []
    collecting = False

    for row in rows:
        text = row.get_text()

        # ✅ 明日のブロック開始
        if target_str in text:
            collecting = True
            print("明日ブロック開始:", text)
            continue

        # ✅ 次の日付が来たら終了
        if collecting and ("月" in text and "日" in text):
            print("次の日付検出 → 終了:", text)
            break

        # ✅ 明日のデータ収集
        if collecting:
            cols = row.find_all("td")

            if len(cols) >= 2:
                raw = cols[1].get_text(strip=True)

                try:
                    val = float(raw)
                    if 10 <= val <= 40:  # WBGTの正常範囲
                        values.append(val)
                except:
                    pass

    print("明日のWBGT一覧:", values)

    if not values:
        return None

    return max(values)


# ===== 実行 =====
wbgt = get_tomorrow_max_wbgt()
print("明日の最大WBGT:", wbgt)

if wbgt is None:
    print("WBGT取得失敗 → 通知しない")
    exit()


# ===== 通知 =====
payload = {
    "type": "message",
    "text": f"🌡 東京 明日の最高暑さ指数：{wbgt}"
}

if not WEBHOOK_URL:
    print("Webhook URL未設定")
    exit()

response = requests.post(WEBHOOK_URL, json=payload)

print("status:", response.status_code)
print("response:", response.text)
