from Generation.Combinations_generation import CombinationGenerator
from Generation.Perephrase_generation import PerephraseGenerator
import spacy
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Storage.DatabaseManager import DatabaseManager
class SamplesGenerator:
    CombGen:CombinationGenerator
    PereGen:PerephraseGenerator
    __orig_dataset:Dataset
    generated_dataset:Dataset
    def __init__(self,dataset:Dataset, project_id):
        """class for samples generation

        Args:
            dataset (Dataset): annotated dataset
            project_id (int): project identificator
        """        
        self.CombGen=CombinationGenerator(project_id)
        self.PereGen=PerephraseGenerator(project_id)
        self.orig_dataset=dataset
        self.generated_dataset=Dataset(dataset.domain)
        self.DBManager=DatabaseManager()
        self.project_id=project_id

    @property
    def orig_dataset(self):
        return self.__orig_dataset
    
    @orig_dataset.setter
    def orig_dataset(self,value):
        if not isinstance(value,Dataset):
            raise argument_exception("Wrong type of dataset!")
        self.__orig_dataset=value

    def generate_dataset(self):
        """Dataset generation using two different methods

        Raises:
            argument_exception: Empty dataset
        """        
        if self.__orig_dataset==[]:
            raise argument_exception("Empty dataset!")
        self.PereGen.generate_samples(self.__orig_dataset)
        self.CombGen.generate_samples(self.__orig_dataset)
        self.generated_dataset.samples=self.CombGen.combinations_dataset.samples+self.PereGen.perephrase_dataset.samples+Dataset.template_dataset().samples
        self.DBManager.change_operation_info(self.project_id, "Dataset generation", 2, 0.9)
    