class GameSpellNotFound(Exception):
    def __init__(self):
        super().__init__("Словарь доступных спеллов не заполнен")
