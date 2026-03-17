#import pytest
#from DatasetModels.DatasetModel import Dataset
#from Generation.Full_generation import SamplesGenerator
#from Model.LLM import LLM
#class TestGeneration:
#    dataset=Dataset.from_json([["Вкусная еда и отличное обслуживание!", {'еда':'Positive', 'обслуживание':'Positive'}],["Очень неудобная мебель, но приятная атмосфера.", {'мебель':'Negative', 'атмосфера':'Positive'}]])
#    gen=SamplesGenerator("restaurant", dataset)
#    model=LLM()
#    model.apiurl=""
#    def test_generation(self):
#        self.gen.generate_dataset()
#        print(self.gen.generated_dataset)
#        assert 1==0
