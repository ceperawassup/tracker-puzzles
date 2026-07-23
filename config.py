# Словарь: логин Lichess -> отображаемое имя
PLAYERS = {
    "sweet_bun": "Алёна",
    "mariiyachess": "Маша",
    "vasilisa_ukhta": "Василиса",
    "tasya_28": "Таисия",
    "hondrova_varvara": "Варвара",
    "makovtsova-2016": "Маковцева",
    "patronchik": "Сергей",
    # добавь остальных по необходимости
}
# логин дочери на Lichess
DAUGHTER = "sweet_bun"

# Режим "читерства" и его период (если даты не указаны, действует на все дни)
CHEATER_MODE = True
CHEATER_START = "2026-07-16"   # начало периода
CHEATER_END = "2026-07-21"     # конец периода

# Автоматический список логинов (не трогай)
TRACKED_USERS = list(PLAYERS.keys())

