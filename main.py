import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
from datetime import date

# .env dosyasındaki DISCORD_TOKEN değişkenini sisteme yükler
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Botun mesajları okuyabilmesi için gerekli izinler (Intents)
intents = discord.Intents.default()
intents.message_content = True

# Botun komut ön ekini ve izinlerini tanımlıyoruz
bot = commands.Bot(command_prefix='!', intents=intents)

def db_setup():
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pullups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            count INTEGER,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

db_setup()

@bot.event
async def on_ready():
    # Bot çevrimiçi olduğunda terminalde bu mesajı göreceksin
    print(f'Sistem aktif! {bot.user.name} olarak giriş yapıldı.')
    print('Barfiks demiri ve 20 pull-up hedefi bizi bekliyor!')

@bot.command()
async def selam(ctx):
    # !selam komutu verildiğinde botun vereceği cevap
    await ctx.send(f'Selam {ctx.author.name}! Bugün barfikste kaçtayız?')

# Botu çalıştıran ana fonksiyon
if TOKEN:
    bot.run(TOKEN)
else:
    print("Hata: .env dosyasında DISCORD_TOKEN bulunamadı!")