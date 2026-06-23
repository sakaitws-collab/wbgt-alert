import requests
from bs4 import BeautifulSoup

# ===== 設定 =====
URL = "https://www.wbgt.env.go.jp/graph_ref_tm.php?region=03&prefecture=44&point=44132&refId=3"
WEBHOOK_URL = "https://default08bb7afa6044483795caee99eb9784.4b.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/963d83c9898541bfbfaa801149f47448/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=n6zvENvE2fWqkzo2trg_oAEv_i6rAU14v-oc_bM22qA"

# ===== WBGT取得 =====
def get_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.find_all("tr")

    tomorrow_values = []

    for i, row in enumerate(rows):
        if "明日" in row.get_text():
            next_row = rows[i + 1]
            cols = next_row.find_all("td")

            for col in cols:
                raw_text = col.get_text(strip=True)

                digits = "".join([c for c in raw_text if c.isdigit()])
                split_vals = [digits[i:i+2] for i in range(0, len(digits), 2)]

                for v in split_vals:
                    try:
                        val = float(v)
                        if 10 <= val <= 40:
                            tomorrow_values.append(val)
                    except:
                        pass
            break

    # ✅ 8個に制限
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

requests.post(WEBHOOK_URL, json=payload)
