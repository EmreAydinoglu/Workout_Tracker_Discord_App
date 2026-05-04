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
    # Veritabanı işlemleri (Aynı kalıyor)
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    bugun = date.today().strftime("%d/%m/%Y")
    cursor.execute("INSERT INTO pullups (user_id, count, date) VALUES (?, ?, ?)", 
                   (str(ctx.author.id), sayi, bugun))
    conn.commit()
    conn.close()

    # Profesyonel Embed Tasarımı
    embed = discord.Embed(
        title="💪 Antrenman Başarıyla Kaydedildi!",
        description=f"Harika bir set çıkardın, **{ctx.author.name}**!",
        color=0xff0000 # Kaguya Kırmızısı
    )
    
    embed.add_field(name="Çekilen Barfiks", value=f"**{sayi}**", inline=True)
    
    hedef = 20 # Senin o meşhur hedefin
    if sayi >= hedef:
        embed.add_field(name="Durum", value="🏆 **HEDEF TAMAMLANDI!**", inline=False)
        embed.set_footer(text="Mükemmel disiplin! Kaguya seninle gurur duyuyor.")
    else:
        kalan = hedef - sayi
        embed.add_field(name="Hedefe Kalan", value=f"**{kalan}** barfiks daha!", inline=True)
        embed.set_footer(text="Gelişmeye devam et, pes etmek yok!")

    await ctx.send(embed=embed)

@bot.command()
async def gecmis(ctx):
    # Veritabanına bağlan
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    
    # SQL Sorgusu: Sadece bu kullanıcının verilerini al, son eklenenden geriye doğru 5 tanesini getir
    cursor.execute('''
        SELECT date, count FROM pullups 
        WHERE user_id = ? git
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
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ **Hata:** Dostum, barfiks sayısını sayı olarak girmelisin! Örn: `!kaydet 10`")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❓ **Eksik Bilgi:** Kaç barfiks çektin? Sayı girmeyi unuttun sanırım. Örn: `!kaydet 5`")
    else:
        print(f"Sistemde bir hata oluştu: {error}")

@bot.event
async def on_ready():
    print(f'Sistem aktif! {bot.user.name} olarak giriş yapıldı.')
    print('Barfiks demiri ve 20 pull-up hedefi bizi bekliyor!')

@bot.command()
async def selam(ctx):
    await ctx.send(f'Selam {ctx.author.name}! Bugün barfikste kaçtayız?')

if TOKEN:
    bot.run(TOKEN)
else:
    print("Hata: .env dosyasında DISCORD_TOKEN bulunamadı!")