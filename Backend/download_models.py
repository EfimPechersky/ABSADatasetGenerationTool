import os
import subprocess
import sys
import zipfile
import urllib.request
from pathlib import Path

def check_and_download_checkpoint():
    """
    Проверяет наличие моделей в указанных папках.
    Если модели отсутствуют или папки пусты, скачивает их.
    """
    
    # Определяем базовую директорию (работает и в Docker, и локально)
    if os.path.exists('/.dockerenv'):
        base_dir = "/app"
    else:
        base_dir = "."
    
    # Пути к моделям
    bert_model_path = os.path.join(base_dir, "Backend/Model/microsoft--mdeberta-v3-base")
    absa_model_path = os.path.join(base_dir, "Backend/Model/checkpoints/ATEPC_MULTILINGUAL_CHECKPOINT")
    
    # Функция для проверки, пуста ли папка
    def is_dir_empty(path):
        return not (os.path.exists(path) and os.listdir(path))
    
    # Функция для проверки наличия необходимых файлов модели
    def is_bert_model_valid(path):
        required_files = ["config.json", "pytorch_model.bin"]
        if not os.path.exists(path):
            return False
        for file in required_files:
            if not os.path.exists(os.path.join(path, file)):
                return False
        return True
    
    def is_absa_model_valid(path):
        required_files = ["fast_lcf_atepc.config", "fast_lcf_atepc.state_dict", "fast_lcf_atepc.tokenizer"]
        if not os.path.exists(path):
            return False
        for file in required_files:
            if not os.path.exists(os.path.join(path, file)):
                return False
        return True
    
    # Скачивание BERT модели (microsoft/mdeberta-v3-base)
    if not is_bert_model_valid(bert_model_path):
        print(f"BERT model not found or incomplete at {bert_model_path}. Downloading...")
        
        # Создаем директорию
        os.makedirs(bert_model_path, exist_ok=True)
        
        # Пытаемся использовать huggingface-cli
        try:
            result = subprocess.run([
                sys.executable, "-m", "huggingface_hub.commands.huggingface_cli", "download",
                "microsoft/mdeberta-v3-base",
                "--local-dir", bert_model_path,
                "--local-dir-use-symlinks", "False"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ BERT model downloaded successfully via huggingface-cli")
            else:
                raise Exception("huggingface-cli failed")
                
        except Exception as e:
            print(f"huggingface-cli failed: {e}, trying alternative method...")
            
            # Альтернативный метод: через transformers
            try:
                from transformers import AutoModel, AutoTokenizer
                print("Downloading BERT model via transformers...")
                model = AutoModel.from_pretrained("microsoft/mdeberta-v3-base")
                tokenizer = AutoTokenizer.from_pretrained("microsoft/mdeberta-v3-base")
                model.save_pretrained(bert_model_path)
                tokenizer.save_pretrained(bert_model_path)
                print("✓ BERT model downloaded successfully via transformers")
            except Exception as e2:
                print(f"Failed to download BERT model: {e2}")
                raise
    else:
        print(f"✓ BERT model already exists at {bert_model_path}")
    
    # Скачивание ABSA модели
    if not is_absa_model_valid(absa_model_path):
        print(f"ABSA model not found or incomplete at {absa_model_path}. Downloading...")
        
        # Создаем директорию
        os.makedirs(absa_model_path, exist_ok=True)
        
        # URL для скачивания
        url = "https://huggingface.co/spaces/yangheng/PyABSA/resolve/main/checkpoints/Multilingual/ATEPC/fast_lcf_atepc_Multilingual_cdw_apcacc_85.1_apcf1_80.2_atef1_76.45.zip"
        zip_path = "/tmp/absa_model.zip"
        
        try:
            # Скачиваем ZIP-файл
            print(f"Downloading ABSA model from {url}...")
            urllib.request.urlretrieve(url, zip_path)
            print(f"Downloaded to {zip_path}")
            
            # Распаковываем
            print(f"Extracting to {absa_model_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(absa_model_path)
            
            # Удаляем ZIP-файл
            os.remove(zip_path)
            
            # Проверяем, не создалась ли вложенная папка
            extracted_items = os.listdir(absa_model_path)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(absa_model_path, extracted_items[0])):
                subfolder = os.path.join(absa_model_path, extracted_items[0])
                for item in os.listdir(subfolder):
                    os.rename(os.path.join(subfolder, item), os.path.join(absa_model_path, item))
                os.rmdir(subfolder)
                print("Flattened subdirectory structure")
            
            print("✓ ABSA model downloaded and extracted successfully")
            
        except Exception as e:
            print(f"Failed to download ABSA model: {e}")
            raise
    else:
        print(f"✓ ABSA model already exists at {absa_model_path}")
    
    # Финальная проверка
    print("\n=== Model Validation ===")
    print(f"BERT model valid: {is_bert_model_valid(bert_model_path)}")
    print(f"ABSA model valid: {is_absa_model_valid(absa_model_path)}")
    
    return True