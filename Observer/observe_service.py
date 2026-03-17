"""
Реализация наблюдателя
"""
class observe_service:
    handlers = []

    """
    Добавить объект под наблюденние
    """
    @staticmethod
    def add(instance):
        if instance is None: return

        if instance not in  observe_service.handlers:
            observe_service.handlers.append( instance )

    """
    Удалить из под наблюдения
    """
    @staticmethod
    def delete(instance):
        if instance is None: return

        if instance in  observe_service.handlers:
            observe_service.handlers.remove( instance )

    """
    Вызвать событие
    """
    @staticmethod
    def create_event(  event: str, params ):
        for instance in observe_service.handlers:
            instance.handle ( event, params  )