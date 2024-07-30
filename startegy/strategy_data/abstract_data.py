from abc import ABC, abstractmethod


class AbstractData(ABC):
    def __init__(self, base_args):
        self.base_args = base_args


    @abstractmethod
    def read_data(self,cerebro):
        pass
