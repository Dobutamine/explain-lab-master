import math

class Gas:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
              setattr(self, key, value)
                
        # now inject the gas compound fractions in all model component types eligble for containing gas (as defined in the targets and target_label properties of this Gas class)
        for component_name, component in model.components.items():
            if ((component.model_type in self.target_models) and component.content == self.target_label):
                # now prepare the object for being a gas containing object
                self.initialize_gas_object(component)
  
    def model_step(self):
        pass
    
    def initialize_gas_object (self, component):
        for compound_name, compound_concentration in self.compounds.items():
            # set the compound names in a list
            component.compound_names.append(compound_name)
            # set the compound value in a list
            component.compound_concentrations.append(compound_concentration)
            # inject the mix_gas method in the compliance/time_varying_elastance object. This object now exposes the mix_gas method.
        setattr(component, 'mix_gas', self.mix_gas)
        setattr(component, 'initialized', True)
        
    def mix_gas(self, dvol, comp_to, comp_from):
        pass
    