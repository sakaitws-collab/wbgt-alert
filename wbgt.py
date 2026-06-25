import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.wbgt.env.go.jp/wbgt_data.php"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def get_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # ===== 一番下の表 =====
    tables = soup.find_all("table")
    table = tables[-1]

    # ===== 東京の行を探す =====
    for row in table.find_all("tr"):
        cols = row.find_all("td")

        if cols:
            place = cols[0].get_text(strip=True)

            if "東京" in place:
                # ✅ 2列目（翌日）
                raw = cols[1].get_text(strip=True)

                try:
                    return float(raw)
                except:
                    return None

    return None


# ===== 実行 =====
wbgt = get_wbgt()

if wbgt is None:
    print("WBGT取得失敗")
    exit()

print("明日の最高暑さ指数:", wbgt)


# ===== 通知 =====
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
                        "text": "🌡明日の最高暑さ指数",
                        "size": "Large",
                        "weight": "Bolder"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"東京 明日の最高暑さ指数：{wbgt}",
                        "size": "Medium"
                    }
                ]
            }
        }
    ]
}

response = requests.post(WEBHOOK_URL, json=payload)
print("status:", response.status_code)
