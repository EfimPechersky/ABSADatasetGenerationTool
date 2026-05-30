from Backend.custom_exceptions import argument_exception, operation_exception
"""
Class defines aspect term
"""
class Aspect:
    """List of available sentiments"""
    Sentiments=["Negative", "Positive", "Neutral"]
    __term=""
    __sentiment=""
    def __init__(self,term:str="", sentiment:str="Neutral"):
        """Constructor

        Args:
            term (str): aspect term Defaults to "".
            sentiment (str): aspect sentiment Defaults to "Neutral".
        """        
        self.term=term
        self.sentiment=sentiment

    @property
    def term(self):
        """Упоминание аспекта в тексте"""
        return self.__term
    
    @term.setter
    def term(self, value):
        """Aspect term setter

        Args:
            value (string): aspect term

        Raises:
            argument_exception: Wrong type of term
        """        ""
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
        """Aspect sentiment setter

        Args:
            value (string): aspect sentiment

        Raises:
            argument_exception: Wrong sentiment
        """        
        if isinstance(value,str) and value in self.Sentiments:
            self.__sentiment=value
        else:
            raise argument_exception(f"Wrong sentiment {value}")
    
    def __eq__(self,value):
        if isinstance(value,Aspect):
            return self.term==value.term
        else:
            raise TypeError
    
    def __str__(self):
        return f"{self.term}:{self.sentiment}"