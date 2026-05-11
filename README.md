# 🏋️ Kaguya: Personal Fitness Tracker

A discipline-oriented Discord fitness tracking assistant developed with OOP principles and modular architecture.

## 🚀 Key Features
* **Modular Architecture (Cogs):** Each exercise type (Pull-ups, Push-ups, Dips) is isolated in its own module to enhance system scalability.
* **Smart Inheritance:** All exercise modules are derived from a central `BaseExercise` class, effectively preventing code redundancy (DRY principle).
* **Data Analytics:** Integrated with Matplotlib to generate real-time performance graphs for tracking progress.
* **Discipline Tracking:** Utilizes SQL-based algorithms to track daily streaks, weekly totals, and personal records.
* **Advanced UI:** Provides a dynamic, paginated help menu utilizing Discord's button and embed features.

## 🛠️ Technical Stack
* **Language:** Python.
* **Database:** SQLite3.
* **Core Libraries:** `discord.py`, `matplotlib`, `python-dotenv`.
* **Architecture:** Object-Oriented Programming (OOP) and Modular Cogs structure.

## 🔧 Installation & Usage
1. Clone the repository and install dependencies: `pip install -r requirements.txt`.
2. Rename `.env.example` to `.env` and define your `DISCORD_TOKEN` and `CHANNEL_ID` variables.
3. Launch the bot: `python main.py`.
4. Access the command guide on Discord via the `!help` command.

---
*This project demonstrates technical proficiency in software architecture and database management.*