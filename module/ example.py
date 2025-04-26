async def handle_message(event):
    if "привет" in event.text.lower():
        await event.reply("👋 Привет от модуля!")
