from Generation.Combinations_generation import CombinationGenerator
from Generation.Perephrase_generation import PerephraseGenerator
import spacy
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Storage.Process_statuses import ProcessStatuses
"""Класс, отвечающий за полную генерацию нового датасета"""
class SamplesGenerator:
    CombGen:CombinationGenerator
    PereGen:PerephraseGenerator
    __orig_dataset:Dataset
    __code=0
    generated_dataset:Dataset
    """Конструктор"""
    def __init__(self,dataset:Dataset, code):
        self.__code=code
        self.CombGen=CombinationGenerator(code)
        self.PereGen=PerephraseGenerator(code)
        self.orig_dataset=dataset
        self.generated_dataset=Dataset(dataset.domain)
        self.__PS=ProcessStatuses()

    """Вручную аннотированный датасет"""
    @property
    def orig_dataset(self):
        return self.__orig_dataset
    
    @orig_dataset.setter
    def orig_dataset(self,value):
        if not isinstance(value,Dataset):
            raise argument_exception("Wrong type of dataset!")
        self.__orig_dataset=value

    """Генерация датасета"""
    def generate_dataset(self):
        if self.__orig_dataset==[]:
            raise argument_exception("Empty dataset!")
        self.PereGen.generate_samples(self.__orig_dataset)
        self.CombGen.generate_samples(self.__orig_dataset)
        self.generated_dataset.samples=self.CombGen.combinations_dataset.samples+self.PereGen.perephrase_dataset.samples+Dataset.template_dataset().samples
        self.__PS.change_dataset_generation_progress(self.__code,"Done", 1.0)
    