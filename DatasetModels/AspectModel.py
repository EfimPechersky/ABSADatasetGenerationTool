from custom_exceptions import argument_exception, operation_exception
"""
Класс, описывающий аспект в тексте
"""
class Aspect:
    """Список возможных тональностей"""
    Sentiments=["Negative", "Positive", "Neutral"]
    __term=""
    __sentiment=""
    """Конструктор"""
    def __init__(self,term:str="", sentiment:str="Neutral"):
        self.term=term
        self.sentiment=sentiment
    """Упоминание аспекта в тексте"""
    @property
    def term(self):
        return self.__term
    
    @term.setter
    def term(self, value):
        if isinstance(value,str):
            self.__term=value
        else:
            raise argument_exception("Wrong type of term!")
    
    """Тональность аспекта"""
    @property
    def sentiment(self):
        return self.__sentiment
    @sentiment.setter
    def sentiment(self, value):
        if isinstance(value,str) and value in self.Sentiments:
            self.__sentiment=value
        else:
            raise argument_exception(f"Wrong sentiment {value}")
    
    """Сравнение аспектов"""
    def __eq__(self,value):
        if isinstance(value,Aspect):
            return self.term==value.term
        else:
            raise TypeError
    
    """Строковое представление аспекта"""
    def __str__(self):
        return f"{self.term}:{self.sentiment}"