import pytest
from contextlib import nullcontext as does_not_raise
from DatasetModels.DatasetModel import Dataset
from DatasetModels.SampleModel import Sample
from DatasetModels.AspectModel import  Aspect
from custom_exceptions import argument_exception, operation_exception
"""Тесты для классов датасета, примера и аспекта"""
class TestDatasetModels:
    """Проверка создания объекта аспект"""
    @pytest.mark.parametrize("term, sent, result", [
        ("food", "Positive", does_not_raise()),
        ("service", "Negative", does_not_raise()),
        ("restaurant", "Neutral", does_not_raise()),
        (123, "Neutral", pytest.raises(argument_exception)),
        ("food", 123, pytest.raises(argument_exception)),
        ("food", "123", pytest.raises(argument_exception))
    ])
    def test_aspect_model_creation(self,term ,sent, result):
        with result:
            asp=Aspect(term, sent)
            assert asp.term == term
            assert asp.sentiment == sent
    
    """Проверка создания объекта пример"""
    @pytest.mark.parametrize("review, aspects, result", [
        ("Great food", [Aspect("food")], does_not_raise()),
        ("Great food, bad service", [Aspect("food"), Aspect("service")], does_not_raise()),
        (123, [], pytest.raises(argument_exception)),
        ("food", 123, pytest.raises(argument_exception)),
        ("Great food", [Aspect("service")], pytest.raises(IndexError))
    ])
    def test_sample_model_creation(self, review, aspects, result):
        with result:
            samp=Sample(review, aspects)
            assert samp.review == review
            assert samp.aspects[0] == aspects[0]
            assert samp.aspects[-1] == aspects[-1]
    
    """Проверка преобразования json в пример"""
    def test_sample_convert_from_json(self):
        json_format=["Great food", {"food":"Positive"}]
        samp=Sample.from_json(json_format)
        assert samp.review == json_format[0]
        assert samp.aspects[0].term == "food"
    
    """Проверка преобразования пример в json"""
    def test_sample_convert_to_json(self):
        json_format=["Great food", {"food":"Positive"}]
        samp=Sample("Great food", [Aspect("food", "Positive")])
        new_json=samp.to_json()
        assert json_format==new_json
    

    """Проверка преобразования json в датасет"""
    def test_dataset_convert_from_json(self):
        json_format=[["Great food", {"food":"Positive"}], ["Bad service", {"service":"Negative"}]]
        dataset=Dataset.from_json(json_format)
        assert dataset.samples[0].review == json_format[0][0]
        assert dataset.samples[-1].review == json_format[-1][0]
    
    """Проверка преобразования датасета в json"""
    def test_dataset_convert_to_json(self):
        json_format=[["Great food", {"food":"Positive"}], ["Bad service", {"service":"Negative"}]]
        dataset=Dataset(samples= [Sample("Great food", [Aspect("food", "Positive")]),Sample("Bad service", [Aspect("service", "Negative")])] )
        assert dataset.to_json() == json_format

    """Проверка создания объекта датасет"""
    @pytest.mark.parametrize("domain, samples, result", [
        ("restaurant", [Sample("Great food", [Aspect("food")])], does_not_raise()),
        (123, [Sample("Great food", [Aspect("food")])], pytest.raises(argument_exception)),
        ("restaurant", 123, pytest.raises(argument_exception)),
        ("restaurant", [123], pytest.raises(argument_exception))
    ])
    def test_dataset_model_creation(self,domain, samples, result):
        with result:
            dataset=Dataset(domain,samples)
            print(dataset.samples)
            assert dataset.domain == domain
            assert dataset.samples[0].review == samples[0].review
            