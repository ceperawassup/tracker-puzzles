import sqlite3
from datetime import date, timedelta

DB_NAME = "activity.db"

def show_last_week():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = date.today()
    week_ago = today - timedelta(days=6)  # последние 7 дней, включая сегодня
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

    # Готовим таблицу: {username: {date: count, ...}}
    from collections import defaultdict
    user_data = defaultdict(lambda: defaultdict(int))
    for user, d, cnt in rows:
        user_data[user][d] += cnt

    # Выводим по дням для каждого пользователя
    print(f"Активность по дням с {week_ago} по {today}:\n")
    for user in sorted(user_data.keys()):
        print(f"--- {user} ---")
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
