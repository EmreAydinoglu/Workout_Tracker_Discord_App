import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx):
    from cogs.base_exercise import HelpView
    view = HelpView(bot)
    view.update_buttons()
    await ctx.send(embed=view.build_embed(), view=view)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_') and not filename.startswith('base_'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'✅ Loaded cog: {filename}')

@bot.event
async def on_ready():
    await load_cogs()
    print(f'🤖 {bot.user.name} is online and ready!')

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN not found in .env file!")