import requests
"""Класс, описывающий LLM"""
class LLM:
    _instance = None
    __apiurl:str
    """Singletone"""
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    """Ссылка на API"""
    @property
    def apiurl(self):
        return self.__apiurl
    
    @apiurl.setter
    def apiurl(self,value):
        if not isinstance(value,str):
            raise Exception("Wrong type of url!")
        self.__apiurl=value
    
    """Отправка запроса и получение ответа"""
    def send_prompt(self, messages):
        headers = {
            "Content-Type": "application/json"
        }

        # Отправка POST запроса

        response = requests.post(self.apiurl+"/test", json=messages, headers=headers)
        
        # Проверка статуса ответа
        response.raise_for_status()
        
        # Вывод результата
        return response.text

