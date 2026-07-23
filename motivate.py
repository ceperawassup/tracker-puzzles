import sqlite3
import argparse
from datetime import date, timedelta, datetime
from config import DAUGHTER, PLAYERS, CHEATER_MODE, CHEATER_START, CHEATER_END

DB_NAME = "activity.db"

def get_stats(start, end):
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

def print_motivation(period=None, date_str=None, details=False, cheater_mode=False):
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

    # Если cheater_mode активен – перемещаем дочь в конец списка
    if cheater_mode:
        # Удаляем дочь из списка, если она там есть
        rows = [row for row in rows if row[0] != DAUGHTER]
        # Добавляем её в конец
        rows.append((DAUGHTER, daughter_total, daughter_win, daughter_loss))
        leader_row = rows[0] if rows else (None, 0, 0, 0)
    else:
        leader_row = rows[0] if rows else (None, 0, 0, 0)

    leader_user, leader_total, leader_win, leader_loss = leader_row
    leader_name = PLAYERS.get(leader_user, leader_user) if leader_user else "—"

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
    if cheater_mode:
        # Зачёркнутый текст (ANSI) и пометка
        strike = '\033[9m'
        reset = '\033[0m'
        print(f"  {strike}Задачи: {daughter_total} (прав: {daughter_win}, непр: {daughter_loss}){reset} ❌ СЖУЛЬНИЧАЛА")
        if daughter_total > 0:
            win_rate = (daughter_win / daughter_total) * 100
            print(f"  {strike}Точность: {win_rate:.1f}%{reset}")
    else:
        print(f"  Задачи: {daughter_total} (прав: {daughter_win}, непр: {daughter_loss})")
        if daughter_total > 0:
            win_rate = (daughter_win / daughter_total) * 100
            print(f"  Точность: {win_rate:.1f}%")
        else:
            print("  Задач пока нет 😴")
    print()

    # Сравнение с лидером
    if cheater_mode:
        print("🏆 Ты сегодня вне зачёта!")
    else:
        if daughter_total == leader_total and leader_user == DAUGHTER:
            print("🏆 Ты лучшая! Так держать!")
        elif daughter_total == leader_total:
            print(f"🥇 Ты делишь первое место с {leader_name} — отлично!")
        else:
            diff = leader_total - daughter_total
            print(f"📈 Лидер — {leader_name} с {leader_total} задачами.")
            print(f"   Тебе не хватило {diff} задач, чтобы догнать.")
            if diff <= 5:
                print("   Всего несколько задачек! Поднажми 😉")
            else:
                print("   Не расстраивайся, завтра новый день! ☀️")

        # Оценка точности (только если не cheater_mode)
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
    print("")

    # Если включены подробности, выводим таблицу всех игроков
    if details:
        print("\n--- Все результаты ---")
        GREEN = '\033[92m'
        RESET = '\033[0m'
        STRIKE = '\033[9m'

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
            if user == DAUGHTER and cheater_mode:
                # Перечёркиваем и добавляем метку
                line = f"{i:<5} {STRIKE}{name:<20} {total:>6} {win:>5} {loss:>5} {rate:>7.1f}%{RESET} ❌ СЖУЛЬНИЧАЛА"
                print(line)
            elif user == DAUGHTER and not cheater_mode:
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

    # Определяем cheater_mode для запрошенного периода
    cheater_mode = False
    if CHEATER_MODE:
        if CHEATER_START and CHEATER_END:
            # Определим start, end для проверки пересечения
            if args.date:
                req_date = datetime.strptime(args.date, "%Y-%m-%d").date()
                req_start = req_end = req_date
            elif args.period == "today":
                req_start = req_end = date.today()
            elif args.period == "yesterday":
                req_start = req_end = date.today() - timedelta(days=1)
            elif args.period == "week":
                req_start = date.today() - timedelta(days=6)
                req_end = date.today()
            elif args.period == "month":
                req_start = date.today() - timedelta(days=29)
                req_end = date.today()
            else:
                req_start = req_end = date.today()

            cheat_start = datetime.strptime(CHEATER_START, "%Y-%m-%d").date()
            cheat_end = datetime.strptime(CHEATER_END, "%Y-%m-%d").date()
            if max(req_start, cheat_start) <= min(req_end, cheat_end):
                cheater_mode = True
        else:
            # Даты не заданы — читерство на все дни
            cheater_mode = True

    print_motivation(period=args.period if not args.date else None,
                     date_str=args.date,
                     details=args.details,
                     cheater_mode=cheater_mode)
