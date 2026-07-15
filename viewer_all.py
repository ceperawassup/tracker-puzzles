import sqlite3
from collections import defaultdict
from config import PLAYERS

DB_NAME = "activity.db"

def show_all():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, date, puzzles_count FROM daily_puzzles ORDER BY username, date")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("База пуста. Запустите collector.py для сбора данных.")
        return

    user_data = defaultdict(list)
    for user, date, count in rows:
        user_data[user].append((date, count))

    def total(user):
        return sum(cnt for _, cnt in user_data[user])

    sorted_users = sorted(user_data.keys(), key=lambda u: PLAYERS.get(u, u).lower())

    print("=== ПОЛНАЯ ИСТОРИЯ АКТИВНОСТИ ===\n")
    for user in sorted_users:
        display_name = PLAYERS.get(user, user)
        entries = sorted(user_data[user])
        total_sum = sum(cnt for _, cnt in entries)
        active_days = len(entries)
        avg = total_sum / active_days if active_days else 0
        print(f"--- {display_name} ---")
        for date, cnt in entries:
            print(f"  {date}: {cnt}")
        print(f"  Итого: {total_sum} задач за {active_days} дней (в среднем {avg:.1f} в день)\n")

if __name__ == "__main__":
    show_all()
