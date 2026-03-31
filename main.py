from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from Observer.observe_service import observe_service
from Observer.datasets_service import datasets_service
from Observer.event_type import event_type
from Model.LLM import LLM
from datetime import datetime
from Generation.KeyDrivenGeneration import KeyDrivenGenerator

obs=observe_service()
das=datasets_service()
model=LLM()
model.apiurl=""
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки, для продакшена укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"]
)

@app.options("/*")
async def options_save_reviews():
    return {}
SAVE_DIR = "./Datasets/"
"""Метод-прототип для генерации примеров"""
@app.post("/test_generate_examples")
async def test_generate_examples(request: Request):
    return {"status":"success","examples":{"food":["Качество еды оставляет желать лучшего.","Блюда были недостаточно горячие, когда их принесли.","Общее впечатление от ужина было отрицательным."],"service":["Интерьер ресторана создает уютную атмосферу, а управление ожиданием было на высшем уровне, благодаря отличному обслуживанию.","Кухня впечатляет разнообразием блюд, и стоит отметить, что управление ожиданием не омрачило вечер, благодаря отличному обслуживанию.","Персонал проявил себя с лучшей стороны, обеспечивая быстрое обслуживание и комфортное управление ожиданием, что в сочетании с отличным обслуживанием сделало наш визит незабываемым."]}}

"""Генерация примеров для разметки"""
@app.post("/generate_examples")
async def generate_examples(request: Request):
    data = await request.json()
    print(data)
    KDG=KeyDrivenGenerator()
    KDG.generate_examples(data["domain"], data["examples"], data["categories"])
    print(KDG.generated_examples)
    return {"status": "success", "examples":KDG.generated_examples}
@app.post("/save-reviews")
async def save_reviews(request: Request):
    #try:
    data = await request.json()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_dir=SAVE_DIR+f"d{timestamp}/"
    os.makedirs(new_dir, exist_ok="True")
    filename = f"annotated_reviews.json"
    domain=data["domain"]
    with open(new_dir+filename, 'w', encoding="utf-8") as f:
        json.dump(data["data"], f, ensure_ascii=False, indent=2)
    observe_service.create_event(event_type.saved_dataset(),{"path_to_file":new_dir, "domain":domain})
    return {"status": "success", "file": filename}
    
    #except Exception as e:
        #print(str(e))
        #return {"status": "error", "message": str(e)}

# Тестовый endpoint для проверки
@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)