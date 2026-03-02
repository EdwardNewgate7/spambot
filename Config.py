# Config.py
# Bu dosyayı kendi bilgilerinizle doldurun.
# .env dosyasına gerek yoktur, tüm ayarlar buradan yapılır.

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Config")

# ==============================================================================
# TELEGRAM API AYARLARI
# https://my.telegram.org adresinden alabilirsiniz.
# ==============================================================================

API_ID = "37323344"  # Buraya API ID'nizi yazın (Sayı olarak)
API_HASH = "4a12063a5c87a672d820d733bac0adca"  # Buraya API Hash'inizi yazın (Tırnak içinde)

# ==============================================================================
# YÖNETİCİ AYARLARI (SUDO)
# Botu kontrol edebilecek kullanıcıların ID'leri.
# Örnek: SUDO = [123456789, 987654321]
# ==============================================================================

SUDO = [
    # Buraya kendi Telegram ID'nizi ekleyin (Virgülle ayırarak birden fazla ekleyebilirsiniz)
    123456789
]

# ==============================================================================
# OTURUM AYARLARI (SESSIONS)
# String Session kodlarınızı buraya liste olarak ekleyin.
# Telethon veya Pyrogram string session'ları olabilir.
# ==============================================================================

SESSIONS = [
    # 1. Hesap
    "1BJWap1sBu6oO_eIJZFuDaheDkCI_VNPJRmM7Nq5HZx8KZo3EcjrlHeeM79Eos2c0MS0nGytwEfvZ-0Doi4gjtx_DT8FIPYSS5Co2RJq8talUPcHKkHX5N4lwiOS4Wo6ss1bh2f8Hp3vZg7nzmY9NHzxuwrnY4ZH6YKQz1XdyDbsLQt8zX5226Ux0rcQdVl9hkgGvydbJ8TNBeo_ZCqTNZhV7LAzHS8jq6VZigau5d5Qo3JJLmp66Ni-Iq8_sXSi2lTbWPL_7Vn9ux6SnNTsIdi9CR5MNVIv1XCjREwbVSQZNcVOpYRnZZllHx_i0LsOYZ28B4aaC-I881iHod1Q0NUKE2FntNb0=",
    
    # 2. Hesap (Varsa)
    # "STRING_SESSION_KODU_2_BURAYA",
    
    # 3. Hesap (Varsa)
    # "STRING_SESSION_KODU_3_BURAYA",
]

# ==============================================================================
# DİĞER AYARLAR
# ==============================================================================

# Botun biyografisi (İsteğe bağlı)
BIO_MESSAGE = "KingBot Spam Botu Tarafından Korunmaktadır."

# ==============================================================================
# KONTROLLER (Burası kodun çalışması içindir, değiştirmeyin)
# ==============================================================================

# Hız limitleri
SPAM_DELAY = 0.2
BIGSPAM_DELAY = 0.3

# Varsayılan katılınacak kanallar (boş bırakın)
DEFAULT_JOIN_CHANNELS = []

if not API_ID or not API_HASH:
    logger.warning("API_ID veya API_HASH eksik! Bot düzgün çalışmayabilir.")

if not SESSIONS:
    logger.warning("Hiçbir oturum (Session) bulunamadı! Lütfen SESSIONS listesine string kodlarınızı ekleyin.")

# Boş stringleri veya hatalı girişleri temizle
SESSIONS = [s for s in SESSIONS if s and not s.startswith("STRING_SESSION_KODU")]

