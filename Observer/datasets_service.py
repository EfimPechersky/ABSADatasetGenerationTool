from Observer.observe_service import observe_service
from Generation.Full_generation import SamplesGenerator
from Observer.event_type import event_type
from FileManager.FileManager import FileManager
from DatasetModels.DatasetModel import Dataset
from Generation.KeyDrivenGeneration import KeyDrivenGenerator
import os
"""Класс следящий за появлением новых датасетов"""
class datasets_service():

    """Конструктор"""
    def __init__(self):
        self.__gen:SamplesGenerator
        observe_service.add(self)

    """
    Обработка событий
    """
    def handle(self, event:str, params):

        if event == event_type.saved_dataset():
            data=FileManager.load_json(params["path_to_file"]+"annotated_reviews.json")
            dataset=Dataset.from_json(data)
            print(dataset)
            dataset.domain=params["domain"]
            self.__gen=SamplesGenerator(dataset)
            self.__gen.generate_dataset()
            print(self.__gen.generated_dataset)
            os.makedirs(params["path_to_file"]+"dat", exist_ok="True")
            FileManager.save_json(params["path_to_file"]+"generated_dataset.json", self.__gen.generated_dataset.to_json())
            FileManager.save_dat(params["path_to_file"]+"dat/generated_dataset.train.dat.atepc", self.__gen.generated_dataset.to_dat())
            FileManager.save_dat(params["path_to_file"]+"dat/annotated_dataset.test.dat.atepc", dataset.to_dat())