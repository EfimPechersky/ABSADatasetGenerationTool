import requests
"""Класс, описывающий LLM"""
class LLM:
    _instance = None
    __apiurl:str
    def __new__(cls, *args, **kwargs):
        """Class for LLM API management

        Returns:
            LLM: created instance
        """        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def apiurl(self):
        return self.__apiurl
    
    @apiurl.setter
    def apiurl(self,value):
        if not isinstance(value,str):
            raise Exception("Wrong type of url!")
        self.__apiurl=value
    
    def send_prompt(self, messages):
        """Send prompt to API

        Args:
            messages (list): list of messages

        Returns:
            str: LLM response
        """        
        headers = {
            "Content-Type": "application/json"
        }


        response = requests.post(self.apiurl, json=messages, headers=headers)
        
        response.raise_for_status()

        return response.text

