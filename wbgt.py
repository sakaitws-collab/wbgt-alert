import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.wbgt.env.go.jp/wbgt_data.php"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_wbgt():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find_all("table")

    # ✅ 全テーブルから東京を探す
    for table in tables:
        for row in table.find_all("tr"):
            cols = row.find_all("td")

            if len(cols) < 2:
                continue

            place = cols[0].get_text(strip=True)

            # ✅ 東京行を検出
            if "東京" in place:
                values = [c.get_text(strip=True) for c in cols]

                print("東京行の中身:", values)

                # ✅ 2列目（翌日）
                raw = values[1]
                print("翌日WBGT(raw):", raw)

                # ✅ 空データ対応
                if raw in ["", "--"]:
                    print("データなし（未公開）")
                    return None

                # ✅ 数値変換
                try:
                    return float(raw)
                except:
                    print("数値変換失敗:", raw)
                    return None

    print("東京が見つからない")
    return None


# ===== 実行 =====
wbgt = get_wbgt()
print("WBGT:", wbgt)

if wbgt is None:
    print("WBGT取得失敗 → 通知しない")
    exit()


# ===== 通知 =====
payload = {
    "type": "message",
    "text": f"🌡 東京 明日の最高暑さ指数：{wbgt}"
}

print("WEBHOOK_URL:", WEBHOOK_URL)

if not WEBHOOK_URL:
    print("Webhook URL未設定")
    exit()

response = requests.post(WEBHOOK_URL, json=payload)

print("status:", response.status_code)
print("response:", response.text)
