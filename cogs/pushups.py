from .base_exercise import BaseExercise
from discord.ext import commands
import discord


class Pushups(BaseExercise):
    EXERCISE_LABEL = "Şınav"
    THEME_COLOR = 0x00BFFF  # Electric Blue

    def __init__(self, bot):
        super().__init__(bot, exercise_type='pushup', daily_target=50)

    # ------------------------------------------------------------------ #
    #  Commands                                                            #
    # ------------------------------------------------------------------ #

    @commands.command(name='sinav_kaydet')
    async def kaydet(self, ctx, sayi: int):
        self.save_entry(str(ctx.author.id), sayi)
        embed = discord.Embed(
            title="💥 Şınav Kaydedildi!",
            description=f"Göğsünü yere değdirdin, **{ctx.author.name}**!",
            color=self.THEME_COLOR
        )
        embed.add_field(name="Çekilen Şınav", value=f"**{sayi}**", inline=True)
        if sayi >= self.daily_target:
            embed.add_field(name="Durum", value="🏆 **HEDEF TAMAMLANDI!**", inline=False)
            embed.set_footer(text="Pektoral kasların ateş püskürüyor!")
        else:
            embed.add_field(name="Hedefe Kalan", value=f"**{self.daily_target - sayi}** şınav daha!", inline=True)
            embed.set_footer(text="Göğsünü yere, hedefini gökyüzüne!")
        await ctx.send(embed=embed)

    @commands.command(name='sinav_sil')
    async def sil(self, ctx, kayit_id: int):
        if self.delete_by_id(str(ctx.author.id), kayit_id):
            await ctx.send(f"✅ `{kayit_id}` ID'li şınav kaydı silindi.")
        else:
            await ctx.send("❌ Kayıt bulunamadı veya bu kaydı silme yetkin yok!")

    @commands.command(name='sinav_sonusil')
    async def sonusil(self, ctx):
        deleted_id = self.delete_last(str(ctx.author.id))
        if deleted_id:
            await ctx.send(f"✅ Son şınav kaydın (ID: `{deleted_id}`) silindi.")
        else:
            await ctx.send("Silinecek bir kayıt bulunamadı.")

    @commands.command(name='sinav_gecmis')
    async def gecmis(self, ctx):
        kayitlar = self.get_history(str(ctx.author.id), limit=5)
        if not kayitlar:
            await ctx.send("Henüz şınav kaydın yok. `!sinav_kaydet` ile başla!")
            return
        mesaj = "📊 **Son Şınav Antrenmanların:**\n\n"
        for kayit_id, tarih, miktar in kayitlar:
            mesaj += f"🆔 `{kayit_id}` | 📅 {tarih} ➡️ **{miktar} Şınav**\n"
        await ctx.send(mesaj)

    @commands.command(name='sinav_haftalik')
    async def haftalik(self, ctx):
        toplam = self.get_weekly_total(str(ctx.author.id))
        embed = discord.Embed(
            title="📈 Haftalık Şınav Raporu",
            description=f"Son 7 günde toplam **{toplam}** şınav çektin!",
            color=self.THEME_COLOR
        )
        embed.set_footer(text="Her şınav bir adım daha güçlü!" if toplam > 0 else "Bu hafta henüz kayıt yok!")
        await ctx.send(embed=embed)

    @commands.command(name='sinav_rekor')
    async def rekor(self, ctx):
        best = self.get_record(str(ctx.author.id))
        if best is not None:
            await ctx.send(f"🏆 Şınav rekoru: **{best}** tekrar!")
        else:
            await ctx.send("Henüz bir kaydın yok.")

    @commands.command(name='sinav_seri')
    async def seri(self, ctx):
        streak = self.get_streak(str(ctx.author.id))
        embed = discord.Embed(title="🔥 Şınav Serisi", color=self.THEME_COLOR)
        if streak >= 5:
            embed.description = f"**Efsane irade!** Tam **{streak}** gündür şınavdan vazgeçmedin."
        elif streak > 0:
            embed.description = f"**{streak}** günlük aktif şınav serin var. Devam et!"
        else:
            embed.description = "Seri bozulmuş. Bugün yeniden ateşle! 💥"
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Pushups(bot))
