# from abc import ABCMeta, abstractmethod


# class Strip(metaclass=ABCMeta):
class Strip:

    """Abstract base class for LED strips."""

    # @abstractmethod
    def __len__(self):
        raise NotImplementedError

    # @abstractmethod
    def __setitem__(self, index, value):
        raise NotImplementedError

    # @abstractmethod
    def __getitem__(self, index):
        raise NotImplementedError

    def fill(self, color):
        raise NotImplementedError

    # @abstractmethod
    def show(self):
        raise NotImplementedError

