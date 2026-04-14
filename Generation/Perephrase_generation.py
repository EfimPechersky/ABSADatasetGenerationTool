from Generation.prompts import Prompts
from Generation.Filtration import find_russian_substring_simple
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Model.LLM import LLM
from Storage.Process_statuses import ProcessStatuses
import re
"""Класс, отвечающий за генерацию примеров при помощи метода перефразирования"""
class PerephraseGenerator:
    __all_samples=[]
    __all_dasp=[]
    perephrase_dataset:Dataset
    __PS:ProcessStatuses
    model:LLM
    """Конструктор"""
    def __init__(self, code):
        self.__all_samples=[]
        self.__all_dasp=[]
        self.perephrase_dataset=Dataset()
        self.model=LLM()
        self.__PS=ProcessStatuses()
        self.__code=code
    
    """Генерация примеров"""
    def get_samples(self,domain, sentence):
        gen_prompt = Prompts.get_semantic_paraphrasing_prompt(domain,sentence)
        messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
        res = self.model.send_prompt(messages)
        print(res)
        samples=res.split("SAMPLE")[1:]
        print(samples)
        for i in range(0,len(samples)):
            if "</s>" in samples[i]:
                samples[i]=samples[i][samples[i].index(":")+2:samples[i].index("</s>")]
            else:
                samples[i]=samples[i][samples[i].index(":")+2:samples[i].index("\n")]
        return samples
    
    """Разметка примеров"""
    def get_aspects(self, source_sentence, sentences,aspects):
        gen_prompt = Prompts.get_aspect_annotation_prompt(source_sentence,sentences,aspects)
        messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
        res=self.model.send_prompt(messages)
        dasp=[]
        new_asp=[]
        aspects=res[:res.index("</s>")].split("\n")
        for asp in aspects:
            if asp[:7]!="ASPECTS":
                continue
            new_asp+=[asp[7:]]
        aspects=new_asp.copy()
        print(aspects)
        for i in range(0,len(aspects)):
            dasp+=[{}]
            aspects[i]=aspects[i][aspects[i].index(":")+2:]

            for asp in aspects[i].split(";")[:-1]:
                dasp[i][re.split("\d?\ ?\:", asp)[0].strip()]=asp.split(":")[1].strip()
        return dasp
    
    """Генерация датасета"""
    def generate_samples(self,dataset:Dataset):
        if not isinstance(dataset, Dataset):
            raise argument_exception("Wrong type of dataset")
        self.perephrase_dataset.domain=dataset.domain
        for samp in dataset.samples:
            try:
                gen_samples=self.get_samples(dataset.domain, samp.review)
                gen_aspects=self.get_aspects(samp.review, gen_samples,samp.aspects)
            except:
                continue
            if len(gen_samples)==len(gen_aspects):
                self.__all_samples+=gen_samples
                self.__all_dasp+=gen_aspects
            progress=self.__PS.get_dataset_generation_progress(self.__code)["progress"]+0.5/len(dataset.samples)
            self.__PS.change_dataset_generation_progress(self.__code,"In progress", progress)
        for ind in range(0,len(self.__all_samples)):
            new_aspects=[]
            for aspect in self.__all_dasp[ind]:
                try:
                    indexes=find_russian_substring_simple(self.__all_samples[ind],aspect)
                except:
                    continue
                if indexes==[]:
                    continue
                else:
                    indexes=indexes[0]
                new_asp=Aspect(self.__all_samples[ind][indexes[0]:indexes[1]],self.__all_dasp[ind][aspect][0].upper()+self.__all_dasp[ind][aspect][1:])
                new_aspects+=[new_asp]
            if len(new_aspects)>0:
                new_samp=Sample(self.__all_samples[ind],new_aspects)
                self.perephrase_dataset.add_sample(new_samp)
            