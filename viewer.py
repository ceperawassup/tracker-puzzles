import sqlite3
from datetime import date, timedelta
from collections import defaultdict
from config import TRACKED_USERS, PLAYERS   # <-- добавлен импорт

DB_NAME = "activity.db"

def show_last_week():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = date.today()
    week_ago = today - timedelta(days=6)

    c.execute('''
        SELECT username, date, puzzles_count
        FROM daily_puzzles
        WHERE date BETWEEN ? AND ?
        ORDER BY username, date DESC
    ''', (week_ago.isoformat(), today.isoformat()))
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("Нет данных за последние 7 дней.")
        return

    user_data = defaultdict(lambda: defaultdict(int))
    for user, d, cnt in rows:
        user_data[user][d] += cnt

    print(f"Активность по дням с {week_ago} по {today}:\n")
    # Сортируем пользователей по алфавиту отображаемых имён
    sorted_users = sorted(user_data.keys(), key=lambda u: PLAYERS.get(u, u).lower())
    for user in sorted_users:
        display_name = PLAYERS.get(user, user)
        print(f"--- {display_name} ---")
        total_week = 0
        for i in range(7):
            day = week_ago + timedelta(days=i)
            day_str = day.isoformat()
            cnt = user_data[user].get(day_str, 0)
            total_week += cnt
            print(f"  {day_str}: {cnt}")
        print(f"  → Всего за неделю: {total_week}\n")

if __name__ == "__main__":
    show_last_week()
