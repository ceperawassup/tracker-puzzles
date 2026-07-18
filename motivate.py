import sqlite3
import argparse
from datetime import date, timedelta, datetime
from config import DAUGHTER, PLAYERS

DB_NAME = "activity.db"

def get_stats(start, end):
    """Возвращает список строк (username, total, win, loss) за указанный диапазон дат (включительно)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = '''
        SELECT username,
               SUM(puzzles_total) as total,
               SUM(puzzles_win) as win,
               SUM(puzzles_loss) as loss
        FROM daily_puzzles
        WHERE date BETWEEN ? AND ?
        GROUP BY username
        ORDER BY total DESC
    '''
    c.execute(query, (start, end))
    rows = c.fetchall()
    conn.close()
    return rows

def print_motivation(period=None, date_str=None, details=False):
    today = date.today()

    # Определяем диапазон дат
    if date_str:
        try:
            specific_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = end = specific_date.isoformat()
            period_label = specific_date.strftime("%Y-%m-%d")
            period_type = "date"
        except ValueError:
            print("Неверный формат даты. Используйте YYYY-MM-DD.")
            return
    else:
        if period == "today":
            start = end = today.isoformat()
            period_label = today.isoformat()
            period_type = "today"
        elif period == "yesterday":
            yesterday = today - timedelta(days=1)
            start = end = yesterday.isoformat()
            period_label = yesterday.isoformat()
            period_type = "yesterday"
        elif period == "week":
            start = (today - timedelta(days=6)).isoformat()
            end = today.isoformat()
            period_label = f"{start} – {end}"
            period_type = "week"
        elif period == "month":
            start = (today - timedelta(days=29)).isoformat()
            end = today.isoformat()
            period_label = f"{start} – {end}"
            period_type = "month"
        else:
            print("Укажите --period (today, yesterday, week, month) или --date YYYY-MM-DD")
            return

    rows = get_stats(start, end)
    if not rows:
        print("Нет данных за этот период.")
        return

    # Словарь для быстрого доступа
    stats = {user: (total, win, loss) for user, total, win, loss in rows}

    # Данные дочери
    daughter_total, daughter_win, daughter_loss = stats.get(DAUGHTER, (0, 0, 0))
    daughter_name = PLAYERS.get(DAUGHTER, DAUGHTER)

    # Лидер (первый в списке)
    leader_user, leader_total, leader_win, leader_loss = rows[0]
    leader_name = PLAYERS.get(leader_user, leader_user)

    # Заголовок
    if period_type == "today":
        print(f"=== Мотивация за сегодня ({period_label}) ===")
    elif period_type == "yesterday":
        print(f"=== Мотивация за вчера ({period_label}) ===")
    elif period_type == "date":
        print(f"=== Мотивация за {period_label} ===")
    else:
        print(f"=== Мотивация за период {period_label} ===")
    print()

    # Основная информация о дочери
    print(f"Твои результаты, {daughter_name}:")
    print(f"  Задачи: {daughter_total} (прав: {daughter_win}, непр: {daughter_loss})")
    if daughter_total > 0:
        win_rate = (daughter_win / daughter_total) * 100
        print(f"  Точность: {win_rate:.1f}%")
    else:
        print("  Задач пока нет 😴")
    print()

    # Сравнение с лидером
    if daughter_total == leader_total and leader_user == DAUGHTER:
        print("🏆 Ты лучшая! Так держать!")
    elif daughter_total == leader_total:
        print(f"🥇 Ты делишь первое место с {leader_name} — отлично!")
    else:
        diff = leader_total - daughter_total
        print(f"📈 Лидер — {leader_name} с {leader_total} задачами.")
        print(f"   Тебе не хватило {diff} задач, чтобы догнать.")
        if diff <= 5:
            print("   Всего несколько задачек! Поднажми сегодня вечером 😉")
        else:
            print("   Не расстраивайся, завтра новый день! ☀️")

    # Оценка точности
    if daughter_total > 0:
        avg_win_rate = 0
        count = 0
        for user, total, win, loss in rows:
            if total > 0:
                avg_win_rate += (win / total) * 100
                count += 1
        if count > 1:
            avg_win_rate /= count
            daughter_rate = (daughter_win / daughter_total) * 100
            if daughter_rate > avg_win_rate + 5:
                print(f"🧠 Твоя точность ({daughter_rate:.1f}%) выше средней ({avg_win_rate:.1f}%) — ты решаешь не только много, но и правильно!")
            elif daughter_rate < avg_win_rate - 5:
                print(f"💡 Твоя точность ({daughter_rate:.1f}%) ниже средней ({avg_win_rate:.1f}%). Старайся не спешить, проверяй каждый ход.")

    print()
    print("Продолжай заниматься, и результат придёт! 💪")

    # Если включены подробности, выводим таблицу всех игроков
    if details:
        print("\n--- Все результаты ---")
        # ANSI-коды для выделения дочери
        GREEN = '\033[92m'
        RESET = '\033[0m'

        # Шапка таблицы
        header = f"{'Место':<5} {'Имя':<20} {'Задач':>6} {'Прав':>5} {'Непр':>5} {'Точность':>8}"
        print(header)
        print("-" * len(header))

        for i, (user, total, win, loss) in enumerate(rows, start=1):
            name = PLAYERS.get(user, user)
            if total > 0:
                rate = (win / total) * 100
            else:
                rate = 0.0
            line = f"{i:<5} {name:<20} {total:>6} {win:>5} {loss:>5} {rate:>7.1f}%"
            if user == DAUGHTER:
                # Выделяем зелёным
                print(f"{GREEN}{line}{RESET}")
            else:
                print(line)
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Мотивационный отчёт для шахматистки")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--period", default="today",
                       choices=["today", "yesterday", "week", "month"],
                       help="За какой период вывести мотивацию (по умолчанию today)")
    group.add_argument("--date", type=str, default=None,
                       help="Конкретная дата в формате YYYY-MM-DD")
    parser.add_argument("--details", action="store_true",
                        help="Показать полный список всех участников с детализацией")
    args = parser.parse_args()

    print_motivation(period=args.period if not args.date else None,
                     date_str=args.date,
                     details=args.details)
