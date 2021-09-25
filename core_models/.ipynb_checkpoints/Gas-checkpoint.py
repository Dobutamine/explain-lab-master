import math

class Gas:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
              setattr(self, key, value)
        
        self.gas_components = []
        
        # now inject the gas compound fractions in all model component containing gas (as defined in the targets and target_label properties of this Gas class)
        for component_name, component in model.components.items():
            if ((component.model_type in self.target_models) and component.content == self.target_label):
                # now prepare the object for being a gas containing object
                self.initialize_gas_component(component)
                self.gas_components.append(component)
                
  
    def model_step(self):
        if (self.is_enabled):
            for gas_component in self.gas_components:
                self.calculate_gas_composition(gas_component)
    
    def initialize_gas_component (self, component):
        # first set the attributes which are going to hold the gas names, fractions, concentrations and the partial pressures
        setattr(component, 'gas_names', [])
        setattr(component, 'gas_fractions', [])
        setattr(component, 'gas_concentrations', [])
        setattr(component, 'gas_partial_pressures', [])
        setattr(component, 'c_total', 0)
        setattr(component, 'c_total_dry', 0)
        setattr(component, 'temp', 37)
        setattr(component, 'p_atm', self.p_atm)
        setattr(component, 'po2', 0)
        setattr(component, 'pco2', 0)
        setattr(component, 'co2', 0)
        setattr(component, 'cco2', 0)
        setattr(component, 'fo2', 0)
        setattr(component, 'fco2', 0)
        setattr(component, 'ph2o', 0)
        setattr(component, "fsum", 0)
        
        
        # now we have to intialize the lists with all the initial values from dry air
        counter = 0
        for gas_name, gas_fraction in self.dry_air.items():
            # set the gas names in the list
            component.gas_names.append(gas_name)
            index_name = gas_name[1:] + '_index'
            setattr(component, index_name, counter)
            setattr(self, index_name, counter)
            counter += 1
            # set the gas fractions in the list
            component.gas_fractions.append(gas_fraction)
            # set the concentrations and partial pressures to zero for now
            component.gas_concentrations.append(0)
            component.gas_partial_pressures.append(0)
        
        # now apply the temperature settings to the component
        for temp in self.temp_settings:
            if temp == component.name:
                setattr(component, "temp", self.temp_settings[temp])
                setattr(component, "ph2o", self.calculate_water_vapour_pressure(self.temp_settings[temp]))
        
        # first calculate the pressure in the component
        component.calculate_pressure()
        
        # now calculate the gas partial pressures and concentrations of the gasses from the fractions
        self.calculate_gas_composition_from_fractions(component)
        
        # inject the mix_gas method in the compliance/time_varying_elastance object. This object now exposes the mix_gas method.
        setattr(component, 'mix_gas', self.mix_gas)
        setattr(component, 'initialized', True)
    
    def calculate_water_vapour_pressure(self, temp):
        # due to the water vapour production, molecules are added to the component depending on the temperature, at the same time water molecules are removed by breathing.
        return math.pow(math.e, (20.386 - (5132 / (temp + 273)))) 
        
    
    def calculate_gas_composition_from_fractions(self, component):
        # calculate the concentration of all molecules in the component including h2o at the current pressure, volume and temperarure of the component in mmol/l
        component.c_total = ((component.pres * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000
        component.c_total_dry = (((component.pres - component.ph2o) * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000
        
        # now get the fractions of the other compounds (o2, co2, argon, n2, h2o) of dry air and calculate the partial pressure and gas concentrations of the gas
        for index, fraction in enumerate(component.gas_fractions):
            # calculate the partial pressure of gas of moist air (so where part of the pressure is taken up by water vapour)
            component.gas_partial_pressures[index] = fraction * (component.pres - component.ph2o)
            # calculate concentration of gas in the component
            component.gas_concentrations[index] = fraction * component.c_total_dry

        component.fsum = sum(component.gas_fractions)
        
    def calculate_gas_composition(self, component):
        # first check whether the gas component has been initialized
        if component.initialized == False:
            self.initialize_gas_component(component)
            
        # calculate the concentration of all molecules (including h2o) in the air at the current pressure, volume and temperarure of the component in mmol/l
        component.c_total = ((component.pres * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000 
        component.c_total_dry = (((component.pres - component.ph2o) * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000
        
        # now calculate the new fractions of the other compounds (o2, co2, argon, n2)
        for index, fraction in enumerate(component.gas_fractions):
            # calculate the partial pressures
            component.gas_partial_pressures[index] = fraction * (component.pres - component.ph2o)
            # calculate the gas concentrations
            component.gas_concentrations[index] = fraction * component.c_total_dry
        
        # store the po2 and pco2 for easy access
        component.po2 = component.gas_partial_pressures[self.o2_index]
        component.pco2 = component.gas_partial_pressures[self.co2_index]
#         component.co2 = component.gas_concentrations[self.o2_index]
#         component.cco2 = component.gas_concentrations[self.co2_index]
#         component.fo2 = component.gas_fractions[self.o2_index]
#         component.fco2 = component.gas_fractions[self.co2_index]
#         component.fsum = sum(component.gas_fractions)

            
    def mix_gas(self, dvol, comp_to, comp_from):
        # check whether the compartments are initialized and if so mix the gasses using the fractions
        if (comp_to.initialized and comp_from.initialized):
            # calculate the new concentrations
            for index, concentration in enumerate(comp_to.gas_fractions):
                # get the concentrations
                frac_to = comp_to.gas_fractions[index]
                frac_from = comp_from.gas_fractions[index]
                # calculate the change in concentration
                d_compound = (frac_from - frac_to) * dvol
                comp_to.gas_fractions[index] = (frac_to * comp_to.vol + d_compound) / comp_to.vol
            
           
                
    