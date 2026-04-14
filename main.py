from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from Observer.observe_service import observe_service
from Observer.datasets_service import datasets_service
from Observer.event_type import event_type
from Model.LLM import LLM
from datetime import datetime
from Generation.KeyDrivenGeneration import KeyDrivenGenerator
from Storage.Process_statuses import ProcessStatuses
import random
import asyncio
from Model.ABSAModel import ABSAModel

def generate_code():
    return random.randrange(1000000000, 10000000000)

# Инициализация сервисов
obs = observe_service()
das = datasets_service()
model = LLM()
model.apiurl = "https://thin-files-sing.loca.lt"

app = FastAPI()

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки, для продакшена укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"]
)

SAVE_DIR = "./Datasets/"
PS = ProcessStatuses()

@app.options("/*")
async def options_save_reviews():
    return {}

"""Метод-прототип для генерации примеров"""
@app.post("/test_generate_examples")
async def test_generate_examples(request: Request):
    return {
        "status": "success",
        "examples": {
            "food": [
                "Качество еды оставляет желать лучшего.",
                "Блюда были недостаточно горячие, когда их принесли.",
                "Общее впечатление от ужина было отрицательным."
            ],
            "service": [
                "Интерьер ресторана создает уютную атмосферу, а управление ожиданием было на высшем уровне, благодаря отличному обслуживанию.",
                "Кухня впечатляет разнообразием блюд, и стоит отметить, что управление ожиданием не омрачило вечер, благодаря отличному обслуживанию.",
                "Персонал проявил себя с лучшей стороны, обеспечивая быстрое обслуживание и комфортное управление ожиданием, что в сочетании с отличным обслуживанием сделало наш визит незабываемым."
            ]
        }
    }

"""Генерация примеров для разметки"""
@app.post("/generate_examples")
async def generate_examples(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    code = generate_code()
    PS.create_examples_generation_progress(code)
    print(data)
    
    # Запускаем фоновую задачу
    background_tasks.add_task(process_generate_reviews_task, data, code)
    
    return {"status": "success", "code": code}

"""Получить статус генерации примеров"""
@app.get("/get_examples_generation_status")
async def get_examples_generation_status(code: str):
    # Получаем статус из хранилища
    result = PS.get_examples_generation_progress(int(code))
    print(result)
    # Форматируем ответ в нужном формате
    return result

@app.post("/save-reviews")
async def save_reviews(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    code = generate_code()
    PS.create_dataset_generation_progress(code)
    print(data)
    
    # Запускаем фоновую задачу
    background_tasks.add_task(process_save_reviews_task, data, code)
    
    return {"status": "success", "code": code}

@app.post("/train_model")
async def train_model(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    code = data["code"]
    print(code)
    PS.create_model_training_progress(int(code), int(data["epochs"]))
    # Запускаем фоновую задачу
    background_tasks.add_task(process_train_model_task, data, int(code))
    
    return {"status": "success", "code": code}

"""Получить статус обучения модели"""
@app.get("/get_train_model_status")
async def get_train_model_status(code: str):
    # Получаем статус из хранилища
    PS.change_training_model_progress(int(code))
    result = PS.get_model_training_progress(int(code))
    # Форматируем ответ в нужном формате
    return result

"""Получить статус генерации датасета"""
@app.get("/get_dataset_generation_status")
async def get_dataset_generation_status(code: str):
    # Получаем статус из хранилища
    result = PS.get_dataset_generation_progress(int(code))
    
    # Форматируем ответ в нужном формате
    return result

# Фоновые задачи
async def process_save_reviews_task(data: dict, code: int):
    """Фоновая задача для сохранения отзывов"""
    try:
        new_dir = SAVE_DIR + f"d{code}/"
        os.makedirs(new_dir, exist_ok=True)
        filename = "annotated_reviews.json"
        domain = data["domain"]
        
        with open(new_dir + filename, 'w', encoding="utf-8") as f:
            json.dump(data["data"], f, ensure_ascii=False, indent=2)
        
        await asyncio.to_thread(observe_service.create_event,
            event_type.saved_dataset(),
            {"path_to_file": new_dir, "domain": domain, "code": code}
        )
        
        # Обновляем статус при успешном завершении
        PS.change_dataset_generation_progress(code, PS.statuses[1], 1.0)
        
    except Exception as e:
        print(f"Error in save_reviews_task: {e}")
        PS.change_dataset_generation_progress(code, PS.statuses[2], 1.0)  # Статус ошибки

async def process_generate_reviews_task(data: dict, code: int):
    """Фоновая задача для генерации примеров"""
    try:
        # Обновляем статус на "в процессе"
        PS.change_examples_generation_progress(code, PS.statuses[0], 0.1)
        
        # Создаем генератор
        KDG = KeyDrivenGenerator(code)
        
        # Генерируем примеры
        await asyncio.to_thread(KDG.generate_examples, data["domain"], data["examples"], data["categories"])
        print(KDG.generated_examples)
        
        # Обновляем статус на "завершено" с результатом
        PS.change_examples_generation_progress(code, PS.statuses[1], 1.0)
        
        # Если у вас есть возможность сохранить результат в ProcessStatuses, сделайте это
        # Например:
        # PS.set_result(code, KDG.generated_examples)
        
    except Exception as e:
        print(f"Error in generate_reviews_task: {e}")
        PS.change_examples_generation_progress(code, PS.statuses[2], 1.0)  # Статус ошибки

async def process_train_model_task(data:dict, code: int):
    """Фоновая задача для генерации примеров"""
    dataset_path=f"datasets\d{code}\dat"
    model = ABSAModel()
    await asyncio.to_thread(model.train, code, int(data["epochs"]), int(data["batch_size"]), dataset_path)

# Тестовый endpoint для проверки
@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)