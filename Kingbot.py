import os
import sys
import asyncio
import logging
import random
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl import functions, types
from telethon.tl.functions.channels import LeaveChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, SaveGifRequest
from telethon.tl.functions.account import UpdateProfileRequest
import telethon.utils

# Local imports
from Config import SESSIONS, SUDO, API_ID, API_HASH, SPAM_DELAY, BIGSPAM_DELAY, DEFAULT_JOIN_CHANNELS
from Utils import RAID, RRAID

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SMEX_USERS = list(SUDO)
QUE = {} # Queue for reply raid

# Clients list
clients = []

async def start_clients():
    if not API_ID or not API_HASH:
        logger.critical("API_ID and API_HASH must be set in environment variables!")
        return

    logger.info(f"Found {len(SESSIONS)} sessions.")
    for i, session in enumerate(SESSIONS, 1):
        try:
            logger.info(f"Booting Up Client {i}")
            client = TelegramClient(StringSession(session), API_ID, API_HASH)
            await client.start()
            
            # Join default channels (optional)
            for ch in DEFAULT_JOIN_CHANNELS:
                try:
                    await client(JoinChannelRequest(channel=ch))
                except Exception as e:
                    logger.warning(f"Client {i} failed to join channel {ch}: {e}")
            
            me = await client.get_me()
            bot_id = telethon.utils.get_peer_id(me)
            if bot_id not in SMEX_USERS:
                SMEX_USERS.append(bot_id)
            clients.append(client)
            logger.info(f"Client {i} started as {me.first_name} ({bot_id})")
        except Exception as e:
            logger.error(f"Failed to start client {i}: {e}")

async def gifspam(e, media):
    try:
        await e.client(
            SaveGifRequest(
                id=types.InputDocument(
                    id=media.document.id,
                    access_hash=media.document.access_hash,
                    file_reference=media.document.file_reference,
                ),
                unsave=True,
            )
        )
    except Exception:
        pass

# --- Event Handlers ---

async def bio_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Bio\n\nKullanım:\n.bio <metin>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        bio_text = args[1]
        msg = await e.reply("Biyografi değiştiriliyor...")
        try:
            await e.client(UpdateProfileRequest(about=bio_text))
            await msg.edit("Biyografi güncellendi")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def join_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Katıl\n\nKullanım:\n.join <kamu kanal/grup linki veya kullanıcı adı>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        channel = args[1]
        msg = await e.reply("Katılıyor...")
        try:
            await e.client(JoinChannelRequest(channel=channel))
            await msg.edit("Başarıyla katıldı")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def pjoin_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Özel Katıl\n\nKullanım:\n.pjoin <davet hash>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        hash_val = args[1]
        msg = await e.reply("Katılıyor...")
        try:
            await e.client(ImportChatInviteRequest(hash_val))
            await msg.edit("Başarıyla katıldı")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def leave_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Ayrıl\n\nKullanım:\n.leave <kanal/sohbet ID>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            chat_id = int(args[1])
            msg = await e.reply("Ayrılıyor...")
            await e.client(LeaveChannelRequest(chat_id))
            await msg.edit("Başarıyla ayrıldı")
        except ValueError:
            await e.reply("Geçersiz ID formatı.")
        except Exception as err:
            await e.reply(str(err))
    else:
        await e.reply(usage)

async def spam_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Spam\n\nKullanım:\n.spam <adet> <mesaj>\n.spam <adet>  (bir mesaja yanıtlayarak)\n\nAdet sayı olmalı."
    error = "Spam en fazla 100 adet için kullanılabilir. Daha fazla için .bigspam kullan."
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)
        
    args = e.text.split(maxsplit=1)
    # args[0] is command, args[1] is params
    if len(args) < 2:
        return await e.reply(usage)
        
    params = args[1].split(" ", 1)
    try:
        count = int(params[0])
    except ValueError:
        return await e.reply(usage)
        
    if count > 100:
        return await e.reply(error)

    reply_msg = await e.get_reply_message()
    
    # Case 1: .spam 10 Mesaj metni
    if len(params) == 2:
        message = params[1]
        for _ in range(count):
            await e.respond(message)
            await asyncio.sleep(SPAM_DELAY)
        
    # Case 2: .spam 10 (medyaya yanıt)
    elif reply_msg and reply_msg.media:
        for _ in range(count):
            sent = await e.client.send_file(e.chat_id, reply_msg, caption=reply_msg.text)
            await gifspam(e, sent)
            await asyncio.sleep(SPAM_DELAY)
            
    # Case 3: .spam 10 (metne yanıt)
    elif reply_msg and reply_msg.text:
        message = reply_msg.text
        for _ in range(count):
            await e.respond(message)
            await asyncio.sleep(SPAM_DELAY)
    else:
        await e.reply(usage)

async def delayspam_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: DelaySpam\n\nKullanım:\n.delayspam <bekleme> <adet> <mesaj>\n.delayspam <bekleme> <adet>  (yanıtla)"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)

    args = e.text.split(maxsplit=1)
    if len(args) < 2: return await e.reply(usage)
    
    params = args[1].split(" ", 2)
    # [sleep, count, message] veya [sleep, count]
    
    try:
        sleep_time = float(params[0])
        count = int(params[1])
    except (ValueError, IndexError):
        return await e.reply(usage)

    reply_msg = await e.get_reply_message()

    if len(params) == 3:
        message = params[2]
        for _ in range(count):
            async with e.client.action(e.chat_id, "typing"):
                if e.reply_to_msg_id:
                    await reply_msg.reply(message)
                else:
                    await e.client.send_message(e.chat_id, message)
                await asyncio.sleep(sleep_time)
                
    elif reply_msg and reply_msg.media:
        for _ in range(count):
            async with e.client.action(e.chat_id, "document"):
                sent = await e.client.send_file(e.chat_id, reply_msg, caption=reply_msg.text)
                await gifspam(e, sent)
            await asyncio.sleep(sleep_time)
            
    elif reply_msg and reply_msg.text:
        message = reply_msg.text
        for _ in range(count):
            async with e.client.action(e.chat_id, "typing"):
                await e.client.send_message(e.chat_id, message)
            await asyncio.sleep(sleep_time)
    else:
        await e.reply(usage)

async def bigspam_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: BigSpam\n\nKullanım:\n.bigspam <adet> <mesaj>\n.bigspam <adet>  (yanıtla)"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)

    args = e.text.split(maxsplit=1)
    if len(args) < 2: return await e.reply(usage)
    
    params = args[1].split(" ", 1)
    try:
        count = int(params[0])
    except ValueError:
        return await e.reply(usage)

    reply_msg = await e.get_reply_message()

    if len(params) == 2:
        message = params[1]
        for _ in range(count):
            async with e.client.action(e.chat_id, "typing"):
                if e.reply_to_msg_id:
                    await reply_msg.reply(message)
                else:
                    await e.client.send_message(e.chat_id, message)
            await asyncio.sleep(BIGSPAM_DELAY)
            
    elif reply_msg and reply_msg.media:
        for _ in range(count):
            async with e.client.action(e.chat_id, "document"):
                sent = await e.client.send_file(e.chat_id, reply_msg, caption=reply_msg.text)
                await gifspam(e, sent)
            await asyncio.sleep(BIGSPAM_DELAY)
            
    elif reply_msg and reply_msg.text:
        message = reply_msg.text
        for _ in range(count):
            async with e.client.action(e.chat_id, "typing"):
                await e.client.send_message(e.chat_id, message)
            await asyncio.sleep(BIGSPAM_DELAY)
    else:
        await e.reply(usage)

async def raid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Raid\n\nKullanım:\n.raid <adet> <kullanıcı>\n.raid <adet>  (yanıtla)"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)

    args = e.text.split(maxsplit=1)
    if len(args) < 2: return await e.reply(usage)
    
    params = args[1].split(" ", 1)
    try:
        count = int(params[0])
    except ValueError:
        return await e.reply(usage)

    reply_msg = await e.get_reply_message()

    if len(params) == 2:
        target_str = params[1]
        try:
            entity = await e.client.get_entity(target_str)
            user_link = f"[{entity.first_name}](tg://user?id={entity.id})"
            for _ in range(count):
                reply = random.choice(RAID)
                caption = f"{user_link} {reply}"
                async with e.client.action(e.chat_id, "typing"):
                    await e.client.send_message(e.chat_id, caption)
                    await asyncio.sleep(0.3)
        except Exception as err:
            await e.reply(f"Hata: {err}")
            
    elif reply_msg:
        try:
            entity = await e.client.get_entity(reply_msg.sender_id)
            user_link = f"[{entity.first_name}](tg://user?id={entity.id})"
            for _ in range(count):
                reply = random.choice(RAID)
                caption = f"{user_link} {reply}"
                async with e.client.action(e.chat_id, "typing"):
                    await e.client.send_message(e.chat_id, caption)
                    await asyncio.sleep(0.3)
        except Exception as err:
            await e.reply(f"Hata: {err}")
    else:
        await e.reply(usage)

async def replyraid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: ReplyRaid\n\nKullanım:\n.replyraid <kullanıcı>\n.replyraid  (yanıtla)"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)
        
    args = e.text.split(maxsplit=1)
    reply_msg = await e.get_reply_message()
    
    target_id = None
    
    if len(args) > 1:
        target_str = args[1]
        try:
            entity = await e.client.get_entity(target_str)
            target_id = entity.id
        except Exception:
            pass
    elif reply_msg:
        target_id = reply_msg.sender_id
        
    if target_id:
        if target_id not in QUE:
            QUE[target_id] = []
        QUE[target_id].append(target_id)
        await e.reply("Yanıt baskını açıldı")
    else:
        await e.reply(usage)

async def dreplyraid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: ReplyRaid Kapat\n\nKullanım:\n.dreplyraid <kullanıcı>\n.dreplyraid  (yanıtla)"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)
        
    args = e.text.split(maxsplit=1)
    reply_msg = await e.get_reply_message()
    
    target_id = None
    
    if len(args) > 1:
        target_str = args[1]
        try:
            entity = await e.client.get_entity(target_str)
            target_id = entity.id
        except Exception:
            pass
    elif reply_msg:
        target_id = reply_msg.sender_id
        
    if target_id and target_id in QUE:
        QUE.pop(target_id, None)
        await e.reply("Yanıt baskını kapatıldı")
    else:
        await e.reply(usage)

async def auto_reply_handler(e):
    if e.sender_id in QUE:
        async with e.client.action(e.chat_id, "typing"):
            await asyncio.sleep(0.3)
        async with e.client.action(e.chat_id, "typing"):
            await e.client.send_message(
                entity=e.chat_id,
                message=random.choice(RRAID),
                reply_to=e.message.id,
            )

async def ping_handler(e):
    if e.sender_id not in SMEX_USERS: return
    start = datetime.now()
    msg = await e.reply("Pong!")
    end = datetime.now()
    ms = (end-start).microseconds / 1000
    await msg.edit(f"🚀 𝗣𝗼𝗻𝗴!\n`{ms}` 𝗺𝘀")

async def restart_handler(e):
    if e.sender_id not in SMEX_USERS: return
    await e.reply("Yeniden başlatılıyor...\n\nLütfen tamamlanmasını bekleyin.")
    for client in clients:
        try:
            await client.disconnect()
        except Exception:
            pass
    os.execl(sys.executable, sys.executable, *sys.argv)

async def help_handler(e):
    if e.sender_id not in SMEX_USERS: return
    text = "⚡Komutlar⚡\n\nYardımcı:\n.ping\n.restart\n\nKullanıcı:\n.bio\n.join\n.pjoin\n.leave\n.clone\n\nModerasyon:\n.lockdown\n.unlockdown\n.purge <adet>\n\nSpam:\n.spam\n.delayspam\n.bigspam\n.raid\n.replyraid\n.dreplyraid"
    await e.reply(text)

async def clone_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Modül: Clone\n\nKullanım:\nBir kullanıcının mesajına yanıt verip .clone yaz."
    reply_msg = await e.get_reply_message()
    if not reply_msg:
        return await e.reply(usage)
    msg = await e.reply("Klonlanıyor...")
    try:
        entity = await e.client.get_entity(reply_msg.sender_id)
        full = await e.client(functions.users.GetFullUserRequest(entity))
        first = entity.first_name or ""
        last = entity.last_name or None
        about = getattr(full.full_user, "about", None)
        try:
            await e.client(UpdateProfileRequest(first_name=first, last_name=last, about=about))
        except Exception:
            await e.client(UpdateProfileRequest(first_name=first, last_name=last))
        try:
            photo_path = await e.client.download_profile_photo(entity, file="clone_pp.jpg")
            if photo_path:
                await e.client.upload_profile_photo(photo_path)
                try:
                    os.remove(photo_path)
                except Exception:
                    pass
        except Exception:
            pass
        await msg.edit("Klonlama tamamlandı.")
    except Exception as err:
        await msg.edit(f"Hata: {err}")

async def lockdown_handler(e):
    if e.sender_id not in SMEX_USERS: return
    msg = await e.reply("Sohbet kilitleniyor...")
    try:
        rights = types.ChatBannedRights(
            until_date=None,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_games=True,
            send_inline=True,
            embed_links=True,
            send_polls=True,
            change_info=False,
            invite_users=False,
            pin_messages=False,
        )
        try:
            await e.client(functions.channels.EditDefaultBannedRights(channel=e.chat_id, banned_rights=rights))
        except Exception:
            await e.client(functions.messages.EditChatDefaultBannedRights(peer=e.chat_id, banned_rights=rights))
        await msg.edit("Sohbet kilitlendi (mesaj gönderimi kapalı).")
    except Exception as err:
        await msg.edit(f"Hata: {err}")

async def unlockdown_handler(e):
    if e.sender_id not in SMEX_USERS: return
    msg = await e.reply("Sohbet açılıyor...")
    try:
        rights = types.ChatBannedRights(
            until_date=None,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_links=False,
            send_polls=False,
            change_info=False,
            invite_users=False,
            pin_messages=False,
        )
        try:
            await e.client(functions.channels.EditDefaultBannedRights(channel=e.chat_id, banned_rights=rights))
        except Exception:
            await e.client(functions.messages.EditChatDefaultBannedRights(peer=e.chat_id, banned_rights=rights))
        await msg.edit("Sohbet açıldı (mesaj gönderimi serbest).")
    except Exception as err:
        await msg.edit(f"Hata: {err}")

async def purge_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "Kullanım: .purge <adet>"
    args = e.text.split(maxsplit=1)
    if len(args) < 2:
        return await e.reply(usage)
    try:
        count = int(args[1])
    except ValueError:
        return await e.reply(usage)
    msg = await e.reply("Siliniyor...")
    try:
        msgs = await e.client.get_messages(e.chat_id, limit=count)
        await e.client.delete_messages(e.chat_id, [m.id for m in msgs])
        await msg.edit(f"{count} mesaj silindi.")
    except Exception as err:
        await msg.edit(f"Hata: {err}")

# --- Main Registration ---

def register_handlers():
    for client in clients:
        client.add_event_handler(bio_handler, events.NewMessage(pattern=r"\.bio"))
        client.add_event_handler(join_handler, events.NewMessage(pattern=r"\.join"))
        client.add_event_handler(pjoin_handler, events.NewMessage(pattern=r"\.pjoin"))
        client.add_event_handler(leave_handler, events.NewMessage(pattern=r"\.leave"))
        client.add_event_handler(spam_handler, events.NewMessage(pattern=r"\.spam"))
        client.add_event_handler(delayspam_handler, events.NewMessage(pattern=r"\.delayspam"))
        client.add_event_handler(bigspam_handler, events.NewMessage(pattern=r"\.bigspam"))
        client.add_event_handler(raid_handler, events.NewMessage(pattern=r"\.raid"))
        client.add_event_handler(replyraid_handler, events.NewMessage(pattern=r"\.replyraid"))
        client.add_event_handler(dreplyraid_handler, events.NewMessage(pattern=r"\.dreplyraid"))
        client.add_event_handler(ping_handler, events.NewMessage(pattern=r"\.ping"))
        client.add_event_handler(restart_handler, events.NewMessage(pattern=r"\.restart"))
        client.add_event_handler(help_handler, events.NewMessage(pattern=r"\.help"))
        client.add_event_handler(clone_handler, events.NewMessage(pattern=r"\.clone"))
        client.add_event_handler(lockdown_handler, events.NewMessage(pattern=r"\.lockdown"))
        client.add_event_handler(unlockdown_handler, events.NewMessage(pattern=r"\.unlockdown"))
        client.add_event_handler(purge_handler, events.NewMessage(pattern=r"\.purge"))
        
        # Auto reply handler (no pattern, just checks QUE)
        client.add_event_handler(auto_reply_handler, events.NewMessage(incoming=True))

async def main():
    await start_clients()
    if not clients:
        logger.error("No clients started. Please check your Config and environment variables.")
        return
    
    register_handlers()
    
    print("""
_______  _  _  _____  _ _  
/  _| _ \/ _ \ |  \/  || ___ \|  _  |_   _| 
\ --.| |_/ / /_\ \| .  . || |_/ /| | | | | |   
 --. \  __/|  _  || |\/| || _ \| | | | | |   
/\/ / |   | | | || |  | || |_/ /\ \_/ / | |   
\____/\_|   \_| |_/\_|  |_/\____/  \___/  \_/
""")
    print(f"Pawri💥! {len(clients)} Clients Deployed. SUPPORT - @KINGBOTOFFICIAL.")
    
    await asyncio.gather(*[c.run_until_disconnected() for c in clients])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

