from pyabsa import ATEPCCheckpointManager
from pyabsa import AspectTermExtraction as ATEPC
from pyabsa import ModelSaveOption, DeviceTypeOption,DatasetItem
"""Класс, описывающий модель ABSA"""
class ABSAModel:
    model=ATEPCCheckpointManager.get_aspect_extractor("multilingual")
    """Конструктор"""
    def __init__(self):
        self.model=ATEPCCheckpointManager.get_aspect_extractor("multilingual")
    
    """Обучение"""
    def train(self,epochs=10, batch_size=1, dataset_path="./datasets/custom"):
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
        self.model = ATEPC.ATEPCTrainer(config=config,
                                      dataset=dataset_path,
                                      checkpoint_save_mode=1,
                                      from_checkpoint="multilingual",
                                      auto_device=True
                                      ).load_trained_model()