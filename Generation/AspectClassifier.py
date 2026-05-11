from Generation.prompts import Prompts
from FileManager.FileManager import FileManager
from custom_exceptions import argument_exception, operation_exception
from Model.LLM import LLM
from Storage.DatabaseManager import DatabaseManager
import json

class AspectClassifier:
    NEW_SAVE_DIR = "./ProjectsStorage/"
    model=LLM()
    DBManager=DatabaseManager()
    process_data=None
    categories=None
    keywords=None
    count_aspects={}
    project_dir=""
    def __init__(self,project_id):
        """Classficate extracted aspects

        Args:
            project_id (int): project identificator

        Raises:
            argument_exception: Wrong project_id
        """        
        try:
            dir_name=self.DBManager.get_project_by_id(project_id).dir_name
            self.project_dir=f"{self.NEW_SAVE_DIR}{dir_name}"
            self.process_data=FileManager.load_json(f"{self.project_dir}/analysed_reviews.json")
            self.categories=FileManager.load_json(f"{self.project_dir}/project_info.json")["categories"]
            for cat in self.categories:
                self.count_aspects[cat]={"all":0, "positive":0, "negative":0, "neutral":0}
            self.count_aspects["Другое"]={"all":0, "positive":0, "negative":0, "neutral":0}
        except:
            raise argument_exception(f"Wrong project_id: {project_id}!")


    def classificate_aspects(self):
        """Classificates aspects by categories of domain
        """        
        if self.process_data==None or self.categories==None:
            operation_exception("Data is empty!")
        all_aspects=[]
        for rev in self.process_data:
            for asp in rev[1].keys():
                all_aspects+=[asp]
        all_aspects=list(set(all_aspects))
        gen_prompt = Prompts.define_aspects_categories(self.categories,all_aspects)
        messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
        res=self.model.send_prompt(messages)
        print(res)
        lst=res[res.index("{"):res.index("}")+1]
        lst=lst.replace("\n", "")
        lst=lst.replace("'",'"')
        self.keywords=json.loads(lst)
        
    
    def get_category(self, aspect):
        """Get category of aspect

        Args:
            aspect (str): aspect term

        Returns:
            str: category of aspect
        """        
        if self.keywords==None:
            self.classificate_aspects()
        for cat in self.keywords:
            if aspect in self.keywords[cat]:
                if cat not in self.count_aspects.keys():
                    return "Другое"
                return cat
        return "Другое"


    def count_aspects_per_category(self):
        """Count aspects by categories and sentiments
        """        
        for rev in self.process_data:
            for asp in rev[1]:
                cat=self.get_category(asp)
                self.count_aspects[cat]["all"]+=1
                self.count_aspects[cat][rev[1][asp].lower()]+=1
        FileManager.save_json(f"{self.project_dir}/dashboard_data.json", self.count_aspects)
