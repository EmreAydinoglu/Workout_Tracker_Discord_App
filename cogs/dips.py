from .base_exercise import BaseExercise
from discord.ext import commands
import discord


class Dips(BaseExercise):
    EXERCISE_LABEL = "Dip"
    THEME_COLOR = 0x9B59B6  # Royal Purple

    def __init__(self, bot):
        super().__init__(bot, exercise_type='dip', daily_target=30)

    @commands.command(name='dip_kaydet')
    async def kaydet(self, ctx, sayi: int):
        self.save_entry(str(ctx.author.id), sayi)
        embed = discord.Embed(
            title="🔱 Dip Kaydedildi!",
            description=f"Paralel barları fethettin, **{ctx.author.name}**!",
            color=self.THEME_COLOR
        )
        embed.add_field(name="Yapılan Dip", value=f"**{sayi}**", inline=True)
        if sayi >= self.daily_target:
            embed.add_field(name="Durum", value="🏆 **HEDEF TAMAMLANDI!**", inline=False)
            embed.set_footer(text="Trisepsler çelik gibi! Kaguya onayladı.")
        else:
            embed.add_field(name="Hedefe Kalan", value=f"**{self.daily_target - sayi}** dip daha!", inline=True)
            embed.set_footer(text="Aşağı in, yukarı çık, büyü!")
        await ctx.send(embed=embed)

    @commands.command(name='dip_sil')
    async def sil(self, ctx, kayit_id: int):
        if self.delete_by_id(str(ctx.author.id), kayit_id):
            await ctx.send(f"✅ `{kayit_id}` ID'li dip kaydı silindi.")
        else:
            await ctx.send("❌ Kayıt bulunamadı veya bu kaydı silme yetkin yok!")

    @commands.command(name='dip_sonusil')
    async def sonusil(self, ctx):
        deleted_id = self.delete_last(str(ctx.author.id))
        if deleted_id:
            await ctx.send(f"✅ Son dip kaydın (ID: `{deleted_id}`) silindi.")
        else:
            await ctx.send("Silinecek bir kayıt bulunamadı.")

    @commands.command(name='dip_gecmis')
    async def gecmis(self, ctx):
        kayitlar = self.get_history(str(ctx.author.id), limit=5)
        if not kayitlar:
            await ctx.send("Henüz dip kaydın yok. `!dip_kaydet` ile başla!")
            return
        mesaj = "📊 **Son Dip Antrenmanların:**\n\n"
        for kayit_id, tarih, miktar in kayitlar:
            mesaj += f"🆔 `{kayit_id}` | 📅 {tarih} ➡️ **{miktar} Dip**\n"
        await ctx.send(mesaj)

    @commands.command(name='dip_haftalik')
    async def haftalik(self, ctx):
        toplam = self.get_weekly_total(str(ctx.author.id))
        embed = discord.Embed(
            title="📈 Haftalık Dip Raporu",
            description=f"Son 7 günde toplam **{toplam}** dip yaptın!",
            color=self.THEME_COLOR
        )
        embed.set_footer(text="Trisepsler büyüyor!" if toplam > 0 else "Bu hafta henüz kayıt yok!")
        await ctx.send(embed=embed)

    @commands.command(name='dip_rekor')
    async def rekor(self, ctx):
        best = self.get_record(str(ctx.author.id))
        if best is not None:
            await ctx.send(f"🏆 Dip rekoru: **{best}** tekrar!")
        else:
            await ctx.send("Henüz bir kaydın yok.")

    @commands.command(name='dip_seri')
    async def seri(self, ctx):
        streak = self.get_streak(str(ctx.author.id))
        embed = discord.Embed(title="🔥 Dip Serisi", color=self.THEME_COLOR)
        if streak >= 5:
            embed.description = f"**Paralel bar ustası!** Tam **{streak}** gündür dip serisini sürdürüyorsun."
        elif streak > 0:
            embed.description = f"**{streak}** günlük aktif dip serin var. Trisepsler teşekkür eder!"
        else:
            embed.description = "Seri bozulmuş. Paralel bara geri dön! 🔱"
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Dips(bot))