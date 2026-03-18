import requests
import time
from telegram import Bot

# ===== CONFIG =====
TOKEN = "8787831925:AAHc0mN3s6_sE4GwhBfqwU_FecQc6klZrW8"
CHAT_ID = "8595770963"

APIS = [
    "https://markers-amenities-vertex-gratuit.trycloudflare.com/api/tx"
]

bot = Bot(token=TOKEN)

last_phien = None
du_doan_truoc = None
history = []

# =========================
# 🔥 ENGINE 1: TREND
# =========================
def trend_engine(data):
    recent = data[-10:]
    tai = recent.count("TAI")
    xiu = recent.count("XIU")

    if tai > xiu:
        return "TAI", 0.7
    elif xiu > tai:
        return "XIU", 0.7
    return recent[-1], 0.5


# =========================
# ⚡ ENGINE 2: PATTERN
# =========================
def pattern_engine(data):
    if len(data) < 5:
        return data[-1], 0.5

    a,b,c,d,e = data[-5:]

    # bệt dài
    if a == b == c == d == e:
        return e, 0.9

    # đảo chuẩn
    if a != b and b != c and c != d and d != e:
        return "TAI" if e == "XIU" else "XIU", 0.8

    # 2-2
    if a == b and c == d:
        return e, 0.7

    return e, 0.5


# =========================
# 💥 ENGINE 3: BREAK
# =========================
def break_engine(data):
    if len(data) < 3:
        return data[-1], 0.5

    a,b,c = data[-3:]

    if a == b and b != c:
        return c, 0.8

    return c, 0.5


# =========================
# 🚀 ENGINE 4: MOMENTUM
# =========================
def momentum_engine(data):
    if len(data) < 6:
        return data[-1], 0.5

    last6 = data[-6:]

    change = sum(1 for i in range(1,6) if last6[i] != last6[i-1])

    if change >= 4:
        return "TAI" if last6[-1] == "XIU" else "XIU", 0.75

    return last6[-1], 0.5


# =========================
# 🧠 COMBINE AI
# =========================
def ultra_predict(data):
    t1,w1 = trend_engine(data)
    t2,w2 = pattern_engine(data)
    t3,w3 = break_engine(data)
    t4,w4 = momentum_engine(data)

    score = {"TAI":0, "XIU":0}

    score[t1] += w1
    score[t2] += w2
    score[t3] += w3
    score[t4] += w4

    result = "TAI" if score["TAI"] > score["XIU"] else "XIU"
    confidence = round(max(score.values()) / sum(score.values()) * 100)

    return result, confidence


# =========================
# 🚨 DETECT CẦU ĐẸP
# =========================
def detect_cau(data):
    if len(data) < 4:
        return ""

    if data[-1] == data[-2] == data[-3]:
        return "🔥 Cầu bệt đẹp"

    if data[-1] != data[-2] != data[-3]:
        return "⚡ Cầu đảo đẹp"

    return ""


# =========================
# 📡 GET DATA (ANTI LỆCH)
# =========================
def get_data():
    for api in APIS:
        try:
            res = requests.get(api, timeout=5).json()
            if "phien" in res and "ket_qua" in res:
                return res
        except:
            continue
    return None


# =========================
# 🚀 MAIN LOOP
# =========================
while True:
    try:
        data = get_data()

        if not data:
            time.sleep(3)
            continue

        phien = data["phien"]
        ket_qua = data["ket_qua"]

        if phien != last_phien:
            history.append(ket_qua)

            # check win/lose
            if du_doan_truoc:
                dung = "✅" if du_doan_truoc == ket_qua else "❌"
            else:
                dung = "..."

            # AI predict
            du_doan, conf = ultra_predict(history)

            # detect cầu
            cau = detect_cau(history)

            msg = f"""
📡 Phiên: {phien}
📌 Kết quả: {ket_qua}

🔮 Dự đoán: {du_doan}
📊 Độ tin cậy: {conf}%

{cau}

Kết quả trước: {dung}
            """

            bot.send_message(chat_id=CHAT_ID, text=msg)

            du_doan_truoc = du_doan
            last_phien = phien

        time.sleep(3)

    except Exception as e:
        print("Lỗi:", e)
        time.sleep(5)
