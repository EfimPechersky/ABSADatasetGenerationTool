import json
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.SampleModel import Sample
"""Класс, описывающий датасет"""
class Dataset:
    __samples:list
    __domain:str
    """Конструктор"""
    def __init__(self,domain:str="",samples:list=None):
        self.domain=domain
        if samples !=None:
            self.samples=samples
        else:
            self.samples=[]

    """Предметная область"""
    @property
    def domain(self):
        return self.__domain
    
    @domain.setter
    def domain (self, value):
        if not isinstance(value,str):
            raise argument_exception("Wrong type of domain")
        self.__domain=value

    """Список примеров"""
    @property
    def samples(self):
        return self.__samples
    
    @samples.setter
    def samples(self,value):
        self.__samples=[]
        if not isinstance(value,list):
            raise argument_exception("Wrong type of samples")
        for samp in value: 
            self.add_sample(samp) 

    """Добавить новый пример в список"""
    def add_sample(self,sample):
        if not isinstance(sample,Sample):
            raise argument_exception("Wrong type of sample!")
        self.__samples.append(sample)
    
    """Преобразовать датасет в json формат"""
    def to_json(self):
        result=[]
        for samp in self.samples:
            result+=[samp.to_json()]
        return result
    
    """Преобразовать json в датасет"""
    def from_json(json):
        new_dataset=Dataset()
        if isinstance(json,list):
            for samp in json:
                new_samp=Sample.from_json(samp)
                if new_samp:
                    new_dataset.add_sample(new_samp)
            return new_dataset
        else:
            return None

    """Преобразовать датасет в формат для обучения модели pyABSA"""
    def to_dat(self):
        all_dats=[]
        for sample in self.samples:
            all_dats+=sample.to_dat()
        for i in range(0,len(all_dats)-1):
            for j in range(1,len(all_dats[i])-1):
                print(all_dats[i][j])
                if all_dats[i][j][1]=="B-ASP" and all_dats[i][j-1][1]=="B-ASP":
                    all_dats[i][j][1]="I-ASP"
                if len(all_dats[i][j])==3:
                    if all_dats[i][j][1]!="O" and all_dats[i][j][2] not in ["Positive", "Negative", "Neutral", "-100"]:
                        print(all_dats[i][j])
                        all_dats[i][j][2]="Neutral"
        text=""
        for i in range(0,len(all_dats)):
            for j in range(0,len(all_dats[i])):
                text+=" ".join(all_dats[i][j])
                text+='\n'
            text+='\n'
        return text
    
    """Строковое представление датасета"""
    def __str__(self):
        return f"{self.to_json()}"