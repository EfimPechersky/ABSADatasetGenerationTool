# SampleModel.py - исправленный метод to_dat
import spacy
from Backend.custom_exceptions import argument_exception, operation_exception
from Backend.DatasetModels.AspectModel import Aspect

class Sample:
    __review: str = ""
    __aspects: list = []
    
    def __init__(self, review: str = "", aspects: list = None):
        """Sample for model training

        Args:
            review (str): review text. Defaults to "".
            aspects (list): annotated aspects. Defaults to None.
        """        
        self.review = review
        if aspects != None:
            self.aspects = aspects
        else:
            self.aspects = []
    
    @property
    def review(self):
        return self.__review
    
    @review.setter
    def review(self, value):
        if not isinstance(value, str):
            raise argument_exception("Wrong type of text review!")
        self.__review = value
    
    @property
    def aspects(self):
        return self.__aspects
    
    @aspects.setter
    def aspects(self, value):
        self.__aspects = []
        if isinstance(value, list):
            for asp in value:
                self.add_aspect(asp)
        else:
            raise argument_exception("Wrong type of aspects")
    
    def add_aspect(self, value):
        """Add annotated aspect

        Args:
            value (Aspect): aspect

        Raises:
            argument_exception: Aspect has wrong type or already added
        """        
        if not isinstance(value, Aspect):
            raise argument_exception("Aspect has wrong type or already added")
        if value.term in self.review and value not in self.aspects:
            self.__aspects += [value]
    
    def to_json(self):
        """Convert sample to json

        Returns:
            list: converted sample
        """        
        result = [self.review, {}]
        for asp in self.__aspects:
            result[1][asp.term] = asp.sentiment
        return result
    
    def from_json(json):
        """Convert sample from json

        Args:
            json (list): sample in json format

        Returns:
            False: cannot convert sample
        """        
        if isinstance(json, list) and len(json) == 2:
            if isinstance(json[0], str) and isinstance(json[1], dict):
                aspects = []
                for asp in json[1]:
                    try:
                        new_asp = Aspect(asp, json[1][asp])
                        aspects += [new_asp]
                    except:
                        return False
                return Sample(json[0], aspects)
            return False
        return False
    
    def to_dat(self):
        """Convert sample to format for model training

        Returns:
            list: converted sample
        """        
        nlp = spacy.load("ru_core_news_sm")
        doc = nlp(self.review)
        text_tokens = list(filter(lambda x: (not x in ["<", ">"]), [token.text for token in doc]))
        
        all_aspects = []
        for asp in self.aspects:
            doc = nlp(asp.term)
            aspect_tokens = [token.text for token in doc]
            aspect_tokens = list(filter(lambda x: (not x in ["<", ">"]), aspect_tokens))
            
            for i in range(len(text_tokens) - len(aspect_tokens) + 1):
                if [t.lower() for t in text_tokens[i:i+len(aspect_tokens)]] == [t.lower() for t in aspect_tokens]:
                    all_aspects.append({
                        'tokens': aspect_tokens,
                        'start': i,
                        'end': i + len(aspect_tokens),
                        'sentiment': asp.sentiment,
                        'term': asp.term
                    })
                    break
        
        dats = []
        for main_asp in all_aspects:
            dat = []
            marks = ['O'] * len(text_tokens)
            sentiments = ['-100'] * len(text_tokens)
            
            for asp in all_aspects:
                if asp == main_asp:
                    sentiment = asp['sentiment']
                else:
                    sentiment = '-100'
                
                marks[asp['start']] = 'B-ASP'
                sentiments[asp['start']] = sentiment
                for j in range(1, len(asp['tokens'])):
                    marks[asp['start'] + j] = 'I-ASP'
                    sentiments[asp['start'] + j] = sentiment
            
            for i, token in enumerate(text_tokens):
                if token.strip():
                    dat.append([token.strip(), marks[i], sentiments[i].strip()])
            
            dats.append(dat)
        
        return dats