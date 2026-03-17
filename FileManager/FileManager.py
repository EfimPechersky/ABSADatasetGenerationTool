import json
import os
"""Класс, осуществляющий работу с файлами"""
class FileManager:
    """Сохранить данные в json формате"""
    @staticmethod
    def save_json(filename, data):
        try:
            with open(filename, 'w', encoding="utf-8") as file:
                json.dump(data,file)
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")
        return True
    
    """Загрузить данные в json формате"""
    @staticmethod
    def load_json(filename):
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data=json.load(file)
                return data
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")
    
    """Сохранить данные в текстовом формате"""
    @staticmethod
    def save_dat(filename, data):
        try:
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(data)
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")
        return True

    """Загрузить данные из текстововго формата"""
    @staticmethod
    def load_dat(filename, data):
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data=file.read()
                return data
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")