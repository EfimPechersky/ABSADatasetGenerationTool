
import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re
from Backend.Model.LLM import LLM
from datetime import datetime
from Backend.Generation.KeyDrivenGeneration import KeyDrivenGenerator
from Backend.Generation.Full_generation import SamplesGenerator
import random
import asyncio
from Backend.Model.ABSAModel import ABSAModel
from Backend.FileManager.FileManager import FileManager
from Backend.Generation.AspectClassifier import AspectClassifier
from Backend.DatasetModels.DatasetModel import Dataset
from Backend.Storage.DatabaseManager import DatabaseManager
from Backend.download_models import check_and_download_checkpoint
from unidecode import unidecode

def generate_code():
    """random number generation

    Returns:
        int: random number
    """    
    return random.randrange(1000000000, 10000000000)

DBManager=DatabaseManager()
# Инициализация сервисов
model = LLM()
model.apiurl = os.getenv("LLM_API_URL", "https://7941-34-135-48-16.ngrok-free.app")
check_and_download_checkpoint()
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


NEW_SAVE_DIR = "./ProjectsStorage/"

SECRET_KEY =  os.getenv("SECRET_KEY", "your-super-secret-key-change-this-to-something-very-secure-2024")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",60))

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token

    Args:
        data (dict)
        expires_delta (timedelta): Defaults to None.

    Returns:
        str: encoded jwt
    """    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """token verification

    Args:
        token (str): JWT token

    Returns:
        dict: verification result
    """    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.options("/*")
async def options_save_reviews():
    """Endpoint for CORS

    Returns:
        dict: Nothing
    """    
    return {}

@app.post("/create_user")
async def create_user(request: Request):
    """User creation endpoint

    Args:
        request (Request)

    Returns:
        dict: registration status
    """    
    data = await request.json()
    try:
        DBManager.create_user(data["login"], data["password"], data["email"])
        return {"status":"Success", "message":"Succesfully created new user!"}
    except Exception as e:
        return {"status":"Error", "message":f"{e}"}

@app.post("/login")
async def login(request: Request):
    """Login endpoint

    Args:
        request (Request)

    Returns:
        dict: status and token
    """    
    data = await request.json()
    try:
        access_token=DBManager.login_user(data["login"], data["password"])
        return {"status":"Success", "message":access_token}
    except Exception as e:
        print(e)
        return {"status":"Error", "message":f"Wrong login or password"}

@app.get("/projects")
async def get_all_projects(request:Request):
    """endpoints for projects info

    Args:
        request (Request): _description_

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format

    Returns:
        dict: _description_
    """    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Проверяем формат "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    access_token = parts[1]
    try:
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
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Error on server side")

@app.post("/create_project")
async def create_project(request:Request):
    """Project creation endpoint

    Args:
        request (Request)

    Raises:
        HTTPException: Invalid authorization header format
        HTTPException: Authorization header missing

    Returns:
        dict: creation status
    """    
    data = await request.json()
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
    """Project info endpoint

    Args:
        request (Request)
        project_id (int): project identificator

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: project info
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

@app.post("/generate_examples")
async def generate_examples(request: Request, background_tasks: BackgroundTasks):
    """Endpoint to start generation operation

    Args:
        request (Request)
        background_tasks (BackgroundTasks)

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: operation status
    """    
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
    """Endpoint to get generated examples

    Args:
        request (Request)
        project_id (int): project identificator

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: generated examples
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
    """Dataset generation endpoint

    Args:
        request (Request)
        background_tasks (BackgroundTasks)

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: status
    """    
    data = await request.json()
    project_id=data["project_id"]
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

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
        if DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Not started" and DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Error":
            return {'status':"Error", "message":"Its already done"}
        
        background_tasks.add_task(process_save_reviews_task,data, project_id)
        
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")

@app.post("/train_model")
async def train_model(request: Request, background_tasks: BackgroundTasks):
    """Endpoint to start model training 

    Args:
        request (Request)
        background_tasks (BackgroundTasks)

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: operation status
    """  
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
        if DBManager.get_operation_info(project_id, "Model training")["status"] != "Not started" and DBManager.get_operation_info(project_id, "Model training")["status"] != "Error" and DBManager.get_operation_info(project_id, "Model training")["status"] != "Queue":
            print(DBManager.get_operation_info(project_id, "Model training"))
            return {'status':"Error", "message":"Its in progress"}
        DBManager.change_operation_info(project_id, "Model training", 5, 0.0)
        DBManager.add_to_queue(project_id, data["batch_size"],data["epochs"])
        if DBManager.get_count_queue()<2:
            background_tasks.add_task(new_process_train_model_task)
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Wrong access token!")


@app.post("/analyse_reviews")
async def analyse_reviews(request: Request, background_tasks: BackgroundTasks):
    """Endpoint to start review analysis

    Args:
        request (Request)
        background_tasks (BackgroundTasks)

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: operation status
    """  
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
    """Endpoint for model training progress

    Args:
        request (Request)
        project_id (int)

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong access token

    Returns:
        dict: training progress
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
    if user.access_token == access_token and project.user_id==user.id:
        if DBManager.get_operation_info(project_id, "Model training")["status"] == "Not started" or DBManager.get_operation_info(project_id, "Model training")["status"] == "Queue":
            return {'status':"Error", "message":"Process not started"}
        ABSAModel.update_info_from_logs(project_id)
        res=DBManager.get_model_training_progress(project_id)
        return {"status":"Success","data":res}
    raise HTTPException(status_code=401, detail="Wrong access token!")


async def process_save_reviews_task(data, project_id: int):
    """Background task for dataset generaion

    Args:
        data(dict):data
        project_id (int): project identificator
    """    
    try:
        if DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Not started" and DBManager.get_operation_info(project_id, "Dataset generation")["status"] != "Error":
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
        data=FileManager.load_json(new_dir+"annotated_reviews.json")
        dataset=Dataset.from_json(data)
        dataset.domain=domain
        gen=SamplesGenerator(dataset, project_id)
        await asyncio.to_thread(gen.generate_dataset)
        os.makedirs(new_dir+"dat", exist_ok="True")
        await asyncio.to_thread(FileManager.save_json, new_dir+"generated_dataset.json", gen.generated_dataset.to_json())
        await asyncio.to_thread(FileManager.save_dat, new_dir+"dat/generated_dataset.train.dat.atepc", gen.generated_dataset.to_dat())
        dataset.samples=dataset.samples+Dataset.template_dataset().samples
        await asyncio.to_thread(FileManager.save_dat, new_dir+"dat/annotated_dataset.test.dat.atepc", dataset.to_dat())
        # Обновляем статус при успешном завершении
        DBManager.change_operation_info(project_id, "Dataset generation", 3, 1.0)
        
    except Exception as e:
        print(f"Error in save_reviews_task: {e}")
        DBManager.change_operation_info(project_id, "Dataset generation", 4, 0.0)  # Статус ошибки

async def process_generate_reviews_task(project_id):
    """Background task for examples generation

    Args:
        project_id (int): project identificator
    """    
    try:
        if DBManager.get_operation_info(project_id, "Examples generation")["status"] != "Not started" and DBManager.get_operation_info(project_id, "Examples generation")["status"] != "Error":
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



async def new_process_train_model_task():
    """Background task for model training
    """    
    niq=DBManager.next_in_queue()
    while niq:
        project_id=niq["project_id"]
        try:
            DBManager.change_operation_info(project_id, "Model training", 2, 0.0)
            model = await asyncio.to_thread(ABSAModel)
            await asyncio.to_thread(model.train, project_id, niq["num_epochs"], niq["batch_size"])
            DBManager.change_operation_info(project_id, "Model training", 3, 1.0)
            DBManager.complete_queue(project_id)
        except Exception as e:
            DBManager.complete_queue(project_id)
            DBManager.change_operation_info(project_id,"Model training",4, 0.0)
            print(f"Error in train_model_task: {e}")
        niq=DBManager.next_in_queue()

async def process_review_analysis_task(project_id):
    """Background task for review analysis

    Args:
        project_id (int): project identificator
    """    
    try:
        print("1")
        if DBManager.get_operation_info(project_id, "Review analysis")["status"] != "Not started" and  DBManager.get_operation_info(project_id, "Review analysis")["status"] != "Error":
            return
        DBManager.change_operation_info(project_id, "Review analysis", 2, 0.0)
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        import os
        print("2")
        if not os.path.isfile(f"{NEW_SAVE_DIR}{dir_name}/analysed_reviews.json"):
            model=await asyncio.to_thread(ABSAModel)
            model.load_model_from_file(project_id)
            await asyncio.to_thread(model.analyse_all_reviews,project_id)
        DBManager.change_operation_info(project_id,"Review analysis",2, 0.7)
        AS=AspectClassifier(project_id)
        print("3")
        await asyncio.to_thread(AS.count_aspects_per_category)
        DBManager.change_operation_info(project_id,"Review analysis",3, 1.0)
    except Exception as e:
        print(f"Error in review_analysis_task: {e}")
        DBManager.change_operation_info(project_id,"Review analysis",4, 0.0)  # Статус ошибки

@app.get("/chart-data")
async def get_chart_data(request: Request, project_id ,sentiment: str = "all"):
    """Endpoint for chart data

    Args:
        request (Request)
        project_id (int): project
        sentiment (str): Value of filter by sentiments. Defaults to "all".

    Raises:
        HTTPException: Authorization header missing
        HTTPException: Invalid authorization header format
        HTTPException: Wrong acess token
        HTTPException: Review analysis is not done
        HTTPException: No data

    Returns:
        dict: Data for charts
    """    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
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
    filtered_data = []
    for item in data:
        if sentiment == "positive":
            value = data[item]["positive"]
        elif sentiment == "negative":
            value = data[item]["negative"]
        elif sentiment == "neutral":
            value = data[item]["neutral"]
        else: 
            value = data[item]["all"]
        
        filtered_data.append({
            "category": item,
            "value": value,

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

@app.get("/test")
async def test():
    """Test endpoint

    Returns:
        dict: Successful response
    """
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)