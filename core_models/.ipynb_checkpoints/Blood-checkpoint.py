import math

class Blood:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        self.target_models = ["Compliance", "TimeVaryingElastance"]
        self.compounds = {}

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the whole model
        self.model = model
        
        # define a list which contains all components holding gas
        self.blood_components = []
        
        # now inject transform the components with content blood into blood components
        for comp_name, comp in model.components.items():
            if ((comp.model_type in self.target_models) and comp.content == 'blood'):
                # now transform the model component into a blood containing object
                setattr(comp, 'mix_blood', self.mix_blood)
                setattr(comp, 'so2', 80)
                # set the blood compounds as attributes of the model component
                for compound, value in self.compounds.items():
                    setattr(comp, compound, value)
                    
                 
    def model_step(self):
        pass
        
    
    def mix_blood(self, dvol, comp_to, comp_from):
        # mix the blood only if the blood model is enabled
        if self.is_enabled:
            # iterate over all the blood compounds
            for compound in self.compounds.keys():
                # get the compound concenrtation in the components
                comp_to_conc = getattr(comp_to, compound)
                comp_from_conc = getattr(comp_from, compound)
                # get the volume
                volume = comp_to.vol
                # calculate the change in compound concentration
                d_compound = (comp_from_conc - comp_to_conc) * dvol
                # update the new compound concentration in the component receiving the blood
                if volume > 0:
                    new_conc = (comp_to_conc * volume + d_compound) / volume
                else:
                    new_conc = 0
                # store the new concentration in the component receiving the blood
                setattr(comp_to, compound, new_conc)
  
    


            