import os
import importlib.util
import logging
import requests
from telethon import TelegramClient, events
from config import API_ID, API_HASH, PHONE

# Настройка логов
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient('userbot_session', API_ID, API_HASH)
MODS_DIR = "modules"
active_mods = {}

def setup():
    os.makedirs(MODS_DIR, exist_ok=True)
    logger.info("Папка для модулей создана")

async def load_mod(mod_name: str):
    mod_path = os.path.join(MODS_DIR, f"{mod_name}.py")
    if not os.path.exists(mod_path):
        return False, "Файл модуля не найден"

    try:
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        active_mods[mod_name] = mod
        return True, f"✅ Модуль {mod_name} загружен"
    except Exception as e:
        return False, f"❌ Ошибка: {str(e)}"

@client.on(events.NewMessage(pattern=r'\.dlmod (.+?) (\w+)'))
async def dlmod_handler(event):
    url, mod_name = event.pattern_match.groups()
    try:
        response = requests.get(url)
        if response.status_code != 200:
            await event.reply("❌ Ошибка скачивания")
            return

        mod_path = os.path.join(MODS_DIR, f"{mod_name}.py")
        with open(mod_path, "wb") as f:
            f.write(response.content)
        await event.reply(f"✅ Модуль {mod_name} скачан")
        await load_mod(mod_name)
    except Exception as e:
        await event.reply(f"❌ Ошибка: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.loadmod (\w+)'))
async def loadmod_handler(event):
    mod_name = event.pattern_match.group(1)
    success, msg = await load_mod(mod_name)
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    await event.reply("🏓 Pong!")

@client.on(events.NewMessage)
async def message_handler(event):
    for mod in active_mods.values():
        if hasattr(mod, 'handle_message'):
            try:
                await mod.handle_message(event)
            except Exception as e:
                logger.error(f"Ошибка в модуле: {str(e)}")

async def main():
    setup()
    await client.start(PHONE)
    logger.info("Юзербот запущен!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
