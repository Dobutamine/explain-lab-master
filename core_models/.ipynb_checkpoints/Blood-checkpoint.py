import math

class Blood:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # now inject the blood compounds in all model component types eligble for containing blood (as defined in the targets and target_label properties of this Blood class)
        for component_name, component in model.components.items():
            if ((component.model_type in self.target_models) and component.content == self.target_label):
                # now prepare the object for being a blood containing object
                self.initialize_blood_object(component)
                 
    def model_step(self):
        pass
    
    def initialize_blood_object (self, component):
        for compound_name, compound_concentration in self.compounds.items():
            # set the compound names in a list
            component.compound_names.append(compound_name)
            component.compound_concentrations.append(compound_concentration)
        
        self.to2_index = component.compound_names.index("to2")
        self.tco2_index = component.compound_names.index("tco2")
        
        setattr(component, 'mix_blood', self.mix_blood)
        setattr(component, 'initialized', True)
        setattr(component, 'to2', 0)
        setattr(component, 'tco2', 0)
        
    
    def mix_blood(self, dvol, comp_to, comp_from):
        for index, compound in enumerate(comp_to.compound_concentrations):
            current_conc = comp_to.compound_concentrations[index]
            current_vol = comp_to.vol
            d_compound = (comp_from.compound_concentrations[index] - current_conc) * dvol
            if current_vol > 0:
                comp_to.compound_concentrations[index] = (current_conc * current_vol + d_compound) / current_vol
            else:
                comp_to.compound_concentrations[index] = 0
        
        # store the to2 and tco2 for easy access
        comp_to.to2 = comp_to.compound_concentrations[self.to2_index]
        comp_to.tco2 = comp_to.compound_concentrations[self.tco2_index]
  
    


            