import sqlite3
from config import PLAYERS

DB_NAME = "activity.db"

def show_all():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT username, date, puzzles_total, puzzles_win, puzzles_loss FROM daily_puzzles ORDER BY username, date")
    except Exception as e:
        print(f"Ошибка чтения базы: {e}")
        conn.close()
        return
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("База пуста. Запустите collector.py для сбора данных.")
        return

    # Группируем по пользователям
    from collections import defaultdict
    user_data = defaultdict(list)
    for user, date, total, win, loss in rows:
        user_data[user].append((date, total, win, loss))

    # Сортируем пользователей по имени из PLAYERS
    sorted_users = sorted(user_data.keys(), key=lambda u: PLAYERS.get(u, u).lower())

    print("=== ПОЛНАЯ ИСТОРИЯ АКТИВНОСТИ ===\n")
    for user in sorted_users:
        display_name = PLAYERS.get(user, user)
        entries = sorted(user_data[user])  # по датам
        total_sum = sum(t for _, t, _, _ in entries)
        active_days = len(entries)
        avg = total_sum / active_days if active_days else 0
        win_sum = sum(w for _, _, w, _ in entries)
        loss_sum = sum(l for _, _, _, l in entries)
        print(f"--- {display_name} ---")
        for date, t, w, l in entries:
            # Выводим детализацию, если она есть
            if w + l > 0:
                print(f"  {date}: {t} задач (прав: {w}, непр: {l})")
            else:
                print(f"  {date}: {t} задач")
        print(f"  Итого: {total_sum} задач за {active_days} дней (в среднем {avg:.1f} в день)")
        if win_sum + loss_sum > 0:
            print(f"  Правильно: {win_sum}, неправильно: {loss_sum}")
        print()

if __name__ == "__main__":
    show_all()
