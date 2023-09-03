import asyncio
import dotenv
import discord
from discord.ext import commands
import os

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

tasks = {}

bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.all()
)

@bot.command()
async def wait(ctx: commands.Context, duration: int):
    global tasks
    await ctx.send(f"starting wait timer of {duration} seconds.")
    tasks[ctx.author.id] = asyncio.create_task(asyncio.sleep(duration))
    try:
        await tasks[ctx.author.id]
        await ctx.send("Success")
    except asyncio.CancelledError:
        await ctx.send("Cancelled")

@bot.command()
async def cancel(ctx: commands.Context):
    global tasks
    if ctx.author.id in tasks.keys():
        tasks[ctx.author.id].cancel()

@bot.event
async def on_ready():
    print("Bot is connected to discord services.")

if __name__ == '__main__':
    bot.run(TOKEN)