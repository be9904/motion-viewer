from abc import ABC, abstractmethod

#####################################
# PLUGIN DECLARATION
#####################################

class Plugin(ABC):
    def __init__(self):
        print(f"{self.__class__.__name__}")

    # assemble all configurations and files
    @abstractmethod
    def assemble(self):
        pass

    # setup basic settings (window, gui, logs etc)
    @abstractmethod
    def init(self):
        pass

    # executed every frame
    @abstractmethod
    def update(self):
        pass

    # reset any modified parameters or files
    @abstractmethod
    def reset(self):
        pass

    # release runtime data
    @abstractmethod
    def release(self):
        pass