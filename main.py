import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta, date , time
from discord.ext import tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
raw_id = os.getenv('CHANNEL_ID')
KANAL_ID = int(raw_id) if raw_id else None

intents = discord.Intents.default()
intents.message_content = True

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
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    bugun = date.today().strftime("%d/%m/%Y")
    cursor.execute("INSERT INTO pullups (user_id, count, date) VALUES (?, ?, ?)", 
                   (str(ctx.author.id), sayi, bugun))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="💪 Antrenman Başarıyla Kaydedildi!",
        description=f"Harika bir set çıkardın, **{ctx.author.name}**!",
        color=0xff0000 
    )
    
    embed.add_field(name="Çekilen Barfiks", value=f"**{sayi}**", inline=True)
    
    hedef = 20 
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
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, count FROM pullups 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT 5
    ''', (str(ctx.author.id),))
    
    kayitlar = cursor.fetchall()
    conn.close()
    
    if not kayitlar:
        await ctx.send("Henüz bir kayıt bulamadım. Hemen demire asıl ve `!kaydet` ile ilk verini gir!")
        return
        
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
    if not hatirlatici.is_running():
        hatirlatici.start()
    print('Hatırlatıcı döngüsü başlatıldı!')

@tasks.loop(time=time(hour=18, minute=00))
async def hatirlatici():
    kanal = bot.get_channel(KANAL_ID)
    embed = discord.Embed(
    title="🔔 Günlük Disiplin Hatırlatıcısı",
    description="Hey **Emre**, barfiks demiri seni bekliyor! Bugün omuzlarındaki yükü hissetmeye hazır mısın?",
    color=0xff0000 # Kaguya Kırmızısı
    )
    if kanal:
        await kanal.send(embed=embed)
    else:
        print("Bir sorun ile karşılaşıldı")

bot.remove_command('help')
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 ByEmre's Fitness Toy | Komut Rehberi",
        description="Barfiks hedefine giden yolda asistanın burada! İşte kullanabileceğin komutlar:",
        color=0xff0000
    )

    embed.add_field(
        name="🏋️ Antrenman Komutları", 
        value="`!kaydet [sayı]` - Günlük barfiks setini kaydeder.\n"
              "`!gecmis` - Son 5 antrenmanını listeler.", 
        inline=False
    )

    embed.add_field(
        name="📊 Analiz ve İstatistik", 
        value="`!haftalik` - Son 7 gündeki toplam performansın.\n"
              "`!seri` - Kaç gündür aralıksız çalıştığını gösterir (🔥 Çok yakında!).", 
        inline=False
    )

    embed.add_field(
        name="⚙️ Genel", 
        value="`!help` - Bu menüyü açar.\n",
        inline=False
    )

    embed.set_footer(text="Haliç Üniversitesi Mühendislik Disipliniyle Geliştirildi. 💪")
    embed.set_thumbnail(url=bot.user.avatar.url)

    await ctx.send(embed=embed)   

@bot.command()
async def haftalik(ctx):
    conn = sqlite3.connect('fitness_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, count FROM pullups WHERE user_id = ?", (str(ctx.author.id),))
    kayitlar = cursor.fetchall()
    conn.close()
    
    toplam = 0
    bugun = datetime.now()
    
    for tarih_str, miktar in kayitlar:
        try:
            kayit_tarihi = datetime.strptime(tarih_str, "%d/%m/%Y")
            if (bugun - kayit_tarihi).days <= 7:
                toplam += miktar
        except ValueError:
            continue 
            
    embed = discord.Embed(
        title="📈 Haftalık Performans Raporu",
        description=f"Son 7 günde toplam **{toplam}** barfiks çektin!",
        color=0x3498db 
    )
    
    if toplam > 0:
        embed.set_footer(text="İyi gidiyorsun, demire asılmaya devam!")
    else:
        embed.set_footer(text="Bu hafta henüz kayıt girmemişsin!")
        
    await ctx.send(embed=embed)

if TOKEN:
    bot.run(TOKEN)
else:
    print("Hata: .env dosyasında DISCORD_TOKEN bulunamadı!")