import discord
from discord.ext import commands, tasks
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

voice_client = None
last_channel = None

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    auto_reconnect.start()

@bot.command()
async def join(ctx):
    global voice_client, last_channel

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        last_channel = channel

        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
            voice_client = ctx.voice_client
        else:
            voice_client = await channel.connect()

        play_sound.start()
        await ctx.send("Connecté 🔊")
    else:
        await ctx.send("Va dans un vocal")

@bot.command()
async def leave(ctx):
    global voice_client

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        play_sound.stop()

@tasks.loop(hours=24)
async def play_sound():
    global voice_client

    if voice_client and voice_client.is_connected():
        if not voice_client.is_playing():
            source = discord.FFmpegPCMAudio("pet.mp3")
            voice_client.play(source)

@play_sound.before_loop
async def before_play():
    await bot.wait_until_ready()
    await asyncio.sleep(5)

@tasks.loop(seconds=30)
async def auto_reconnect():
    global voice_client, last_channel

    if last_channel:
        if not voice_client or not voice_client.is_connected():
            try:
                voice_client = await last_channel.connect()
            except:
                pass

bot.run(TOKEN)
