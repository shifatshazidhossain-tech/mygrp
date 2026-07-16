import requests
import time
import re  # মেসেজ থেকে OTP বের করার জন্য
import json # ইনলাইন বাটনকে JSON ফরম্যাটে পাঠানোর জন্য

# কনফিগারেশন
API_URL = "http://147.135.212.197/crapi/had/viewstats"
API_TOKEN = "Qk9YREFBUzREbJlDfVFmYWB1UUN5X2Z0VotzeFhmmFhnTniDfpOWYg=="
TELEGRAM_BOT_TOKEN = "8801373789:AAG_mMkGJbzlbCPEvXQnWyj25zsLb2qwp0o"
CHAT_ID = "-1004329839431"

# ইতোমধ্যে পাঠানো মেসেজ ট্র্যাক করার জন্য ডিকশনারি
sent_messages = {}


def fetch_sms():
    params = {'token': API_TOKEN, 'records': 1000}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Connection Error: {e}")
    return None


def normalize_item(item):
    message = item.get("message") or item.get("sms") or item.get("text") or item.get("msg") or ""
    return {
        "dt": str(item.get("dt", "")),
        "num": str(item.get("num", "")),
        "cli": str(item.get("cli", "")),
        "message": str(message),
    }

COUNTRY_CODES = {
    "1": ("NANP (USA/Canada/Caribbean)", "🇺🇸"),
    "7": ("Russia/Kazakhstan", "🇷🇺"),
    "20": ("Egypt", "🇪🇬"),
    "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco/Western Sahara", "🇲🇦"),
    "213": ("Algeria", "🇩🇿"),
    "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"),
    "220": ("Gambia", "🇬🇲"),
    "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"),
    "223": ("Mali", "🇲🇱"),
    "224": ("Guinea", "🇬🇳"),
    "225": ("Côte d'Ivoire", "🇨🇮"),
    "226": ("Burkina Faso", "🇧🇫"),
    "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"),
    "229": ("Benin", "🇧🇯"),
    "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"),
    "232": ("Sierra Leone", "🇸🇱"),
    "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"),
    "235": ("Chad", "🇹🇩"),
    "236": ("Central African Republic", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"),
    "238": ("Cape Verde", "🇨🇻"),
    "239": ("São Tomé and Príncipe", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"),
    "241": ("Gabon", "🇬🇦"),
    "242": ("Republic of the Congo", "🇨🇬"),
    "243": ("Democratic Republic of the Congo", "🇨🇩"),
    "244": ("Angola", "🇦🇴"),
    "245": ("Guinea-Bissau", "🇬🇼"),
    "246": ("British Indian Ocean Territory", "🇮🇴"),
    "247": ("Ascension Island", "🇦🇨"),
    "248": ("Seychelles", "🇸🇨"),
    "249": ("Sudan", "🇸🇩"),
    "250": ("Rwanda", "🇷🇼"),
    "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"),
    "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"),
    "256": ("Uganda", "🇺🇬"),
    "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"),
    "261": ("Madagascar", "🇲🇬"),
    "262": ("Réunion/Mayotte", "🇷🇪"),
    "263": ("Zimbabwe", "🇿🇼"),
    "264": ("Namibia", "🇳🇦"),
    "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"),
    "267": ("Botswana", "🇧🇼"),
    "268": ("Eswatini", "🇸🇿"),
    "269": ("Comoros", "🇰🇲"),
    "27": ("South Africa", "🇿🇦"),
    "290": ("Saint Helena", "🇸🇭"),
    "291": ("Eritrea", "🇪🇷"),
    "297": ("Aruba", "🇦🇼"),
    "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"),
    "30": ("Greece", "🇬🇷"),
    "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"),
    "33": ("France", "🇫🇷"),
    "34": ("Spain", "🇪🇸"),
    "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"),
    "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"),
    "356": ("Malta", "🇲🇹"),
    "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"),
    "36": ("Hungary", "🇭🇺"),
    "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"),
    "372": ("Estonia", "🇪🇪"),
    "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"),
    "376": ("Andorra", "🇦🇩"),
    "377": ("Monaco", "🇲🇨"),
    "378": ("San Marino", "🇸🇲"),
    "379": ("Vatican City", "🇻🇦"),
    "380": ("Ukraine", "🇺🇦"),
    "381": ("Serbia", "🇷🇸"),
    "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"),
    "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia and Herzegovina", "🇧🇦"),
    "389": ("North Macedonia", "🇲🇰"),
    "39": ("Italy", "🇮🇹"),
    "40": ("Romania", "🇷🇴"),
    "41": ("Switzerland", "🇨🇭"),
    "423": ("Liechtenstein", "🇱🇮"),
    "43": ("Austria", "🇦🇹"),
    "44": ("United Kingdom", "🇬🇧"),
    "45": ("Denmark", "🇩🇰"),
    "46": ("Sweden", "🇸🇪"),
    "47": ("Norway", "🇳🇴"),
    "48": ("Poland", "🇵🇱"),
    "49": ("Germany", "🇩🇪"),
    "500": ("Falkland Islands", "🇫🇰"),
    "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"),
    "503": ("El Salvador", "🇸🇻"),
    "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"),
    "506": ("Costa Rica", "🇨🇷"),
    "507": ("Panama", "🇵🇦"),
    "508": ("Saint Pierre and Miquelon", "🇵🇲"),
    "509": ("Haiti", "🇭🇹"),
    "51": ("Peru", "🇵🇪"),
    "52": ("Mexico", "🇲🇽"),
    "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"),
    "55": ("Brazil", "🇧🇷"),
    "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"),
    "58": ("Venezuela", "🇻🇪"),
    "590": ("Guadeloupe/St Martin/St Barth", "🇬🇵"),
    "591": ("Bolivia", "🇧🇴"),
    "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"),
    "594": ("French Guiana", "🇬🇫"),
    "595": ("Paraguay", "🇵🇾"),
    "596": ("Martinique", "🇲🇶"),
    "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"),
    "599": ("Caribbean Netherlands", "🇧🇶"),
    "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"),
    "62": ("Indonesia", "🇮🇩"),
    "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"),
    "65": ("Singapore", "🇸🇬"),
    "66": ("Thailand", "🇹🇭"),
    "670": ("Timor-Leste", "🇹🇱"),
    "671": ("Northern Mariana Islands", "🇲🇵"),
    "672": ("Australian External Territories", "🇦🇺"),
    "673": ("Brunei", "🇧🇳"),
    "674": ("Nauru", "🇳🇷"),
    "675": ("Papua New Guinea", "🇵🇬"),
    "676": ("Tonga", "🇹🇴"),
    "677": ("Solomon Islands", "🇸🇧"),
    "678": ("Vanuatu", "🇻🇺"),
    "679": ("Fiji", "🇫🇯"),
    "680": ("Palau", "🇵🇼"),
    "681": ("Wallis and Futuna", "🇼🇫"),
    "682": ("Cook Islands", "🇨🇰"),
    "683": ("Niue", "🇳🇺"),
    "685": ("Samoa", "🇼🇸"),
    "686": ("Kiribati", "🇰🇮"),
    "687": ("New Caledonia", "🇳🇨"),
    "688": ("Tuvalu", "🇹🇻"),
    "689": ("French Polynesia", "🇵🇫"),
    "690": ("Tokelau", "🇹🇰"),
    "691": ("Micronesia", "🇫🇲"),
    "692": ("Marshall Islands", "🇲🇭"),
    "81": ("Japan", "🇯🇵"),
    "82": ("South Korea", "🇰🇷"),
    "84": ("Vietnam", "🇻🇳"),
    "850": ("North Korea", "🇰🇵"),
    "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"),
    "856": ("Laos", "🇱🇦"),
    "86": ("China", "🇨🇳"),
    "880": ("Bangladesh", "🇧🇩"),
    "886": ("Taiwan", "🇹🇼"),
    "90": ("Turkey", "🇹🇷"),
    "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"),
    "93": ("Afghanistan", "🇦🇫"),
    "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"),
    "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"),
    "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"),
    "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"),
    "970": ("Palestine", "🇵🇸"),
    "971": ("United Arab Emirates", "🇦🇪"),
    "972": ("Israel", "🇮🇱"),
    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"),
    "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"),
    "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
}


def get_country_info(number):
    digits = re.sub(r'\D', '', str(number))
    if not digits:
        return "Unknown", "🏳️"

    for prefix_length in (4, 3, 2, 1):
        prefix = digits[:prefix_length]
        if prefix in COUNTRY_CODES:
            return COUNTRY_CODES[prefix]

    return "Unknown", "🏳️"


def build_unique_id(item):
    return f"{item['dt']}|{item['num']}|{item['cli']}|{item['message']}"


def extract_otp(message):
    """মেসেজ থেকে ৪ থেকে ৮ ডিজিটের OTP কোড খুঁজে বের করার ফাংশন"""
    match = re.search(r'\b\d{4,8}\b', message)
    return match.group(0) if match else None


def send_to_telegram(item):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    country_name, country_flag = get_country_info(item['num'])
    msg_text = (
        "🔑 OTP RECEIVED!\n\n"
        f"🔢 Number: {item['num']}\n\n"
        f"🌍 Country: {country_flag} {country_name}\n\n"
        f"👤 Service: {item['cli']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    payload = {
        'chat_id': CHAT_ID, 
        'text': msg_text, 
        'parse_mode': 'Markdown'
    }

    # মেসেজ থেকে OTP বের করা
    otp_code = extract_otp(item['message'])
    full_sms_text = item['message']

    # ইনলাইন কিবোর্ডে দুইটি বাটনকে একই লাইনে রাখতে হবে
    inline_keyboard_buttons = []

    # ১. ওটিপি পাওয়া গেলে প্রথম বাটন (OTP Copy Button) যুক্ত হবে এবং সবুজ হবে
    if otp_code:
        inline_keyboard_buttons.append({
            "text": f"🔑 {otp_code}",  # বাটনটি একটু বড় ও পরিষ্কার দেখাবে
            "style": "success",                  # বাটনটি সবুজ (Green) কালার করবে
            "copy_text": {
                "text": otp_code                 # ক্লিক করলে শুধু ওটিপি কপি হবে
            }
        })

    # ২. পুরো এসএমএস কপি করার জন্য দ্বিতীয় বাটন (FULL SMS Button) যুক্ত হবে এবং সবুজ হবে
    if full_sms_text.strip():
        inline_keyboard_buttons.append({
            "text": "📋  FULL SMS",              # বাটনের নাম একটু বড় ও readable হবে
            "style": "success",                 # বাটনটি সবুজ (Green) কালার করবে
            "copy_text": {
                "text": full_sms_text           # ক্লিক করলে পুরো এসএমএস টেক্সট কপি হবে
            }
        })

    # যদি অন্তত একটি বাটনও তৈরি হয়, তবে তা একই লাইনে যুক্ত করা হবে
    if inline_keyboard_buttons:
        reply_markup = {"inline_keyboard": [inline_keyboard_buttons]}
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        requests.post(telegram_url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")


print("Bot is running. Checking every 3 seconds...")

while True:
    data = fetch_sms()

    if data and data.get("status") == "success":
        sms_list = data.get("data", [])

        if isinstance(sms_list, dict):
            sms_list = sms_list.get("items", []) or sms_list.get("data", [])

        if isinstance(sms_list, list):
            for item in sms_list:
                if not isinstance(item, dict):
                    continue

                normalized_item = normalize_item(item)
                if not normalized_item["message"].strip():
                    continue

                unique_id = build_unique_id(normalized_item)
                if unique_id not in sent_messages:
                    send_to_telegram(normalized_item)
                    sent_messages[unique_id] = True

        if len(sent_messages) > 2000:
            sent_messages = dict(list(sent_messages.items())[-1000:])

    time.sleep(3)
