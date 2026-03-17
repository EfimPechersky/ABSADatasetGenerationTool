from Generation.Combinations_generation import CombinationGenerator
from Generation.Perephrase_generation import PerephraseGenerator
import spacy
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
"""Класс, отвечающий за полную генерацию нового датасета"""
class SamplesGenerator:
    CombGen:CombinationGenerator
    PereGen:PerephraseGenerator
    __orig_dataset:Dataset
    generated_dataset:Dataset
    """Конструктор"""
    def __init__(self,dataset:Dataset):
        self.CombGen=CombinationGenerator()
        self.PereGen=PerephraseGenerator()
        self.orig_dataset=dataset
        self.generated_dataset=Dataset(dataset.domain)

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
        self.generated_dataset.samples=self.CombGen.combinations_dataset.samples+self.PereGen.perephrase_dataset.samples
    