import discord
from discord.ext import commands


async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

async def on_message(message):
    if message.author.bot:
        return

def setup_events(bot_instance):
    global bot
    bot = bot_instance
    
    print("[+] Setting up event handlers...")
    bot_instance.add_listener(on_ready)
    bot_instance.add_listener(on_message, 'on_message')
    print("[+] Event handlers registered")