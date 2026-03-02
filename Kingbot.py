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
from Config import SESSIONS, SUDO, API_ID, API_HASH
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
            
            # Join default channels
            try:
                await client(JoinChannelRequest(channel="@KINGBOTOFFICIAL"))
                await client(JoinChannelRequest(channel="@KINGBOTOFFICIALCHAT"))
            except Exception as e:
                logger.warning(f"Client {i} failed to join channel: {e}")
            
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
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗕𝗶𝗼\n\nCommand:\n\n.bio <Message>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        bio_text = args[1]
        msg = await e.reply("Changing Bio...")
        try:
            await e.client(UpdateProfileRequest(about=bio_text))
            await msg.edit("Succesfully Changed Bio")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def join_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗝𝗼𝗶𝗻\n\nCommand:\n\n.join <Public Channel/Group Link/Username>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        channel = args[1]
        msg = await e.reply("Joining...")
        try:
            await e.client(JoinChannelRequest(channel=channel))
            await msg.edit("Succesfully Joined")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def pjoin_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗝𝗼𝗶𝗻\n\nCommand:\n\n.pjoin <Hash>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        hash_val = args[1]
        msg = await e.reply("Joining...")
        try:
            await e.client(ImportChatInviteRequest(hash_val))
            await msg.edit("Succesfully Joined")
        except Exception as err:
            await msg.edit(str(err))
    else:
        await e.reply(usage)

async def leave_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗟𝗲𝗮𝘃𝗲\n\nCommand:\n\n.leave <Channel/Chat ID>"
    args = e.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            chat_id = int(args[1])
            msg = await e.reply("Leaving...")
            await e.client(LeaveChannelRequest(chat_id))
            await msg.edit("Succesfully Left")
        except ValueError:
            await e.reply("Invalid ID format.")
        except Exception as err:
            await e.reply(str(err))
    else:
        await e.reply(usage)

async def spam_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗦𝗽𝗮𝗺\n\nCommand:\n\n.spam <count> <message>\n.spam <count> <reply>\n\nCount must be an integer."
    error = "Spam Module can only be used till 100 count. For bigger spams use BigSpam."
    
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
    
    # Case 1: .spam 10 Message text
    if len(params) == 2:
        message = params[1]
        await asyncio.wait([e.respond(message) for _ in range(count)])
        
    # Case 2: .spam 10 (reply to media)
    elif reply_msg and reply_msg.media:
        for _ in range(count):
            sent = await e.client.send_file(e.chat_id, reply_msg, caption=reply_msg.text)
            await gifspam(e, sent)
            
    # Case 3: .spam 10 (reply to text)
    elif reply_msg and reply_msg.text:
        message = reply_msg.text
        await asyncio.wait([e.respond(message) for _ in range(count)])
    else:
        await e.reply(usage)

async def delayspam_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗗𝗲𝗹𝗮𝘆𝗦𝗽𝗮𝗺\n\nCommand:\n.delayspam <sleep> <count> <message>\n.delayspam <sleep> <count> <reply>"
    
    if e.text[0].isalpha() and e.text[0] in ("/", "#", "@", "!"):
        return await e.reply(usage)

    args = e.text.split(maxsplit=1)
    if len(args) < 2: return await e.reply(usage)
    
    params = args[1].split(" ", 2)
    # params structure: [sleep, count, message] or [sleep, count] (if reply)
    
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
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗕𝗶𝗴𝗦𝗽𝗮𝗺\n\nCommand:\n.bigspam <count> <message>\n.bigspam <count> <reply>"
    
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
            await asyncio.sleep(0.3)
            
    elif reply_msg and reply_msg.media:
        for _ in range(count):
            async with e.client.action(e.chat_id, "document"):
                sent = await e.client.send_file(e.chat_id, reply_msg, caption=reply_msg.text)
                await gifspam(e, sent)
            await asyncio.sleep(0.3)
            
    elif reply_msg and reply_msg.text:
        message = reply_msg.text
        for _ in range(count):
            async with e.client.action(e.chat_id, "typing"):
                await e.client.send_message(e.chat_id, message)
            await asyncio.sleep(0.3)
    else:
        await e.reply(usage)

async def raid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗥𝗮𝗶𝗱\n\nCommand:\n.raid <count> <Username>\n.raid <count> <reply>"
    
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
            await e.reply(f"Error: {err}")
            
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
            await e.reply(f"Error: {err}")
    else:
        await e.reply(usage)

async def replyraid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗥𝗲𝗽𝗹𝘆𝗥𝗮𝗶𝗱\n\nCommand:\n.replyraid <Username>\n.replyraid <reply>"
    
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
        await e.reply("Activated Reply Raid")
    else:
        await e.reply(usage)

async def dreplyraid_handler(e):
    if e.sender_id not in SMEX_USERS: return
    usage = "𝗠𝗼𝗱𝘂𝗹𝗲 𝗡𝗮𝗺𝗲 = 𝗗𝗲𝗮𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗥𝗲𝗽𝗹𝘆𝗥𝗮𝗶𝗱\n\nCommand:\n.dreplyraid <Username>\n.dreplyraid <reply>"
    
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
        await e.reply("De-Activated Reply Raid")
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
    await e.reply("𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙\n\nPlease wait till it reboots...")
    for client in clients:
        try:
            await client.disconnect()
        except Exception:
            pass
    os.execl(sys.executable, sys.executable, *sys.argv)

async def help_handler(e):
    if e.sender_id not in SMEX_USERS: return
    text = "⚡𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀⚡\n\n𝙐𝙩𝙞𝙡𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙:\n.ping\n.restart\n\n𝙐𝙨𝙚𝙧𝙗𝙤𝙩 𝘾𝙤𝙢𝙢𝙖𝙣𝙙:\n.bio\n.join\n.pjoin\n.leave\n\n𝙎𝙥𝙖𝙢 𝘾𝙤𝙢𝙢𝙖𝙣𝙙:\n.spam\n.delayspam\n.bigspam\n.raid\n.replyraid\n.dreplyraid"
    await e.reply(text)

# --- Main Registration ---

def register_handlers():
    for client in clients:
        client.add_event_handler(bio_handler, events.NewMessage(incoming=True, pattern=r"\.bio"))
        client.add_event_handler(join_handler, events.NewMessage(incoming=True, pattern=r"\.join"))
        client.add_event_handler(pjoin_handler, events.NewMessage(incoming=True, pattern=r"\.pjoin"))
        client.add_event_handler(leave_handler, events.NewMessage(incoming=True, pattern=r"\.leave"))
        client.add_event_handler(spam_handler, events.NewMessage(incoming=True, pattern=r"\.spam"))
        client.add_event_handler(delayspam_handler, events.NewMessage(incoming=True, pattern=r"\.delayspam"))
        client.add_event_handler(bigspam_handler, events.NewMessage(incoming=True, pattern=r"\.bigspam"))
        client.add_event_handler(raid_handler, events.NewMessage(incoming=True, pattern=r"\.raid"))
        client.add_event_handler(replyraid_handler, events.NewMessage(incoming=True, pattern=r"\.replyraid"))
        client.add_event_handler(dreplyraid_handler, events.NewMessage(incoming=True, pattern=r"\.dreplyraid"))
        client.add_event_handler(ping_handler, events.NewMessage(incoming=True, pattern=r"\.ping"))
        client.add_event_handler(restart_handler, events.NewMessage(incoming=True, pattern=r"\.restart"))
        client.add_event_handler(help_handler, events.NewMessage(incoming=True, pattern=r"\.help"))
        
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
