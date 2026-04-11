import requests
import re
import yfinance as yf
import smtplib
import os
from datetime import datetime

def get_cape():
    url = "https://www.multpl.com/shiller-pe"
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, timeout=10, headers=headers).text
    match = re.search(r'Current Shiller PE Ratio is ([\d.]+)', html)
    if match:
        return float(match.group(1))
    raise ValueError("Could not parse CAPE from multpl.com")

def get_voo_data():
    voo = yf.Ticker("VOO")
    hist = voo.history(period="1y")
    info = voo.info
    price = hist["Close"].iloc[-1]
    ma50  = hist["Close"].rolling(50).mean().iloc[-1]
    ma200 = hist["Close"].rolling(200).mean().iloc[-1]
    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low  = info.get("fiftyTwoWeekLow")
    return price, ma50, ma200, week52_high, week52_low

def get_cape_zone(cape):
    if cape < 20:
        return "Steal",     "S", 0,  0,  0
    elif cape < 25:
        return "Cheap",     "C", 0,  0,  5
    elif cape < 30:
        return "Fair",      "F", 10,  5, 15
    elif cape < 35:
        return "Elevated",  "L", 20, 15, 25
    elif cape < 40:
        return "Expensive", "E", 30, 25, 35
    else:
        return "Extreme",   "X", 40, 35, 45

def get_ma_signal(ma50, ma200):
    spread = (ma50 - ma200) / ma200 * 100
    if spread > 2:
        return "Bullish",  1, spread, "9"
    elif spread < -5:
        return "Bearish", -1, spread, "1"
    else:
        return "Neutral",  0, spread, "5"

def get_flag(price, week52_high, week52_low):
    pct_below_high = (week52_high - price) / week52_high * 100
    pct_above_low  = (price - week52_low)  / week52_low  * 100
    below_high = pct_below_high > 10
    above_low  = pct_above_low  > 25
    if below_high and not above_low:
        return "Buy",      1, pct_below_high, pct_above_low, "9"
    elif above_low and not below_high:
        return "Sell",    -1, pct_below_high, pct_above_low, "1"
    else:
        return "Neutral",  0, pct_below_high, pct_above_low, "5"

def get_action(score, flag_signal):
    actions = {
        -4: "100% SPAXX + sell 5%",
        -3: "50/50 + sell 5%",
        -2: "100% SPAXX + do nothing",
        -1: "50/50 + do nothing",
         0: "Maintain split + do nothing",
         1: "100% VOO + do nothing",
         2: "Maintain split + deploy 5%",
         3: "100% VOO + deploy 5%",
         4: "100% VOO + deploy 10%",
    }
    exceptions = {
        (-2, "Sell"): "Maintain split + sell 5%",
        ( 3, "Buy"):  "Maintain split + deploy 10%",
    }
    return exceptions.get((score, flag_signal), actions.get(score, "Unknown score"))

def get_maintain_split(target_pct):
    voo_pct = 100 - target_pct
    return str(voo_pct) + "% VOO / " + str(target_pct) + "% SPAXX"

def send_text(subject, body):
    gmail_user     = os.environ["GMAIL_USERNAME"]
    gmail_passkey  = os.environ["GMAIL_APP_PASSKEY"]
    phone_number   = os.environ["PHONE_NUMBER"]
    to             = phone_number + "@vzwpix.com"
    message        = "Subject: " + subject + "\n\n" + body
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login(gmail_user, gmail_passkey)
    smtp.sendmail(gmail_user, to, message)
    smtp.quit()

def main():
    print("=" * 60)
    print("  CMA MONTHLY DECISION -- " + datetime.now().strftime("%B %Y"))
    print("=" * 60)

    cape = get_cape()
    price, ma50, ma200, week52_high, week52_low = get_voo_data()

    zone_label, zone_code, target_pct, floor_pct, ceiling_pct = get_cape_zone(cape)
    ma_signal, ma_score, ma_spread, ma_code = get_ma_signal(ma50, ma200)
    flag_signal, flag_score, pct_below_high, pct_above_low, flag_code = get_flag(price, week52_high, week52_low)

    print("\nCAPE: " + str(round(cape, 2)) + " -> " + zone_label)
    print("   Target SPAXX pool: " + str(target_pct) + "% (acceptable: " + str(floor_pct) + "%-" + str(ceiling_pct) + "%)")
    print("   Maintain split: " + get_maintain_split(target_pct))

    print("\nVOO Price: $" + str(round(price, 2)))
    print("   50-day MA:  $" + str(round(ma50, 2)))
    print("   200-day MA: $" + str(round(ma200, 2)))
    print("   MA Spread:  " + str(round(ma_spread, 2)) + "% -> " + ma_signal + " (score " + str(ma_score) + ")")

    print("\n52-Week High: $" + str(round(week52_high, 2)) + " | Low: $" + str(round(week52_low, 2)))
    print("   " + str(round(pct_below_high, 1)) + "% below 52w high (>10% = buy flag)")
    print("   " + str(round(pct_above_low, 1)) + "% above 52w low  (>25% = sell flag)")
    print("   Flag: " + flag_signal + " (score " + str(flag_score) + ")")

    print("\n" + "-" * 60)
    print("  ACTION -- CHECK YOUR SPAXX BALANCE")
    print("  (Active portfolio = VOO value + SPAXX - $50)")
    print("-" * 60)

    actions = {}
    for funding_label, funding_score, funding_desc in [
        ("Underfunded", -2, "SPAXX pool < " + str(floor_pct) + "% of active portfolio"),
        ("Funded",       0, "SPAXX pool between " + str(floor_pct) + "% and " + str(ceiling_pct) + "%"),
        ("Overfunded",   2, "SPAXX pool > " + str(ceiling_pct) + "% of active portfolio"),
    ]:
        score = funding_score + ma_score + flag_score
        score = max(-4, min(4, score))
        action = get_action(score, flag_signal)
        actions[funding_label] = action
        print("\n  If " + funding_desc + ":")
        print("  -> Score " + str(score) + " (" + funding_label + "): " + action)

    scenario_key = zone_code + ma_code + flag_code

    print("\n" + "=" * 60)
    print("  CALCULATOR CODE: " + scenario_key)
    print("=" * 60)

    subject = "CMA Readout - " + datetime.now().strftime("%B %Y")
    body = (
        "CAPE: " + str(round(cape, 2)) + " (" + zone_label + ")\n"
        "VOO: $" + str(round(price, 2)) + "\n"
        "MA: 50d $" + str(round(ma50, 2)) + " / 200d $" + str(round(ma200, 2)) + " / Spread " + str(round(ma_spread, 2)) + "% (" + ma_signal + ")\n"
        "52w High: $" + str(round(week52_high, 2)) + " (-" + str(round(pct_below_high, 1)) + "%) / Low: $" + str(round(week52_low, 2)) + " (+" + str(round(pct_above_low, 1)) + "%) (" + flag_signal + ")\n"
        "----------------------\n"
        "U: " + actions["Underfunded"] + "\n"
        "F: " + actions["Funded"] + "\n"
        "O: " + actions["Overfunded"] + "\n"
        "----------------------\n"
        "Calculator Code: " + scenario_key
    )

    send_text(subject, body)
    print("\nText sent successfully.")

if __name__ == "__main__":
    main()
