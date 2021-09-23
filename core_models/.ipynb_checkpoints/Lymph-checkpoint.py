import math

class Lymph:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # now inject the lymph compounds into all compliance objects and time varying elastance objects containing lymph
        for component_name, component in model.components.items():
            if ((component.model_type == 'Compliance' or component.model_type == 'TimeVaryingElastance') and component.content == 'lymph'):
                for compound_name, compound_value in self.compounds.items():
                    setattr(component, compound_name, compound_value)
        
    def model_step(self):
        pass

            