import json
import os
class FileManager:
    """Class for file management

    Raises:
        Exception: Problem occured while saving a file
        Exception: Problem occured while loading a file

    Returns:
        True: Successfuly saved file
        json: Loaded json
        str: Loaded data
    """    
    @staticmethod
    def save_json(filename, data):
        """Save json data to file

        Args:
            filename (str): path to file
            data (list, dict, str): data for saving

        Raises:
            Exception: Problem occured while saving a file

        Returns:
            True: Successfuly saved file
        """        
        try:
            with open(filename, 'w', encoding="utf-8") as file:
                json.dump(data,file)
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")
        return True
    
    @staticmethod
    def load_json(filename):
        """Load json data from file

        Args:
            filename (str): path to file

        Raises:
            Exception: Problem occured while loading a file

        Returns:
            list, str, dict: loaded data
        """        
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data=json.load(file)
                return data
        except:
            raise Exception(f"Problem occured while loading a file '{filename}'")
    
    @staticmethod
    def save_dat(filename, data):
        """Save data in file

        Args:
            filename (str): path to file
            data (str): data for saving

        Raises:
            Exception: Problem occured while saving a file
        Returns:
            True: successfuly saved data
        """        
        try:
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(data)
        except:
            raise Exception(f"Problem occured while saving a file '{filename}'")
        return True

    @staticmethod
    def load_dat(filename):
        """Load data from file

        Args:
            filename (str): path to file

        Raises:
            Exception: Problem occured while loading a file 

        Returns:
            str: loaded data
        """        
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data=file.read()
                return data
        except:
            raise Exception(f"Problem occured while loading a file '{filename}'")
