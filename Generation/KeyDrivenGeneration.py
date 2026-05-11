import xmltodict, json
from Generation.prompts import Prompts
from Generation.Filtration import find_russian_substring_simple
from custom_exceptions import argument_exception,operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Model.LLM import LLM
from Storage.DatabaseManager import DatabaseManager
import random

class KeyDrivenGenerator:
    __aspects={}
    __categories=[]
    __opinions={}
    __project_id=0
    DBManager=DatabaseManager()
    generated_examples=[]
    model:LLM
    def __init__(self, project_id):
        """Class for generation samples for annotation

        Args:
            project_id (int): project identificator
        """        
        self.__aspects={}
        self.__opinions={}
        self.__categories=[]
        self.generated_examples={}
        self.model=LLM()
        self.__project_id=project_id

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
        """add new category of domain

        Args:
            value (str): category

        Raises:
            argument_exception: Wrong type of category
        """        
        if isinstance(value,str):
            self.__categories.append(value)
        else:
            raise argument_exception(f"Wrong type of category '{value}'!")
    
    def __change_progress(self, progress, status_id=2):
        """Change progress of samples generation process

        Args:
            progress (float): progress value
            status_id (int): identificator of operation status. Defaults to 2.
        """        
        if status_id==None:
            self.DBManager.change_operation_info(self.__project_id, "Examples generation",2, progress)
        else:
            self.DBManager.change_operation_info(self.__project_id, "Examples generation", status_id, progress)
    
    def __get_progress(self):
        """get opearion progress

        Returns:
            float: progress value
        """        
        res=self.DBManager.get_operation_info(self.__project_id, "Examples generation")
        return res["progress"]

    def generate_aspects(self, domain):
        """common aspects for every category

        Args:
            domain (str): domain  of reviews
        """        
        for i in self.__categories:
            asp=Prompts.prompt_AspectTerm(domain,i)
            messages =[{"role":"system", "content": Prompts.absa_description},{"role": "user", "content": asp}]
            res=self.model.send_prompt(messages)
            try:
                lst=res[res.index("["):res.index("]")+1]
                lst=lst.replace("\n", "")
                lst=lst.replace("'",'"')
            except:
                asp=Prompts.prompt_AspectTerm(domain,i)
                messages =[{"role":"system", "content": f"You made a mistake in this answer: {res}, DONT REPEAT IT"},{"role": "user", "content": asp}]
                res=self.model.send_prompt(messages)
                print(res)
                lst=res[res.index("["):res.index("]")+1]
                lst=lst.replace("\n", "")
                lst=lst.replace("'",'"')
            self.__aspects[i]=json.loads(lst)
            progress=self.__get_progress()+0.2/len(self.__categories)
            self.__change_progress(progress)
    
    def generate_opinions(self, domain):
        """generate common opinins for every category

        Args:
            domain (str): domain of reviews
        """        
        for i in self.__categories:
            ops=Prompts.prompt_OpinionTerm(domain,i)
            messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": ops}]
            res=self.model.send_prompt(messages)
            try:
                lst=res
                lst=lst.replace("\n", "")
                lst=lst.replace("\t", "")
                #lst=lst.replace(" ","")
                lst=lst.replace("'",'"')
                lst=lst[lst.index("["):lst.rindex("]")+1]
            except:
                ops=Prompts.prompt_OpinionTerm(domain,i)
                messages =[{"role":"system", "content": f"You made a mistake in this answer: {res}, DONT REPEAT IT"},{"role": "user", "content": ops}]
                res=self.model.send_prompt(messages)
                lst=res
                lst=lst.replace("\n", "")
                lst=lst.replace("\t", "")
                #lst=lst.replace(" ","")
                lst=lst.replace("'",'"')
                lst=lst[lst.index("["):lst.rindex("]")+1]
            self.__opinions[i]=json.loads(lst)
            progress=self.__get_progress()+0.2/len(self.__categories)
            self.__change_progress(progress)
    
    def generate_samples(self, domain, examples):
        """Samples generation

        Args:
            domain (str): domain of reviews
            examples (list): real reviews for reference
        """        
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
                    progress=self.__get_progress()+0.6/(len(self.__categories)*examples_num)
                    self.__change_progress(progress)
                except:
                    continue
                
    
    def from_xml(xml):
        """Convert LLM response to json

        Args:
            xml (str): LLM response in xml format

        Returns:
            list: converted samples
        """        
        if "<samples>" in xml:
            text_to_convert=xml[xml.index("<samples>"):xml.index("</samples>")+10].replace('"', ' ')
        else:
            text_to_convert=xml[xml.index("<sample>"):xml.rfind("</sample>")+9].replace('"', ' ')
            text_to_convert="<samples>"+text_to_convert+"</samples>"
        dct=xmltodict.parse(text_to_convert)
        if "sample" in dct["samples"]:
            dct["samples"]=dct["samples"]["sample"]
        return dct


    def generate_examples(self, domain,examples,categories=[]):
        """Generate examples for annotation

        Args:
            domain (str): domain of reviews
            examples (list): real reviews for reference
            categories (list): categories for domain. Defaults to [].

        Raises:
            argument_exception: Categories are empty
            operation_exception: Error occured in generation process
        """        
        try:
            if categories!=[]:
                self.categories=categories
            if self.categories==[]:
                raise argument_exception("Categories are empty!")
            self.generate_aspects(domain)
            self.generate_opinions(domain)
            self.generate_samples(domain, examples)
            self.__change_progress(0.9)
        except Exception as e:
            self.__change_progress(0.0, 4)
            raise operation_exception(f"Error occured in generation process: {e}")
        
        
