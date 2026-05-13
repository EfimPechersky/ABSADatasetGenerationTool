import json
from custom_exceptions import argument_exception, operation_exception
from DatasetModels.SampleModel import Sample
from DatasetModels.AspectModel import Aspect

class Dataset:

    __samples: list
    __domain: str
    def __init__(self, domain: str = "", samples: list = None):
        """Dataset for ABSA training

        Args:
            domain (str): domain of the reviews Defaults to "".
            samples (list): list of samples for training Defaults to None.
        """        
        self.domain = domain
        if samples != None:
            self.samples = samples
        else:
            self.samples = []
    
    @property
    def domain(self):
        return self.__domain
    
    @domain.setter
    def domain(self, value):
        if not isinstance(value, str):
            raise argument_exception("Wrong type of domain")
        self.__domain = value
    
    @property
    def samples(self):
        return self.__samples
    
    @samples.setter
    def samples(self, value):
        self.__samples = []
        if not isinstance(value, list):
            raise argument_exception("Wrong type of samples")
        for samp in value:
            self.add_sample(samp)
    
    def add_sample(self, sample):
        """add sample to dataset

        Args:
            sample (Sample): sample

        Raises:
            argument_exception: Wrong type of sample!
        """        
        if not isinstance(sample, Sample):
            raise argument_exception("Wrong type of sample!")
        self.__samples.append(sample)
    
    def to_json(self):
        """Convert dataset to json format

        Returns:
            (list): converted dataset
        """        
        result = []
        for samp in self.samples:
            result += [samp.to_json()]
        return result
    
    def from_json(json):
        """Create dataset from json

        Args:
            json (list): json format of dataset

        Returns:
            Dataset: converted dataset
            None: cannot convert dataset
        """        
        new_dataset = Dataset()
        if isinstance(json, list):
            for samp in json:
                new_samp = Sample.from_json(samp)
                if new_samp:
                    new_dataset.add_sample(new_samp)
            return new_dataset
        else:
            return None
    
    def to_dat(self):
        """Convert dataset to format for training

        Returns:
            str: converted dataset
        """        
        all_dats = []
        for sample in self.samples:
            all_dats += sample.to_dat()
        
        text = ""
        for i in range(len(all_dats)):
            for j in range(len(all_dats[i])):
                text += " ".join(all_dats[i][j])
                text += '\n'
            text += '\n'
        
        return text
    
    @staticmethod
    def template_dataset():
        """Template dataset, contains all types of sentiments

        Returns:
            Dataset: template dataset
        """        
        pos_sample = Sample(review="Отличные товары!", aspects=[Aspect("товары", "Positive")])
        neg_sample = Sample(review="Ужасные товары!", aspects=[Aspect("товары", "Negative")])
        neu_sample = Sample(review="Нормальные товары.", aspects=[Aspect("товары", "Neutral")])
        dt = Dataset("products", [pos_sample, neg_sample, neu_sample])
        return dt
    
    def __str__(self):
        return f"{self.to_json()}"