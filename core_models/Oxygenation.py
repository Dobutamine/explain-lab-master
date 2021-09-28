import math

class Oxygenation:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # get a reference to the rest of the model
        self.model = model
        
    def model_step(self):
        if self.is_enabled:
            pass
