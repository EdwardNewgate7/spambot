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
    "1AZWarzQBu756O5RUXB_sei0ceUxLf7D5wnDgWrIcVRnc6ts-uqLN6gT5E6KzYtxC6zKHejzd1g3CmhAwQrNrHYzA_zO8VuEa_XaGxeEKhPQSffCuY4Pzqai-fpcFd4Gs1-QU9kx_JRPi9wLBixuVlwTzk_9jAQQhtTpGue7CGXagkuaN14kPwXFmEXUc7SautDiwP3rwNpNYL-tPazucbSU2qh0MXrBe-FU6tLhT29QjT-hbkpMt2TU_bIaFXdnHSWPyk2e66WEi2OaPCJu6_OsB3LS8fWuMBhwOKI-ZCgrPnNSpMFWdoUHk4BHQaOvIVaTq7BRbH6a71HRjsRX8hB1YV1Cpstg=",
    
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

