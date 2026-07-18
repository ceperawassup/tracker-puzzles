import sqlite3
import argparse
from datetime import date, timedelta
from collections import defaultdict
from config import TRACKED_USERS, PLAYERS

DB_NAME = "activity.db"

def show_last_week(days=7, details=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = date.today()
    week_ago = today - timedelta(days=days-1)
    c.execute('''
        SELECT username, date, puzzles_total, puzzles_win, puzzles_loss
        FROM daily_puzzles
        WHERE date BETWEEN ? AND ?
        ORDER BY username, date DESC
    ''', (week_ago.isoformat(), today.isoformat()))
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("Нет данных за указанный период.")
        return

    user_data = defaultdict(lambda: defaultdict(lambda: {'total':0, 'win':0, 'loss':0}))
    for user, d, total, win, loss in rows:
        user_data[user][d]['total'] += total
        user_data[user][d]['win'] += win
        user_data[user][d]['loss'] += loss

    print(f"Активность по дням с {week_ago} по {today}:\n")
    sorted_users = sorted(user_data.keys(), key=lambda u: PLAYERS.get(u, u).lower())

    for user in sorted_users:
        display_name = PLAYERS.get(user, user)
        print(f"--- {display_name} ---")
        total_week = 0
        for i in range(days):
            day = week_ago + timedelta(days=i)
            day_str = day.isoformat()
            day_data = user_data[user].get(day_str, {'total':0, 'win':0, 'loss':0})
            total = day_data['total']
            total_week += total
            if details:
                print(f"  {day_str}: {total} задач (прав: {day_data['win']}, непр: {day_data['loss']})")
            else:
                print(f"  {day_str}: {total}")
        print(f"  → Всего за неделю: {total_week}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Еженедельная активность")
    parser.add_argument("--days", type=int, default=7, help="Количество дней для отображения")
    parser.add_argument("--details", action="store_true", help="Показывать детализацию правильных/неправильных")
    args = parser.parse_args()
    show_last_week(days=args.days, details=args.details)
