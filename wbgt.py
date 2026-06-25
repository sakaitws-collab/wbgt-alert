import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

URL = "https://www.wbgt.env.go.jp/graph_ref_td.php?region=03&prefecture=44&point=44132&refId=3"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_tomorrow_max_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # ✅ ページ全体のテキストを取得
    text = soup.get_text()

    # ✅ 明日の日付
    tomorrow = datetime.now() + timedelta(days=1)
    target = f"明日({tomorrow.month}月{tomorrow.day}日)"

    # ✅ 明日ブロック抽出
    start_index = text.find(target)

    if start_index == -1:
        print("明日が見つからない")
        return None

    # 次の「明後日」で終了
    end_index = text.find("明後日", start_index)

    if end_index == -1:
        print("明後日が見つからない")
        return None

    block = text[start_index:end_index]

    print("抽出ブロック:", block)

    # ✅ 数値抽出（WBGTっぽいものだけ）
    numbers = re.findall(r'\d+\.\d+|\d+', block)

    values = []

    for n in numbers:
        try:
            val = float(n)
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


# ===== Teams通知 =====
payload = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": f"🌡 明日のWBGT最大：{wbgt}",
                        "size": "Large",
                        "weight": "Bolder"
                    }
                ]
            }
        }
    ]
}

response = requests.post(WEBHOOK_URL, json=payload)
print("status:", response.status_code)
