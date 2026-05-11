import sqlite3
from datetime import datetime, timedelta, date
import discord
from discord.ext import commands


# ------------------------------------------------------------------ #
#  Help UI - Tüm egzersizler tarafından kullanılır                   #
# ------------------------------------------------------------------ #

HELP_PAGES = [
    {
        "title": "📜 Ana Menü | ByEmre's Fitness Toy",
        "description": "Aşağıdan bir modül seç:",
        "color": 0xFF0000,
        "fields": [
            ("🏋️ Barfiks", "`!kaydet` `!gecmis` `!sonusil` `!sil` `!haftalik` `!seri` `!rekor` `!grafik`"),
            ("💥 Şınav",   "`!sinav_kaydet` `!sinav_gecmis` `!sinav_sonusil` `!sinav_sil` `!sinav_haftalik` `!sinav_seri` `!sinav_rekor`"),
            ("🔱 Dip",     "`!dip_kaydet` `!dip_gecmis` `!dip_sonusil` `!dip_sil` `!dip_haftalik` `!dip_seri` `!dip_rekor`"),
        ]
    },
    {
        "title": "🏋️ Barfiks Modülü | Komut Rehberi",
        "description": "Hedef: **20 barfiks/gün**",
        "color": 0xFF0000,
        "fields": [
            ("Antrenman Komutları",
             "`!kaydet [sayı]` - Günlük barfiks setini kaydeder.\n"
             "`!gecmis` - Son 5 antrenmanını listeler.\n"
             "`!sonusil` - En son kaydı siler.\n"
             "`!sil [id]` - Belirli ID'li kaydı siler."),
            ("İstatistik Komutları",
             "`!haftalik` - Son 7 günlük toplamın.\n"
             "`!seri` - Kaç gündür aralıksız çektiğin.\n"
             "`!rekor` - Kişisel rekorun.\n"
             "`!grafik` - Görsel performans grafiği."),
        ]
    },
    {
        "title": "💥 Şınav Modülü | Komut Rehberi",
        "description": "Hedef: **50 şınav/gün**",
        "color": 0x00BFFF,
        "fields": [
            ("Antrenman Komutları",
             "`!sinav_kaydet [sayı]` - Günlük şınav setini kaydeder.\n"
             "`!sinav_gecmis` - Son 5 antrenmanını listeler.\n"
             "`!sinav_sonusil` - En son kaydı siler.\n"
             "`!sinav_sil [id]` - Belirli ID'li kaydı siler."),
            ("İstatistik Komutları",
             "`!sinav_haftalik` - Son 7 günlük toplamın.\n"
             "`!sinav_seri` - Kaç gündür aralıksız çektiğin.\n"
             "`!sinav_rekor` - Kişisel rekorun."),
        ]
    },
    {
        "title": "🔱 Dip Modülü | Komut Rehberi",
        "description": "Hedef: **30 dip/gün**",
        "color": 0x9B59B6,
        "fields": [
            ("Antrenman Komutları",
             "`!dip_kaydet [sayı]` - Günlük dip setini kaydeder.\n"
             "`!dip_gecmis` - Son 5 antrenmanını listeler.\n"
             "`!dip_sonusil` - En son kaydı siler.\n"
             "`!dip_sil [id]` - Belirli ID'li kaydı siler."),
            ("İstatistik Komutları",
             "`!dip_haftalik` - Son 7 günlük toplamın.\n"
             "`!dip_seri` - Kaç gündür aralıksız yaptığın.\n"
             "`!dip_rekor` - Kişisel rekorun."),
        ]
    },
]


class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot
        self.current_page = 0

    def build_embed(self):
        page = HELP_PAGES[self.current_page]
        embed = discord.Embed(
            title=page["title"],
            description=page["description"],
            color=page["color"]
        )
        for name, value in page["fields"]:
            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text=f"Sayfa {self.current_page + 1}/{len(HELP_PAGES)} • Kaguya Personal Assistant 🤖")
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        return embed

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(HELP_PAGES) - 1

    @discord.ui.button(label="◀ Geri", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="🏠 Ana Menü", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="İleri ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# ------------------------------------------------------------------ #
#  BaseExercise                                                        #
# ------------------------------------------------------------------ #

class BaseExercise(commands.Cog):
    """
    Parent class for all exercise tracking cogs.
    Provides shared DB logic, generic CRUD, history retrieval, and help UI.
    """

    DB_PATH = 'fitness_data.db'

    def __init__(self, bot, exercise_type: str, daily_target: int):
        self.bot = bot
        self.exercise_type = exercise_type
        self.daily_target = daily_target
        self._db_setup()

    # ------------------------------------------------------------------ #
    #  Database Helpers                                                    #
    # ------------------------------------------------------------------ #

    def _connect(self):
        return sqlite3.connect(self.DB_PATH)

    def _db_setup(self):
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exercises (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     TEXT    NOT NULL,
                    type        TEXT    NOT NULL,
                    count       INTEGER NOT NULL,
                    date        TEXT    NOT NULL
                )
            ''')
            conn.commit()

    def _execute(self, query: str, params: tuple = ()):
        with self._connect() as conn:
            conn.execute(query, params)
            conn.commit()

    def _fetchall(self, query: str, params: tuple = ()):
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def _fetchone(self, query: str, params: tuple = ()):
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    # ------------------------------------------------------------------ #
    #  Generic CRUD                                                        #
    # ------------------------------------------------------------------ #

    def save_entry(self, user_id: str, count: int) -> str:
        today = date.today().strftime("%Y-%m-%d") 
        self._execute(
            "INSERT INTO exercises (user_id, type, count, date) VALUES (?, ?, ?, ?)",
        (user_id, self.exercise_type, count, today)
    )
        return today

    def delete_by_id(self, user_id: str, record_id: int) -> bool:
        row = self._fetchone(
            "SELECT id FROM exercises WHERE id = ? AND user_id = ? AND type = ?",
            (record_id, user_id, self.exercise_type)
        )
        if row:
            self._execute("DELETE FROM exercises WHERE id = ?", (record_id,))
            return True
        return False

    def delete_last(self, user_id: str):
        row = self._fetchone(
            "SELECT id FROM exercises WHERE user_id = ? AND type = ? ORDER BY id DESC LIMIT 1",
            (user_id, self.exercise_type)
        )
        if row:
            self._execute("DELETE FROM exercises WHERE id = ?", (row[0],))
            return row[0]
        return None

    def get_history(self, user_id: str, limit: int = 5):
        return self._fetchall(
            "SELECT id, date, count FROM exercises WHERE user_id = ? AND type = ? ORDER BY id DESC LIMIT ?",
            (user_id, self.exercise_type, limit)
        )

    def get_record(self, user_id: str):
        row = self._fetchone(
            "SELECT MAX(count) FROM exercises WHERE user_id = ? AND type = ?",
            (user_id, self.exercise_type)
        )
        return row[0] if row else None

    def get_weekly_total(self, user_id: str) -> int:

        query = """
            SELECT SUM(count) FROM exercises 
            WHERE user_id = ? 
            AND type = ? 
            AND date >= date('now', '-7 days')
        """
        row = self._fetchone(query, (user_id, self.exercise_type))
        return row[0] if row[0] else 0

    def get_streak(self, user_id: str) -> int:
        rows = self._fetchall(
            "SELECT DISTINCT date FROM exercises WHERE user_id = ? AND type = ?",
            (user_id, self.exercise_type)
        )
        if not rows:
            return 0

        dates = sorted(
        [datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows],
        reverse=True
        )
        today = date.today()

        if dates[0] not in (today, today - timedelta(days=1)):
            return 0

        streak = 0
        expected = dates[0]
        for d in dates:
            if d == expected:
                streak += 1
                expected -= timedelta(days=1)
            else:
                break
        return streak
    # ------------------------------------------------------------------ #
    #  Shared Error Handler                                                #
    # ------------------------------------------------------------------ #

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ **Hata:** Sayıyı doğru formatta girmelisin! Örn: `!kaydet 10`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❓ **Eksik Bilgi:** Sayı girmeyi unuttun. Örn: `!kaydet 5`")
        else:
            print(f"[ERROR] {error}")
