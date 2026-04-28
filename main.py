from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re
from Observer.observe_service import observe_service
from Observer.datasets_service import datasets_service
from Observer.event_type import event_type
from Model.LLM import LLM
from datetime import datetime
from Generation.KeyDrivenGeneration import KeyDrivenGenerator
import random
import asyncio
from Model.ABSAModel import ABSAModel
from FileManager.FileManager import FileManager
from Generation.AspectClassifier import AspectClassifier
from Storage.DatabaseManager import DatabaseManager
from unidecode import unidecode
def generate_code():
    return random.randrange(1000000000, 10000000000)

DBManager=DatabaseManager()
# Инициализация сервисов
obs = observe_service()
das = datasets_service()
model = LLM()
model.apiurl = "https://happy-years-repeat.loca.lt"

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
NEW_SAVE_DIR = "./ProjectsStorage/"
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

@app.post("/create_user")
async def create_user(request: Request):
    data = await request.json()
    try:
        DBManager.create_user(data["login"], data["password"], data["email"])
        return {"status":"Success", "message":"Succesfully created new user!"}
    except Exception as e:
        return {"status":"Error", "message":e}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    try:
        access_token=DBManager.login_user(data["login"], data["password"])
        return {"status":"Success", "message":access_token}
    except Exception as e:
        return {"status":"Error", "message":e}

@app.get("/projects")
async def get_all_projects(request:Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    #try:
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    if user.access_token == access_token:
        projects=DBManager.get_projects_by_user(user.id)
        result={"status":"Success", "result":[]}
        for p in projects:
            result["result"]+=[{"id":p.id,"name":p.name, "date":p.created_at}]
        return result
    return {"status":"Error", "message":"Wrong token!"}
    #except Exception as e:
    #    return {"status":"Error", "message":e}

@app.post("/create_project")
async def create_project(request:Request):
    data = await request.json()
    print(data)
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    filtered_project_name=re.sub(r'[^a-zA-Z0-9]', '', unidecode(data["name"]))
    dir_name=f"{user.login}_{filtered_project_name}_{generate_code()}"
    new_dir = NEW_SAVE_DIR + f"{dir_name}/"
    os.makedirs(new_dir, exist_ok=True)
    DBManager.create_project(data["name"], user.id, dir_name)
    FileManager.save_json(new_dir+"reviews.json", data["examples"])
    project_info={"domain":data["domain"], "categories":data["categories"]}
    FileManager.save_json(new_dir+"project_info.json", project_info)
    return {"status":"Success!", "message":"Project created succesfully!"}

@app.get("/project")
async def get_project(request:Request, project_id:int):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong access token!")
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        project_info=FileManager.load_json(f"{NEW_SAVE_DIR}{project.dir_name}/project_info.json")
        info={"name":project.name, "date":project.created_at}
        info.update(project_info)
        ABSAModel.update_info_from_logs(project_id)
        operations = DBManager.get_operations_by_project(project_id)
        return {"status":"Success", "message":"Succesfully got project info", "info":info, "operations_info":operations}
    raise HTTPException(status_code=401, detail="Wrong access token!")

"""Генерация примеров для разметки"""
@app.post("/generate_examples")
async def generate_examples(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    project_id=data["project_id"]
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong access token!")
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Examples generation")["status"] == "Done":
            return {"status":"Error", "message":"its already done"}
        
        # Запускаем фоновую задачу
        background_tasks.add_task(process_generate_reviews_task, project_id)
        
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")

"""Получить сгенерированный примеры"""
@app.get("/get_examples")
async def get_examples(request: Request, project_id: int):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong access token!")
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Examples generation")["status"] != "Done":
            return {'status':"Error", "message":"Its not done"}
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        result=FileManager.load_json(f"{NEW_SAVE_DIR}{dir_name}/generated_examples.json")
        project_info=FileManager.load_json(f"{NEW_SAVE_DIR}{dir_name}/project_info.json")
        domain=project_info["domain"]
        categories=project_info["categories"]
        return {"status":"success", "data":result, "domain":domain, "categories":categories}
    raise HTTPException(status_code=401, detail="Wrong access token!")

@app.post("/save-reviews")
async def save_reviews(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    project_id=data["project_id"]
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong access token!")
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Examples generation")["status"] != "Done":
            return {"status":"Error", "message":"Previous operation not completed"}
        if DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Not started":
            return {'status':"Error", "message":"Its already done"}
        
        # Запускаем фоновую задачу
        background_tasks.add_task(process_save_reviews_task, data, project_id)
        
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")

@app.post("/train_model")
async def train_model(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    project_id=data["project_id"]
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Done":
            return {"status":"Error", "message":"Previous operation not completed"}
        if DBManager.get_operation_info(project_id, "Model training")["status"] == "Done":
            return {'status':"Error", "message":"Its already done"}
        background_tasks.add_task(process_train_model_task, data, project_id)
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")

@app.post("/analyse_reviews")
async def analyse_reviews(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    project_id=data["project_id"]
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Model training")["status"] != "Done":
            return {"status":"Error", "message":"Previous operation not completed"}
        if DBManager.get_operation_info(project_id, "Review analysis")["status"] == "Done":
            return {'status':"Error", "message":"Its already done"}
        # Запускаем фоновую задачу
        background_tasks.add_task(process_review_analysis_task, project_id)
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")

"""Получить статус обучения модели"""
@app.get("/get_train_model_status")
async def get_train_model_status(request: Request, project_id: int):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    project = DBManager.get_project_by_id(project_id)
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Model training")["status"] == "Not started":
            return {'status':"Error", "message":"Process not started"}
        ABSAModel.update_info_from_logs(project_id)
        res=DBManager.get_model_training_progress(project_id)
        return {"status":"Success","data":res}
    raise HTTPException(status_code=401, detail="Wrong access token!")

# Фоновые задачи
async def process_save_reviews_task(data: dict, project_id: int):
    """Фоновая задача для сохранения отзывов"""
    try:
        if DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Not started":
            print("ha")
            print(DBManager.get_operation_info(project_id, "Dataset generation"))
            return
        DBManager.change_operation_info(project_id, "Dataset generation", 2, 0.0)
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        new_dir = f"{NEW_SAVE_DIR}{dir_name}/dataset/"
        os.makedirs(new_dir, exist_ok=True)
        filename = "annotated_reviews.json"
        project_info=FileManager.load_json(f"{NEW_SAVE_DIR}{dir_name}/project_info.json")
        domain=project_info["domain"]
        
        with open(f"{new_dir}{filename}", 'w', encoding="utf-8") as f:
            json.dump(data["data"], f, ensure_ascii=False, indent=2)
        
        await asyncio.to_thread(observe_service.create_event,
            event_type.saved_dataset(),
            {"path_to_file": new_dir, "domain": domain, "project_id": project_id}
        )
        
        # Обновляем статус при успешном завершении
        DBManager.change_operation_info(project_id, "Dataset generation", 3, 1.0)
        
    except Exception as e:
        print(f"Error in save_reviews_task: {e}")
        DBManager.change_operation_info(project_id, "Dataset generation", 4, 0.0)  # Статус ошибки

async def process_generate_reviews_task(project_id):
    """Фоновая задача для генерации примеров"""
    try:
        if DBManager.get_operation_info(project_id, "Examples generation")["status"] != "Not started":
            return
        DBManager.change_operation_info(project_id, "Examples generation", 2, 0.0)
        KDG = KeyDrivenGenerator(project_id)
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        project_info=FileManager.load_json(f"{NEW_SAVE_DIR}{dir_name}/project_info.json")
        print(project_info)
        domain=project_info["domain"]
        categories=project_info["categories"]
        examples=info=FileManager.load_json(f"{NEW_SAVE_DIR}{dir_name}/reviews.json")
        await asyncio.to_thread(KDG.generate_examples,domain , examples,categories )
        FileManager.save_json(f"{NEW_SAVE_DIR}{dir_name}/generated_examples.json", KDG.generated_examples)
        DBManager.change_operation_info(project_id, "Examples generation", 3, 1.0)
    except Exception as e:
        DBManager.change_operation_info(project_id,"Examples generation",4, 0.0)
        print(f"Error in generate_reviews_task: {e}")

async def process_train_model_task(data:dict, project_id):
    """Фоновая задача для генерации примеров"""
    try:
        if DBManager.get_operation_info(project_id, "Model training")["status"] != "Not started":
            return
        DBManager.change_operation_info(project_id, "Model training", 2, 0.0)
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        dataset_path=f"{NEW_SAVE_DIR}{dir_name}/dataset/dat"
        dataset_path=dataset_path.replace("/", "\\")
        model = ABSAModel()
        await asyncio.to_thread(model.train, project_id, int(data["epochs"]), int(data["batch_size"]))
        DBManager.change_operation_info(project_id, "Model training", 3, 1.0)
    except Exception as e:
        DBManager.change_operation_info(project_id,"Model training",4, 0.0)
        print(f"Error in train_model_task: {e}")

async def process_review_analysis_task(project_id):
    """Фоновая задача для анализа отзывов"""
    try:
        if DBManager.get_operation_info(project_id, "Review analysis")["status"] != "Not started":
            return
        DBManager.change_operation_info(project_id, "Review analysis", 2, 0.0)
        model=ABSAModel()
        model.load_model_from_file(project_id)
        await asyncio.to_thread(model.analyse_all_reviews,project_id)
        DBManager.change_operation_info(project_id,"Review analysis",2, 0.7)
        AS=AspectClassifier(project_id)
        await asyncio.to_thread(AS.count_aspects_per_category)
        DBManager.change_operation_info(project_id,"Review analysis",3, 1.0)
    except Exception as e:
        print(f"Error in review_analysis_task: {e}")
        DBManager.change_operation_info(project_id,"Review analysis",4, 0.0)  # Статус ошибки

@app.get("/chart-data")
async def get_chart_data(request: Request, project_id ,sentiment: str = "all"):
    """
    API endpoint для получения данных для диаграмм
    sentiment: 'positive', 'negative', 'neutral', 'all'
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    user = DBManager.get_user_by_access_token(access_token)
    if not user:
        return {"status":"Error", "message":"Wrong acess token!"}
    project = DBManager.get_project_by_id(project_id)
    if not(user.access_token == access_token and project.user_id==user.id):
        raise HTTPException(status_code=401, detail="Wrong access token!")
    if not(DBManager.get_operation_info(project_id, "Review analysis")["status"] == "Done"):
        raise HTTPException(status_code=401, detail="Review analysis is not done!")
    project = DBManager.get_project_by_id(project_id)
    dir_name=DBManager.get_project_by_id(project_id).dir_name
    data_path=f"{NEW_SAVE_DIR}{dir_name}/dashboard_data.json"
    data=FileManager.load_json(data_path)
    if data==None:
        raise HTTPException(status_code=401, detail="No data!")
    # Фильтруем данные в зависимости от выбранной тональности
    filtered_data = []
    for item in data:
        if sentiment == "positive":
            value = data[item]["positive"]
        elif sentiment == "negative":
            value = data[item]["negative"]
        elif sentiment == "neutral":
            value = data[item]["neutral"]
        else:  # all
            value = data[item]["all"]
        
        filtered_data.append({
            "category": item,
            "value": value,
            # Сохраняем все данные для tooltip'ов
            "total": data[item]["all"],
            "positive": data[item]["positive"],
            "negative": data[item]["negative"],
            "neutral": data[item]["neutral"]
        })
    
    return {
        "status":"Success",
        "sentiment": sentiment,
        "data": filtered_data
    }

# Тестовый endpoint для проверки
@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)