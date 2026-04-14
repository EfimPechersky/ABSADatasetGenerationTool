from custom_exceptions import argument_exception
import os
import re
class ProcessStatuses:
    _instance = None
    __examples_generation={}
    __dataset_generation={}
    __model_training={}
    statuses=["In progress", "Done", "Error"]
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_examples_generation_progress(self, code):
        if code not in self.__examples_generation:
            raise argument_exception("Process with this code does not exists")
        result = self.__examples_generation[code]
        #if result['status'] == "done":
        #    del self.__examples_generation[code]
        return result
    
    def get_dataset_generation_progress(self, code):
        if code not in self.__dataset_generation:
            print(self.__dataset_generation)
            raise argument_exception("Process with this code does not exists")
        result = self.__dataset_generation[code]
        #if result['status'] == "Done":
        #    del self.__dataset_generation[code]
        return result
    
    def change_dataset_generation_progress(self, code, status, progress, result=None):
        print(code)
        if status not in self.statuses:
            raise argument_exception("Wrong status")
        if progress<0 or progress>1:
            raise argument_exception("Wrong progress")
        self.__dataset_generation[code]["status"]=status
        self.__dataset_generation[code]["progress"]=progress
        if result!=None:
            self.__dataset_generation[code]["result"]=result
    
    def create_examples_generation_progress(self, code):
        self.__examples_generation[code]={"status":"In progress", 'progress':0, "result":None}

    def create_dataset_generation_progress(self, code):
        print(code)
        self.__dataset_generation[code]={"status":"In progress", 'progress':0, "result":None}

    def change_examples_generation_progress(self, code, status, progress, result=None):
        if status not in self.statuses:
            raise argument_exception("Wrong status")
        if progress<0 or progress>1:
            raise argument_exception("Wrong progress")
        self.__examples_generation[code]["status"]=status
        self.__examples_generation[code]["progress"]=progress
        if result!=None:
            self.__examples_generation[code]["result"]=result
    

    def create_model_training_progress(self, code, epochs):
        self.__model_training[code]={"status":"In progress", 'progress':0, "all_epochs":epochs, 'metrics':[]}
        if os.path.isfile(f"./Model/logs/custom_{code}/trainer.log"):
            with open(f"./Model/logs/custom_{code}/trainer.log", 'w', encoding="UTF-8") as file:
                file.write("")

    def get_model_training_progress(self, code):
        if code not in self.__model_training:
            raise argument_exception("Process with this code does not exists")
        result = self.__model_training[code]
        return result

    def change_training_model_progress(self, code):
        if code not in self.__model_training:
            raise argument_exception("Process with this code does not exists")
        metrics = []
        max_epoch=-1
        with open(f"./Model/logs/custom_{code}/trainer.log", 'r', encoding="UTF-8") as file:
            data=file.read()
            pattern="PROGRESS:.+\n"
            result=re.findall(pattern, data)
            for log in result:
                metrics_per_epoch={}
                info=log.split("PROGRESS: ")[1][:-1]
                splitted=info.split("|")
                for part in splitted:
                    m = part.split(":")
                    if m[0] == "Epoch":
                        if max_epoch<int(m[1]):
                            max_epoch=int(m[1])
                        metrics_per_epoch[m[0].lower()]=int(m[1])
                    else:
                        metrics_per_epoch[m[0]]=float(m[1])
                metrics+=[metrics_per_epoch]
        max_epoch+=1
        status="In progress"
        if max_epoch==self.__model_training[code]["all_epochs"]:
            status="Done"
        self.__model_training[code]["status"]=status
        self.__model_training[code]["progress"]=max_epoch/self.__model_training[code]["all_epochs"]
        self.__model_training[code]["metrics"]=metrics
       
            
        
        