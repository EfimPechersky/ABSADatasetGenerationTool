import xmltodict, json
from Generation.prompts import Prompts
from Generation.Filtration import find_russian_substring_simple
from custom_exceptions import argument_exception,operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Model.LLM import LLM
import random
class KeyDrivenGenerator:
    __aspects={}
    __categories=[]
    __opinions={}
    generated_examples=[]
    model:LLM
    def __init__(self):
        self.__aspects={}
        self.__opinions={}
        self.__categories=[]
        self.generated_examples={}
        self.model=LLM()
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
    
    def add_category(self, value):
        if isinstance(value,str):
            self.__categories.append(value)
        else:
            raise argument_exception(f"Wrong type of category '{value}'!")
            
    def generate_aspects(self, domain):
        for i in self.__categories:
            asp=Prompts.prompt_AspectTerm(domain,i)
            messages =[{"role":"system", "content": Prompts.absa_description},{"role": "user", "content": asp}]
            res=self.model.send_prompt(messages)
            lst=res[res.index("["):res.index("]")+1]
            lst=lst.replace("\n", "")
            lst=lst.replace("'",'"')
            self.__aspects[i]=json.loads(lst)
    
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
    
    def generate_samples(self, domain, examples):
        for category in self.__categories:
            self.generated_examples[category]=[]
            count=0
            while count<1:
                count+=1
                aspect=self.__aspects[category][random.randint(0, len(self.__aspects[category])-1)]
                opinion=self.__opinions[category][random.randint(0, len(self.__opinions[category])-1)]
                gen_prompt = Prompts.generate_prompt(domain, aspect, category,opinion[0], opinion[1], examples[random.randint(0,len(examples)-1)])
                messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
                res=self.model.send_prompt(messages)
                try:
                    js=KeyDrivenGenerator.from_xml(res)
                    self.generated_examples[category]+=js["samples"]
                    count+=1
                except:
                    continue
    
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

    def generate_examples(self, domain,examples,categories=[]):
        if categories!=[]:
            self.categories=categories
        if self.categories==[]:
            raise operation_exception("Categories are empty!")
        self.generate_aspects(domain)
        self.generate_opinions(domain)
        self.generate_samples(domain, examples)
        return self.generated_examples
        
