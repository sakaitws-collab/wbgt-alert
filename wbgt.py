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

    # ✅ 明日の日付
    tomorrow = datetime.now() + timedelta(days=1)
    target_str = f"明日({tomorrow.month}月{tomorrow.day}日)"

    values = []
    collecting = False

    for row in rows:
        text = row.get_text(strip=True)

        # ✅ 完全一致で明日スタート
        if target_str in text:
            collecting = True
            print("✅ 明日ブロック開始:", text)
            continue

        # ✅ 明後日が来たら終了
        if collecting and "明後日" in text:
            print("✅ 明日ブロック終了:", text)
            break

        # ✅ データ行だけ拾う
        if collecting:
            cols = row.find_all("td")

            if len(cols) >= 2:
                raw = cols[1].get_text(strip=True)

                try:
                    val = float(raw)
                    if 10 <= val <= 40:
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
    "text": f"🌡 東京 明日の最高WBGT：{wbgt}"
}

if not WEBHOOK_URL:
    print("Webhook URL未設定")
    exit()

response = requests.post(WEBHOOK_URL, json=payload)

print("status:", response.status_code)
print("response:", response.text)
