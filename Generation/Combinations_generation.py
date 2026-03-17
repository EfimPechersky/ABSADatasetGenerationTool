import xmltodict, json
from Generation.prompts import Prompts
from Generation.Filtration import find_russian_substring_simple
from custom_exceptions import argument_exception,operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Model.LLM import LLM
"""Класс, отвечающий за генерацию при помощи метода комбинации"""
class CombinationGenerator:
    combinations_dataset:Dataset
    model:LLM
    """Конструктор"""
    def __init__(self):
        self.combinations_dataset=Dataset()
        self.model=LLM()

    """Преобразование ответа из xml в json"""
    def from_xml(xml):
        if "<samples>" in xml:
            text_to_convert=xml[xml.index("<samples>"):xml.index("</samples>")+10].replace('"', ' ')
        else:
            text_to_convert=xml[xml.index("<sample>"):xml.rfind("</sample>")+9].replace('"', ' ')
            text_to_convert="<samples>"+text_to_convert+"</samples>"
        dct=xmltodict.parse(text_to_convert)
        if "sample" in dct["samples"]:
            dct["samples"]=dct["samples"]["sample"]
        return dct
    
    """Генерация примеров"""
    def generate_samples(self,dataset:Dataset):
        if not isinstance(dataset,Dataset):
            raise argument_exception("Wrong type of dataset")
        self.combinations_dataset.domain=dataset.domain
        samples=[]
        for i in range(0,len(dataset.samples)):
            for j in range(i+1,len(dataset.samples)):
                gen_prompt = Prompts.combination_prompt(dataset.domain,dataset.samples[i].review, dataset.samples[i].aspects,dataset.samples[j].review, dataset.samples[j].aspects)
                messages =[{"role":"system", "content":Prompts.absa_description},{"role": "user", "content": gen_prompt}]
                res=self.model.send_prompt(messages)
                samples+=[res]
        json_data={"samples":[]}
        for i in samples:
            try:
                js=CombinationGenerator.from_xml(i)
                json_data["samples"]+=[js["samples"]]
            except:
                continue
        print(json_data)
        all_samples=[]
        for sample in json_data["samples"]:
            if type(sample)==dict:
                all_samples+=[sample]
            elif type(sample)==list:
                all_samples+=sample
        for sample in all_samples:
            if type(sample["aspect"]) == list:
                if len(sample["aspect"])==0:
                    continue
                new_aspects=[]
                for asp in range(0,len(sample["aspect"])):
                    aspect=sample["aspect"][asp]["term"]
                    try:
                        indexes=find_russian_substring_simple(sample["sentence"],aspect)
                    except:
                        continue
                    if indexes==[]:
                        continue
                    else:
                        indexes=indexes[0]
                    new_sent=sample["aspect"][asp]["sentiment"].strip()[0].upper()+sample["aspect"][asp]["sentiment"].strip()[1:]
                    print(new_sent)
                    if new_sent in Aspect.Sentiments:
                        new_asp=Aspect(sample["sentence"][indexes[0]:indexes[1]],new_sent)
                        new_aspects+=[new_asp]
                if len(new_aspects)>0:
                    new_samp=Sample(sample["sentence"], new_aspects)
                    print(new_samp)
                    self.combinations_dataset.add_sample(new_samp)
            else:
                aspect=sample["aspect"]["term"]
                try:
                    indexes=find_russian_substring_simple(sample["sentence"],aspect)
                except:
                    continue
                if indexes==[]:
                    continue
                else:
                    indexes=indexes[0]
                new_sent=sample["aspect"]["sentiment"].strip()[0].upper+sample["aspect"]["sentiment"].strip()[1:]
                print(new_sent)
                if new_sent in Aspect.Sentiments:
                    new_asp=Aspect(sample["sentence"][indexes[0]:indexes[1]],new_sent)
                self.combinations_dataset.add_sample(Sample(sample["sentence"],[new_asp]))
            print(self.combinations_dataset)