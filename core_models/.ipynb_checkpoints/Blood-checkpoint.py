import math

class Blood:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        self.target_models = ["Compliance", "TimeVaryingElastance"]
        self.compounds = {}
        
        self.active_comp = {}

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
                
    def acidbase(self, comp):
        pass
    
    def net_charge_plasma(self, hp):
        pass
    
    def oxygenation(self, comp):
        pass
    
    def oxygen_dissociation_curve(self, po2):
        pass
    
    def brent_root_finding(self, f, x0, x1, max_iter, tolerance):
        
        fx0 = f(x0)
        fx1 = f(x1)
 
        if (fx0 * fx1) > 0:
            return -1
 
        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0
            fx0, fx1 = fx1, fx0
 
        x2, fx2 = x0, fx0
 
        mflag = True
        steps_taken = 0
 
        while steps_taken < max_iter and abs(x1-x0) > tolerance:
            fx0 = f(x0)
            fx1 = f(x1)
            fx2 = f(x2)

            if fx0 != fx2 and fx1 != fx2:
                L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
                L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
                L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
                new = L0 + L1 + L2

            else:
                new = x1 - ( (fx1 * (x1 - x0)) / (fx1 - fx0) )

            if ((new < ((3 * x0 + x1) / 4) or new > x1) or
                (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2)) or
                (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2)) or
                (mflag == True and (abs(x1 - x2)) < tolerance) or
                (mflag == False and (abs(x2 - d)) < tolerance)):
                new = (x0 + x1) / 2
                mflag = True

            else:
                mflag = False

            fnew = f(new)
            d, x2 = x2, x1

            if (fx0 * fnew) < 0:
                x1 = new
            else:
                x0 = new

            if abs(fx0) < abs(fx1):
                x0, x1 = x1, x0

            steps_taken += 1

        return x1
    
    
    
    