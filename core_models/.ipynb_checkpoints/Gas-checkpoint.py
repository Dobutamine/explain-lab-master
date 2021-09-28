import math

class Gas:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        self.target_models = ["Compliance"]

        self.p_atm = 760
        self.temp_settings = {}
        self.dry_air = {}
        self.compounds = {}
        
        # set the independent properties
        for key, value in args.items():
              setattr(self, key, value)
        
        # get a reference to the whole model
        self.model = model
        
        # define a list which contains all components holding gas
        self.gas_components = []
        
        # now transform the components with content gas into gas components
        for comp_name, comp in model.components.items():
            if ((comp.model_type in self.target_models) and comp.content == 'gas'):
                # now prepare the object for being a gas containing object
                setattr(comp, 'mix_gas', self.mix_gas)
                setattr(comp, 'p_atm', self.p_atm)
                setattr(comp, 'c_total', 0)
                setattr(comp, 'c_total_dry', 0)
                # set the gas compounds as attributes of the model component
                for compound, value in self.compounds.items():
                    setattr(comp, "f" + compound, value)
                    setattr(comp, "c" + compound, 0)
                    setattr(comp, "p" + compound, 0)
                # set the temperature and the water vapour pressure which is temperature dependent
                for temp in self.temp_settings:
                    if temp == comp.name:
                        setattr(comp, "temp", self.temp_settings[temp])
                        setattr(comp, "ph2o", self.calculate_water_vapour_pressure(self.temp_settings[temp]))
                
                
    def model_step(self):
        pass
    
    def calculate_water_vapour_pressure(self, temp):
        # calculate the water vapour pressure in air with temperature temp
        return math.pow(math.e, (20.386 - (5132 / (temp + 273)))) 
        
           
    def calculate_gas_composition(self, comp):
        # calculate the concentration of all molecules (including h2o) in the air at the current pressure, volume and temperarure of 
        comp.c_total = ((comp.pres * comp.vol) / (self.gas_constant * (273.15 + comp.temp)) / comp.vol) * 1000 
        comp.c_total_dry = (((comp.pres - comp.ph2o) * comp.vol) / (self.gas_constant * (273.15 + comp.temp)) / comp.vol) * 1000
        
        # now calculate the partial pressures and concentrations of the compounds
        for compound in self.compounds.keys():
            # get the fraction
            fraction = getattr(comp, "f" + compound)
            # calculate the partial pressures
            setattr(comp, "p" + compound, fraction * (comp.pres - comp.ph2o))
            # calculate the gas concentrations
            setattr(comp, "c" + compound, fraction * comp.c_total_dry)
    
    def mix_gas(self, dvol, comp_to, comp_from):
        # mix the blood only if the blood model is enabled
        if self.is_enabled:
            # iterate over all the blood compounds
            for compound in self.compounds.keys():
                fraction = "f" + compound
                # get the compound concenrtation in the components
                comp_to_fraction = getattr(comp_to, fraction)
                comp_from_fraction = getattr(comp_from, fraction)
                # get the volume
                volume = comp_to.vol
                # calculate the change in compound concentration
                d_fraction = (comp_from_fraction - comp_to_fraction) * dvol
                # update the new compound concentration in the component receiving the blood
                if volume > 0:
                    new_fraction = (comp_to_fraction * volume + d_fraction) / volume
                else:
                    new_fraction = 0
                # store the new concentration in the component receiving the blood
                setattr(comp_to, fraction, new_fraction)

            
            self.calculate_gas_composition(comp_to)
            
           
                
    