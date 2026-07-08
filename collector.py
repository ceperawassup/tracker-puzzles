import requests
import sqlite3
from datetime import datetime, timezone
from config import TRACKED_USERS

DB_NAME = "activity.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_puzzles (
            username TEXT,
            date TEXT,
            puzzles_count INTEGER,
            PRIMARY KEY (username, date)
        )
    ''')
    conn.commit()
    return conn

def fetch_daily_puzzles(username):
    url = f"https://lichess.org/api/user/{username}/activity"
    resp = requests.get(url, headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"Ошибка {resp.status_code} для {username}")
        return []
    data = resp.json()
    entries = []
    for day_entry in data:
        interval = day_entry.get("interval")
        puzzles = day_entry.get("puzzles")
        if not interval or not puzzles:
            continue
        # Преобразуем start-метку в дату (UTC)
        start_ms = interval.get("start")
        if not start_ms:
            continue
        date_obj = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        date_str = date_obj.strftime("%Y-%m-%d")
        # Суммируем все попытки за день
        score = puzzles.get("score", {})
        total = score.get("win", 0) + score.get("loss", 0) + score.get("draw", 0)
        if total > 0:
            entries.append((username, date_str, total))
    return entries

def save_entries(conn, entries):
    c = conn.cursor()
    for username, date_str, count in entries:
        c.execute('''
            INSERT OR REPLACE INTO daily_puzzles (username, date, puzzles_count)
            VALUES (?, ?, ?)
        ''', (username, date_str, count))
    conn.commit()

def main():
    conn = init_db()
    for user in TRACKED_USERS:
        print(f"Сбор для {user}...")
        entries = fetch_daily_puzzles(user)
        if entries:
            save_entries(conn, entries)
            print(f"  Сохранено дней: {len(entries)}")
            # Для наглядности выведем последние 3 дня
            for e in sorted(entries, reverse=True)[:3]:
                print(f"    {e[1]}: {e[2]} задач")
        else:
            print("  Нет данных (активность не найдена)")
    conn.close()
    print("Готово.")

if __name__ == "__main__":
    main()
