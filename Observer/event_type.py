
"""
Типы событий
"""
class event_type:
    """
    Событие - сохранение нового датасета
    """
    @staticmethod
    def saved_dataset() -> str:
        return "New annotated dataset was saved"

    """
    Получить список всех событий
    """
    @staticmethod
    def events() -> list:
        result = []
        methods = [method for method in dir(event_type) if
                    callable(getattr(event_type, method)) and not method.startswith('__') and method != "events"]
        for method in methods:
            key = getattr(event_type, method)()
            result.append(key)

        return result