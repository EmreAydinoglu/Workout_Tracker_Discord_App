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

@bot.command()
async def kaydet(ctx, sayi: int):
    # Veritabanına bağlanıyoruz
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    
    # Bugünün tarihini gün/ay/yıl formatında alıyoruz
    bugun = date.today().strftime("%d/%m/%Y")
    
    # SQL ile veriyi tabloya yerleştiriyoruz
    cursor.execute("INSERT INTO pullups (user_id, count, date) VALUES (?, ?, ?)", 
                   (str(ctx.author.id), sayi, bugun))
    
    conn.commit()
    conn.close()
    
    hedef = 20 # Senin o meşhur 20 barfiks hedefin
    if sayi >= hedef:
        await ctx.send(f"ŞAKA MI? {sayi} barfiks! 20 hedefini vurdun, Kaguya seninle gurur duyuyor! 🏆")
    else:
        kalan = hedef - sayi
        await ctx.send(f"Kaydedildi! {sayi} barfiks cebinde. Hedef 20, kaldı {kalan}. Zorla o demiri! 💪")

@bot.command()
async def gecmis(ctx):
    # Veritabanına bağlan
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    
    # SQL Sorgusu: Sadece bu kullanıcının verilerini al, son eklenenden geriye doğru 5 tanesini getir
    cursor.execute('''
        SELECT date, count FROM pullups 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT 5
    ''', (str(ctx.author.id),))
    
    # Bulunan tüm sonuçları bir listeye çek
    kayitlar = cursor.fetchall()
    conn.close()
    
    # Eğer listede hiç kayıt yoksa
    if not kayitlar:
        await ctx.send("Henüz bir kayıt bulamadım. Hemen demire asıl ve `!kaydet` ile ilk verini gir!")
        return
        
    # Kayıtlar varsa şık bir mesaj oluştur
    mesaj = f"📊 **İşte Son Antrenmanların:**\n\n"
    for tarih, miktar in kayitlar:
        mesaj += f"📅 {tarih} ➡️ **{miktar} Barfiks**\n"
        
    await ctx.send(mesaj)

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