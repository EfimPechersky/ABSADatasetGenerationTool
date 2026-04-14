from pyabsa import ATEPCCheckpointManager
from pyabsa import AspectTermExtraction as ATEPC
from pyabsa import ModelSaveOption, DeviceTypeOption,DatasetItem
from pyabsa.utils.logger import logger
import os
"""Класс, описывающий модель ABSA"""
class ABSAModel:
    """Конструктор"""
    def __init__(self):
        self.model=ATEPCCheckpointManager.get_aspect_extractor("./Model/checkpoints/ATEPC_MULTILINGUAL_CHECKPOINT")
    
    """Обучение"""
    def train(self, code, epochs=10, batch_size=1, dataset_path="./datasets/custom"):
        lg = logger.get_logger(log_path="./Model",log_name=f"custom_{code}",log_type='trainer')
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
        model_dir=f'./Model/checkpoints/model_{code}'
        os.makedirs(model_dir, exist_ok="True")
        config.logger=lg
        config.verbose=False
        config.model_path_to_save=f'./Model/checkpoints/model_{code}'
        config.path_to_save = f'./Model/checkpoints/model_{code}'
        self.model = ATEPC.ATEPCTrainer(config=config,
                                      dataset=dataset_path,
                                      checkpoint_save_mode=1,
                                      from_checkpoint="./Model/checkpoints/ATEPC_MULTILINGUAL_CHECKPOINT",
                                      path_to_save=f'./Model/checkpoints/model_{code}',
                                      auto_device=True
                                      ).load_trained_model()
        
    def atepc(self, review):
        result = self.model.predict(review)
        return result
    
    def load_model_from_file(self, code):
        path = f'./Model/checkpoints/model_{code}'
        entries = os.listdir(path)
        model_path = path + '/' + entries[0]
        self.model = ATEPC.AspectExtractor(model_path)
        
