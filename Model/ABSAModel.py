from pyabsa import ATEPCCheckpointManager
from pyabsa import AspectTermExtraction as ATEPC
from pyabsa import ModelSaveOption, DeviceTypeOption,DatasetItem
from FileManager.FileManager import FileManager
from pyabsa.utils.logger import logger
from DatasetModels.AspectModel import Aspect
from DatasetModels.SampleModel import Sample
from DatasetModels.DatasetModel import Dataset
from Storage.DatabaseManager import DatabaseManager
import os
import re
class ABSAModel:
    NEW_SAVE_DIR = "./ProjectsStorage/"
    def __init__(self):
        """Class for ABSA model management
        """        
        self.model=ATEPCCheckpointManager.get_aspect_extractor("./Model/checkpoints/ATEPC_MULTILINGUAL_CHECKPOINT")
    

    def train(self, project_id, epochs=10, batch_size=1):
        """Model training

        Args:
            project_id (int): project identificator
            epochs (int): Number of epochs. Defaults to 10.
            batch_size (int): Size of batch. Defaults to 1.
        """        
        DBManager=DatabaseManager()
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        dataset_path=f"{self.NEW_SAVE_DIR[2:]}{dir_name}/dataset/dat"
        dataset_path=dataset_path.replace("/", "\\")
        project_dir=f'{self.NEW_SAVE_DIR}{dir_name}'
        model_dir=f'{project_dir}/Model/checkpoints'
        os.makedirs(model_dir, exist_ok="True")
        lg = logger.get_logger(log_path=f"{project_dir}/Model",log_name=f"logger",log_type='trainer')
        config = ATEPC.ATEPCConfigManager.get_atepc_config_multilingual()
        config.model = ATEPC.ATEPCModelList.FAST_LCF_ATEPC
        config.output_dim = 3
        config.pretrained_bert="microsoft/mdeberta-v3-base"
        config.evaluate_begin = 0
        config.max_seq_len = 512
        config.num_epoch=epochs
        config.batch_size=batch_size
        config.l2reg = 1e-8
        config.learning_rate = 2e-5
        config.seed = 42
        config.use_bert_spc = True
        config.use_amp = False
        config.cache_dataset = False
        config.logger=lg
        config.verbose=False
        config.model_path_to_save = model_dir
        config.path_to_save = model_dir
        self.model = ATEPC.ATEPCTrainer(config=config,
                                      dataset=dataset_path,
                                      checkpoint_save_mode=1,
                                      from_checkpoint="./Model/checkpoints/ATEPC_MULTILINGUAL_CHECKPOINT",
                                      path_to_save=model_dir,
                                      auto_device=True
                                      ).load_trained_model()
        
    def atepc(self, review):
        """Analyse review using model

        Args:
            review (str): review fro analysis

        Returns:
            dict: model prediction
        """        
        result = self.model.predict(review)
        return result
    
    def analyse_all_reviews(self, project_id):
        """Analyse all reviews in project

        Args:
            project_id (int): project identificator
        """
        DBManager=DatabaseManager()
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        data=FileManager.load_json(f"{self.NEW_SAVE_DIR}{dir_name}/reviews.json")
        dataset=Dataset()
        result = self.model.predict(data)
        for rev in result:
            new_samp=Sample(rev["sentence"])
            for ind, asp in enumerate(rev["aspect"]):
                new_asp=Aspect(asp, rev["sentiment"][ind])
                new_samp.add_aspect(new_asp)
            dataset.add_sample(new_samp)
        json_data=dataset.to_json()
        FileManager.save_json(f"{self.NEW_SAVE_DIR}{dir_name}/analysed_reviews.json",json_data)


    
    def load_model_from_file(self, project_id):
        """load trained model from project dictionary

        Args:
            project_id (int): project identificator
        """        
        DBManager=DatabaseManager()
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        path = f'{self.NEW_SAVE_DIR}{dir_name}/Model/checkpoints'
        entries = os.listdir(path)
        model_path = path + '/' + entries[-1]
        self.model = ATEPC.AspectExtractor(model_path)
    
    @staticmethod
    def update_info_from_logs(project_id):
        """Get training progress from logs

        Args:
            project_id (int): project identificator

        Returns:
            True: Successfuly readed logs
        """        
        NEW_SAVE_DIR = "./ProjectsStorage/"
        DBManager=DatabaseManager()
        dir_name=DBManager.get_project_by_id(project_id).dir_name
        path=f"{NEW_SAVE_DIR}{dir_name}/Model/logs/logger/trainer.log"
        if DBManager.get_operation_info(project_id, "Model training")["status"]=="Not started" or not(os.path.exists(path)):
            print(path)
            return False
        metrics = []
        max_epoch=-1
        all_epochs=1
        batch_size=0
        with open(path, 'r', encoding="UTF-8") as file:
            data=file.read()
            epoch_pattern="INFO: num_epoch:.+\n"
            result=re.findall(epoch_pattern, data)
            for log in result:
                all_epochs=int(log[len('INFO: num_epoch:'):log.index("	-->")])
                break
            batch_pattern="INFO: batch_size:.+\n"
            result=re.findall(batch_pattern, data)
            for log in result:
                batch_size=int(log[len("INFO: batch_size:"):log.index("	-->")])
                break
            pattern="PROGRESS:.+\n"
            result=re.findall(pattern, data)
            for log in result:
                metrics_per_epoch={}
                info=log.split("PROGRESS: ")[1][:-1]
                splitted=info.split("|")
                for part in splitted:
                    m = part.split(":")
                    if m[0] == "Epoch":
                        if max_epoch<int(m[1]):
                            max_epoch=int(m[1])
                        metrics_per_epoch[m[0].lower()]=int(m[1])
                    else:
                        metrics_per_epoch[m[0].lower()]=float(m[1])
                metrics+=[metrics_per_epoch]
        max_epoch+=1
        if DBManager.get_operation_info(project_id, "Model training")["status"]!="Done":
            DBManager.change_operation_info(project_id, "Model training", 2, 0.9*(max_epoch/all_epochs))
        for m in metrics:
            DBManager.create_model_train_row(project_id, m["epoch"], all_epochs, batch_size, m["apc-acc"], m["apc-f1"], m["ate-f1"])
        return True
