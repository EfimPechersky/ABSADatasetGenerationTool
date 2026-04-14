import xmltodict, json
from Generation.prompts import Prompts
from Generation.Filtration import find_russian_substring_simple
from custom_exceptions import argument_exception,operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Model.LLM import LLM
from Storage.Process_statuses import ProcessStatuses
import random
"""Модуль для генерации примеров с нуля"""
class KeyDrivenGenerator:
    __aspects={}
    __categories=[]
    __opinions={}
    __code=0
    generated_examples=[]
    model:LLM
    __PS:ProcessStatuses
    def __init__(self, code):
        self.__PS=ProcessStatuses()
        self.__aspects={}
        self.__opinions={}
        self.__categories=[]
        self.generated_examples={}
        self.model=LLM()
        self.__code=code
    """Категории"""
    @property
    def categories(self):
        return self.__categories
    @categories.setter
    def categories(self, value):
        if isinstance(value,list):
            self.__categories=[]
            for i in value:
                self.add_category(i)
        else:
            raise argument_exception("Wrong type of categories!")
    
    """Добавить категорию"""
    def add_category(self, value):
        if isinstance(value,str):
            self.__categories.append(value)
        else:
            raise argument_exception(f"Wrong type of category '{value}'!")
    
    """Генерация аспектов"""
    def generate_aspects(self, domain):
        for i in self.__categories:
            asp=Prompts.prompt_AspectTerm(domain,i)
            messages =[{"role":"system", "content": Prompts.absa_description},{"role": "user", "content": asp}]
            res=self.model.send_prompt(messages)
            lst=res[res.index("["):res.index("]")+1]
            lst=lst.replace("\n", "")
            lst=lst.replace("'",'"')
            self.__aspects[i]=json.loads(lst)
            progress=self.__PS.get_examples_generation_progress(self.__code)["progress"]+0.2/len(self.__categories)
            self.__PS.change_examples_generation_progress(self.__code, "In progress", progress)
    
    """Генерация мнений"""
    def generate_opinions(self, domain):
        for i in self.__categories:
            ops=Prompts.prompt_OpinionTerm(domain,i)
            messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": ops}]
            res=self.model.send_prompt(messages)
            lst=res
            lst=lst.replace("\n", "")
            lst=lst.replace("\t", "")
            #lst=lst.replace(" ","")
            lst=lst.replace("'",'"')
            lst=lst[lst.index("["):lst.rindex("]")+1]
            print(lst)
            self.__opinions[i]=json.loads(lst)
            progress=self.__PS.get_examples_generation_progress(self.__code)["progress"]+0.2/len(self.__categories)
            self.__PS.change_examples_generation_progress(self.__code, "In progress", progress)
    
    """Генерация примеров"""
    def generate_samples(self, domain, examples):
        examples_num=1
        for category in self.__categories:
            self.generated_examples[category]=[]
            count=0
            while count<examples_num:
                aspect=self.__aspects[category][random.randint(0, len(self.__aspects[category])-1)]
                opinion=self.__opinions[category][random.randint(0, len(self.__opinions[category])-1)]
                gen_prompt = Prompts.generate_prompt(domain, aspect, category,opinion[0], opinion[1], examples[random.randint(0,len(examples)-1)])
                messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
                res=self.model.send_prompt(messages)
                try:
                    js=KeyDrivenGenerator.from_xml(res)
                    self.generated_examples[category]+=js["samples"]
                    count+=1
                    progress=self.__PS.get_examples_generation_progress(self.__code)["progress"]+0.6/(len(self.__categories)*examples_num)
                    self.__PS.change_examples_generation_progress(self.__code, "In progress", progress)
                except:
                    continue
                
    
    """Конвертация из xml"""
    def from_xml(xml):
        if "<samples>" in xml:
            text_to_convert=xml[xml.index("<samples>"):xml.index("</samples>")+10].replace('"', ' ')
        else:
            text_to_convert=xml[xml.index("<sample>"):xml.rfind("</sample>")+9].replace('"', ' ')
            text_to_convert="<samples>"+text_to_convert+"</samples>"
        dct=xmltodict.parse(text_to_convert)
        print(dct)
        if "sample" in dct["samples"]:
            dct["samples"]=dct["samples"]["sample"]
        return dct

    """Генерация примеров с нуля"""
    def generate_examples(self, domain,examples,categories=[]):
        try:
            if categories!=[]:
                self.categories=categories
            if self.categories==[]:
                raise operation_exception("Categories are empty!")
            self.generate_aspects(domain)
            self.generate_opinions(domain)
            self.generate_samples(domain, examples)
            self.__PS.change_examples_generation_progress(self.__code, "Done", 1.0, result=self.generated_examples)
        except Exception as e:
            self.__PS.change_examples_generation_progress(self.__code, "Error", 0.0)
            raise operation_exception(f"{e}")
        
        
