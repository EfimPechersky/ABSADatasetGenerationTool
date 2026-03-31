from Generation.KeyDrivenGeneration import KeyDrivenGenerator
from Model.LLM import LLM
from DatasetModels.DatasetModel import Dataset
domain="restaurant"
categories=["Food", "Service", "Place"]
examples=["Вкусная еда и отличное обслуживание!","Очень неудобная мебель, но приятная атмосфера."]
llm= LLM()
llm.apiurl="https://01ba-34-126-120-46.ngrok-free.app"
KDG=KeyDrivenGenerator()
KDG.generate_examples(domain, examples, categories)
print(KDG.generated_examples)