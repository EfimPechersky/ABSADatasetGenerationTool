from sqlalchemy import create_engine, Column, Integer, String, inspect, ForeignKey,select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Mapped,mapped_column,relationship
from Storage.Base import Base
from Storage.OperationsTable import Operation
from Storage.Statuses import OperationStatus
from Storage.OperationTypesTable import OperationType
from Storage.ProjectsTable import Project
from Storage.UserTable import User
from Storage.ModelTrainTable import ModelTraining
from Storage.TrainingQueue import Queue
from custom_exceptions import argument_exception, operation_exception
import bcrypt
from uuid import uuid4
from sqlalchemy import func
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-super-secret-key-change-this-to-something-very-secure-2024"  # В продакшене храните в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class DatabaseManager:
    _instance = None
    _initialized=False
    engine=None
    op_types=[]
    op_statuses=[]
    tables=[Operation.__tablename__,OperationType.__tablename__, User.__tablename__,Project.__tablename__, OperationStatus.__tablename__, ModelTraining.__tablename__, Queue.__tablename__]
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.engine = create_engine('postgresql://postgres:mysecretpassword@localhost:5432/postgres')
        self.session = sessionmaker(bind=self.engine)
        if not self.__check_tables():
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            with self.session() as session:
                self.op_types=[
                    OperationType(name="Examples generation"),
                    OperationType(name="Dataset generation"),
                    OperationType(name="Model training"),
                    OperationType(name="Review analysis")
                ]
                self.op_statuses=[
                    OperationStatus(name="Not started"),
                    OperationStatus(name="In progress"), 
                    OperationStatus(name="Done"), 
                    OperationStatus(name="Error"),
                    OperationStatus(name="Queue")
                ]
                session.add_all(self.op_types)
                session.add_all(self.op_statuses)
                session.commit()
        self._initialized=True
            
    

    def __check_tables(self):
        inspector = inspect(self.engine)
        table_list = inspector.get_table_names()
        for table in self.tables:
            if table not in table_list:
                return False
        return True
    
    @staticmethod
    def validate(value, value_type, length=None):
        if not isinstance(login, value_type):
            raise argument_exception(f"Wrong type of value '{value.__name__}'")
        if length!=None:
            if len(login)<=0 or len(login)>length:
                raise argument_exception(f"Wrong length of value '{value.__name__}'")

    def create_user(self, login, password_hash, email):
        with self.session() as session:
            # Проверка существования пользователя
            stmt = select(func.count(User.id)).where(User.login == login)
            row_count = session.scalar(stmt)
            if row_count > 0:
                raise argument_exception("User with this login already exists!")
            stmt = select(func.count(User.id)).where(User.email == email)
            row_count = session.scalar(stmt)
            if row_count > 0:
                raise argument_exception("User with this email already exists!")
            
            # Пароль уже пришел в виде хеша, сохраняем его как есть
            # (или можно дополнительно захешировать bcrypt для двойной защиты)
            new_user = User(login=login, password=password_hash, email=email)
            session.add_all([new_user])
            session.commit()

    def login_user(self, login, password_hash):
        with self.session() as session:
            stmt = select(User).where(User.login == login)
            user = session.scalars(stmt).one()
            
            # Сравниваем хеш из БД с пришедшим хешем
            if user.password == password_hash:
                access_token = create_access_token(
                    data={"sub": str(user.id), "login": user.login, "email": user.email}
                )
                user.access_token = access_token
                session.commit()
                return access_token
            else:
                raise argument_exception("Wrong login or password!")

  
    
    def get_user_by_id(self, id):
        with self.session() as session:
            stmt = select(User).where(User.id==id)
            user = session.scalars(stmt).one()
            return user
    
    def get_user_by_login(self, login):
        with self.session() as session:
            stmt = select(User).where(User.login==login)
            user = session.scalars(stmt).one()
            return user
    
    def get_user_by_access_token(self, access_token):
        with self.session() as session:
            stmt = select(User).where(User.access_token==access_token)
            try:
                user = session.scalars(stmt).one()
                return user
            except:
                return False

    def get_all_users(self):
        with self.session() as session:
            stmt = select(User)
            users = session.scalars(stmt)
            return users
    
    def create_project(self, name, user_id, dir_name):
        with self.session(autoflush=False) as session:
            user=session.get(User, user_id)
            print(user)
            new_project=Project(name=name, user=user, dir_name=dir_name)
            session.get(Project, 1)
            print(new_project)
            session.add(new_project)
            op_types = session.query(OperationType).all()
            status = session.get(OperationStatus, 1)
            for ot in op_types:
                new_operation=Operation(project=new_project, operation_type=ot, status=status, progress=0.0)
                session.add(new_operation)
            session.commit()
    
    def get_project_by_id(self, project_id):
        with self.session() as session:
            stmt = select(Project).where(Project.id==project_id)
            project = session.scalars(stmt).one()
            return project
    
    def get_projects_by_user(self, user_id):
        with self.session() as session:
            stmt = select(Project).where(Project.user_id==user_id)
            projects = session.scalars(stmt).all()
            return projects
    
    def create_operation(self, project, operation_type, status, progress):
        with self.session() as session:
            new_operation=Operation(project=project, operation_type=operation_type, status=status, progress=progress)
            session.add_all([new_operation])
            session.commit()
    
    def get_operation_by_id(self, id):
        with self.session() as session:
            stmt = select(Operation).where(Operation.id==id)
            operation = session.scalars(stmt).one()
            return operation
    
    def get_operations_by_project(self, project_id):
        with self.session() as session:
            stmt = select(Operation).where(Operation.project_id == project_id)
            operations = session.scalars(stmt).all()
            
            # Преобразуем объекты в словари ДО закрытия сессии
            result = []
            for op in operations:
                result.append({
                    "id": op.id,
                    "project_id": op.project_id,
                    "type": op.operation_type.name if op.operation_type else None,
                    "status": op.status.name if op.status else None,
                    "progress": op.progress
                })
            return result
    
    def change_operation_info(self, project_id, operation_type:str, status_id:int=None, progress:float=None):
        with self.session() as session:
            stmt = select(Operation).where(Operation.project_id == project_id).where(Operation.operation_type.has(OperationType.name == operation_type))
            operation = session.scalars(stmt).one()
            print(operation)
            if status_id!=None:
                status = session.get(OperationStatus, status_id)
                operation.status=status
            if progress!=None:
                if isinstance(progress,float):
                    operation.progress=progress
            session.commit()
    
    def get_operation_info(self, project_id, operation_type:str):
        with self.session() as session:
            stmt = select(Operation).where(Operation.project_id == project_id).where(Operation.operation_type.has(OperationType.name == operation_type))
            operation = session.scalars(stmt).one()
            return {"status":operation.status.name, "progress":operation.progress}
    

    def create_model_train_row(self, project_id, current_epoch, num_epochs, batch_size, apc_acc, apc_f1, ate_f1):
        with self.session() as session:
            project=session.get(Project, project_id)
            stmt = select(func.count(ModelTraining.id)).where(ModelTraining.project_id==project_id).where(ModelTraining.current_epoch == current_epoch)
            row_count = session.scalar(stmt)
            if row_count>0:
                return False
            new_row=ModelTraining(
                project=project, 
                num_epochs=num_epochs, 
                batch_size=batch_size, 
                current_epoch=current_epoch, 
                apc_acc=apc_acc,
                apc_f1=apc_f1,
                ate_f1=ate_f1
                )
            session.add(new_row)
            session.commit()
        return True
    
    def add_to_queue(self, project_id, batch_size, num_epochs):
         with self.session() as session:
            project=session.get(Project, project_id)
            new_queue_row = Queue(project=project, batch_size=batch_size, num_epochs=num_epochs)
            session.add(new_queue_row)
            session.commit()

    def complete_queue(self, project_id):
        with self.session() as session:
            stmt = select(Queue).where(Queue.project_id == project_id)
            queue_row = session.scalars(stmt).one()
            queue_row.is_completed=True
            session.commit()

    def get_count_queue(self):
        with self.session() as session:
            stmt = select(func.count(Queue.id)).where(Queue.is_completed == False)
            row_count = session.scalar(stmt)
            return row_count

    def next_in_queue(self):
        if self.get_count_queue()==0:
            return False
        with self.session() as session:
            stmt = select(Queue).where(Queue.is_completed == False).order_by(Queue.id)
            queue_row = session.scalars(stmt).first()
            return {"project_id":queue_row.project_id, "batch_size":queue_row.batch_size, "num_epochs":queue_row.num_epochs}

    def get_model_training_progress(self, project_id):
        with self.session() as session:
            stmt = select(ModelTraining).where(ModelTraining.project_id==project_id)
            rows = session.scalars(stmt).all()
            result=[]
            for row in rows:
                result+=[{"epoch":row.current_epoch, "apc_acc":row.apc_acc, "apc_f1":row.apc_f1, "ate_f1":row.ate_f1}]
            return result

    

    
    