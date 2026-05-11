import io
import discord
import matplotlib.pyplot as plt
from discord.ext import commands, tasks
from datetime import time
import os

from .base_exercise import BaseExercise


class Pullups(BaseExercise):
    """
    Pull-up tracking cog.
    Inherits all DB/CRUD logic and help command from BaseExercise.
    """

    EXERCISE_LABEL = "Barfiks"
    THEME_COLOR = 0xFF0000

    def __init__(self, bot):
        super().__init__(bot, exercise_type='pullup', daily_target=20)
        self.kanal_id = int(os.getenv('CHANNEL_ID', 0))

    # ------------------------------------------------------------------ #
    #  Commands                                                            #
    # ------------------------------------------------------------------ #

    @commands.command()
    async def kaydet(self, ctx, sayi: int):
        self.save_entry(str(ctx.author.id), sayi)
        embed = discord.Embed(
            title="💪 Antrenman Başarıyla Kaydedildi!",
            description=f"Harika bir set çıkardın, **{ctx.author.name}**!",
            color=self.THEME_COLOR
        )
        embed.add_field(name=f"Çekilen {self.EXERCISE_LABEL}", value=f"**{sayi}**", inline=True)
        if sayi >= self.daily_target:
            embed.add_field(name="Durum", value="🏆 **HEDEF TAMAMLANDI!**", inline=False)
            embed.set_footer(text="Mükemmel disiplin! Kaguya seninle gurur duyuyor.")
        else:
            embed.add_field(name="Hedefe Kalan", value=f"**{self.daily_target - sayi}** {self.EXERCISE_LABEL.lower()} daha!", inline=True)
            embed.set_footer(text="Gelişmeye devam et, pes etmek yok!")
        await ctx.send(embed=embed)

    @commands.command()
    async def sil(self, ctx, kayit_id: int):
        if self.delete_by_id(str(ctx.author.id), kayit_id):
            await ctx.send(f"✅ `{kayit_id}` ID'li antrenman kaydı başarıyla imha edildi.")
        else:
            await ctx.send("❌ Hata: Kayıt bulunamadı veya bu kaydı silme yetkin yok!")

    @commands.command()
    async def sonusil(self, ctx):
        deleted_id = self.delete_last(str(ctx.author.id))
        if deleted_id:
            await ctx.send(f"✅ En son girdiğin antrenman kaydı (ID: `{deleted_id}`) başarıyla silindi.")
        else:
            await ctx.send("Silinecek bir kayıt bulunamadı.")

    @commands.command()
    async def gecmis(self, ctx):
        kayitlar = self.get_history(str(ctx.author.id), limit=5)
        if not kayitlar:
            await ctx.send("Henüz bir kayıt bulamadım. Hemen demire asıl ve `!kaydet` ile ilk verini gir!")
            return
        mesaj = "📊 **İşte Son Antrenmanların:**\n\n"
        for kayit_id, tarih, miktar in kayitlar:
            mesaj += f"🆔 `{kayit_id}` | 📅 {tarih} ➡️ **{miktar} {self.EXERCISE_LABEL}**\n"
        await ctx.send(mesaj)

    @commands.command()
    async def haftalik(self, ctx):
        toplam = self.get_weekly_total(str(ctx.author.id))
        embed = discord.Embed(
            title="📈 Haftalık Performans Raporu",
            description=f"Son 7 günde toplam **{toplam}** {self.EXERCISE_LABEL.lower()} çektin!",
            color=0x3498DB
        )
        embed.set_footer(text="İyi gidiyorsun, demire asılmaya devam!" if toplam > 0 else "Bu hafta henüz kayıt girmemişsin!")
        await ctx.send(embed=embed)

    @commands.command()
    async def rekor(self, ctx):
        best = self.get_record(str(ctx.author.id))
        if best is not None:
            await ctx.send(f"🏆 Kişisel rekorun: **{best}** {self.EXERCISE_LABEL.lower()}!")
        else:
            await ctx.send("Henüz bir kaydın yok.")

    @commands.command()
    async def seri(self, ctx):
        streak = self.get_streak(str(ctx.author.id))
        embed = discord.Embed(title="🔥 Disiplin Serisi", color=self.THEME_COLOR)
        if streak >= 5:
            embed.description = f"**Muazzam bir irade!** Tam **{streak}** gündür zinciri kırmadın."
        elif streak > 0:
            embed.description = f"Harika gidiyorsun! **{streak}** günlük bir serin var."
        else:
            embed.description = "Seri şu an bozulmuş görünüyor. Bugün yeniden başla! 💪"
        embed.set_footer(text="Haliç Üniversitesi Mühendislik Disiplini 🎓")
        await ctx.send(embed=embed)

    @commands.command()
    async def grafik(self, ctx):
        kayitlar = self.get_history(str(ctx.author.id), limit=7)
        if not kayitlar:
            await ctx.send("Grafik oluşturmak için henüz yeterli verin yok!")
            return
        gunler  = [row[1] for row in reversed(kayitlar)]
        sayilar = [row[2] for row in reversed(kayitlar)]
        plt.figure(figsize=(10, 5))
        plt.plot(gunler, sayilar, color='red', marker='o', linestyle='-', linewidth=2, markersize=8)
        plt.title(f'{self.EXERCISE_LABEL} Gelişim Grafiği - {ctx.author.name}', fontsize=14, fontweight='bold')
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel(f'{self.EXERCISE_LABEL} Sayısı', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.ylim(0, max(sayilar) + 5)
        with io.BytesIO() as buf:
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            await ctx.send(
                content=f"📈 **{ctx.author.name}**, işte son {len(kayitlar)} antrenmanındaki performansın:",
                file=discord.File(fp=buf, filename='gelisim_grafigi.png')
            )
        plt.close()

    # ------------------------------------------------------------------ #
    #  Scheduled Reminder                                                  #
    # ------------------------------------------------------------------ #

    @tasks.loop(time=time(hour=18, minute=0))
    async def hatirlatici(self):
        kanal = self.bot.get_channel(self.kanal_id)
        if kanal:
            embed = discord.Embed(
                title="🔔 Günlük Disiplin Hatırlatıcısı",
                description="Hey **Emre**, barfiks demiri seni bekliyor! Bugün omuzlarındaki yükü hissetmeye hazır mısın?",
                color=self.THEME_COLOR
            )
            await kanal.send(embed=embed)
        else:
            print("[WARN] Reminder channel not found.")

    @hatirlatici.before_loop
    async def before_hatirlatici(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        if not self.hatirlatici.is_running():
            self.hatirlatici.start()
        print("✅ Pullups cog loaded and reminder started.")


async def setup(bot):
    await bot.add_cog(Pullups(bot))
