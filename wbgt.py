import requests
from bs4 import BeautifulSoup
import os

# ===== 設定 =====
URL = "https://www.wbgt.env.go.jp/graph_ref_tm.php?region=03&prefecture=44&point=44132&refId=3"

# ✅ GitHub Secretsから取得
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# ===== WBGT取得 =====
def get_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.find_all("tr")

    tomorrow_values = []

    for i, row in enumerate(rows):
        if "明日" in row.get_text():
            # 明日の数値は次の行
            next_row = rows[i + 1]
            cols = next_row.find_all("td")

            for col in cols:
                raw_text = col.get_text(strip=True)

                # 数字だけ抜く
                digits = "".join([c for c in raw_text if c.isdigit()])

                # 2桁ずつ分割
                split_vals = [digits[i:i+2] for i in range(0, len(digits), 2)]

                for v in split_vals:
                    try:
                        val = float(v)
                        # WBGTとしてあり得る範囲だけ
                        if 10 <= val <= 40:
                            tomorrow_values.append(val)
                    except:
                        pass

            break

    # ✅ 最初の8個だけ使う
    tomorrow_values = tomorrow_values[:8]

    print("明日のWBGT:", tomorrow_values)

    if not tomorrow_values:
        return None

    return max(tomorrow_values)


# ===== 実行 =====
wbgt = get_wbgt()

if wbgt is None:
    print("WBGT取得失敗")
    exit()

print("最大WBGT:", wbgt)


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
