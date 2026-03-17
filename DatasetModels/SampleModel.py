from DatasetModels.AspectModel import Aspect
from custom_exceptions import argument_exception, operation_exception
import spacy
"""Класс, описывающий пример с разметкой"""
class Sample:
    __review:str=""
    __aspects:list=[]
    """Конструктор"""
    def __init__(self, review:str="", aspects:list=None):
        self.review=review
        if aspects!=None:
            self.aspects=aspects
        else:
            self.aspects=[]
    
    """Текст примера"""
    @property
    def review(self):
        return self.__review
    
    @review.setter
    def review(self,value):
        if not isinstance(value,str):
            raise argument_exception("Wrong type of text review!")
        self.__review=value
    
    """Список аспектов"""
    @property
    def aspects(self):
        return self.__aspects
    
    @aspects.setter
    def aspects(self,value):
        self.__aspects=[]
        if isinstance(value,list):
            for asp in value:
                self.add_aspect(asp)
        else:
            raise argument_exception("Wrong type of aspects")
    
    """Добавить аспект в пример"""
    def add_aspect(self,value):
        if not isinstance(value,Aspect):
            raise argument_exception("Aspect has wrong type or already added")
        if value.term in self.review and value not in self.aspects:        
            self.__aspects+=[value]

    """Преобразовать пример в json"""
    def to_json(self):
        result=[self.review,{}]
        for asp in self.__aspects:
            result[1][asp.term]=asp.sentiment
        return result

    """Преобразовать json в пример"""
    def from_json(json):
        if isinstance(json,list) and len(json)==2:
            if isinstance(json[0],str) and isinstance(json[1], dict):
                aspects=[]
                for asp in json[1]:
                    try:
                        new_asp=Aspect(asp,json[1][asp])
                        aspects+=[new_asp]
                    except:
                        return False
                return Sample(json[0], aspects)
            return False
        return False
    
    """Преобразовать пример в формат для обучения модели"""
    def to_dat(self):
        nlp = spacy.load("ru_core_news_sm")
        doc = nlp(self.review)
        text_tokens = list(filter(lambda x: (not x in ["<", ">"]),[token.text for token in doc]))
        new_aspects=[]
        for asp in self.aspects:
           doc = nlp(asp.term)
           aspect_tokens = [token.text for token in doc]
           aspect_tokens=list(filter(lambda x: (not x in ["<", ">"]),aspect_tokens))
           new_aspects+=[[aspect_tokens,asp.sentiment]]
        dats=[]
        for main_asp in new_aspects:
            dat=[]
            for tok in text_tokens:
                if tok.strip()=="":
                    continue
                tok_type="O"
                sentiment="-100"
                for asp in new_aspects:
                    if tok.lower() in list(map(str.lower,asp[0])):
                        tok_type="B-ASP"
                        if tok.lower() in list(map(str.lower,main_asp[0])):
                            sentiment=asp[1]
                            break
                dat+=[[tok.strip(),tok_type,sentiment.strip()]]
            dats+=[dat]
        return dats