import math

class Gas:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
              setattr(self, key, value)
        
        self.gas_components = []
        
        # now inject the gas compound fractions in all model component types eligble for containing gas (as defined in the targets and target_label properties of this Gas class)
        for component_name, component in model.components.items():
            if ((component.model_type in self.target_models) and component.content == self.target_label):
                # now prepare the object for being a gas containing object
                self.initialize_gas_component(component)
                self.gas_components.append(component)
                
        # get all the gas compartments
        
  
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
        setattr(component, 'temperature', 37)
        setattr(component, 'c_total', 0)
        setattr(component, 'fh2o', 0)
        setattr(component, 'temp', 37)
        setattr(component, 'p_atm', self.p_atm)
        
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
        
        # now apply the fh2o and temperature settings 
        for fh2o in self.fh2o_settings:
            if fh2o == component.name:
                setattr(component, "fh2o", self.fh2o_settings[fh2o])
        
        for temp in self.temp_settings:
            if temp == component.name:
                setattr(component, "temp", self.temp_settings[temp])
        
        # first calculate the pressure in the component
        component.calculate_pressure()
        
        # now calculate the composition of the gasses from the fractions
        self.calculate_gas_composition_from_fractions(component)
        
        # inject the mix_gas method in the compliance/time_varying_elastance object. This object now exposes the mix_gas method.
        setattr(component, 'mix_gas', self.mix_gas)
        setattr(component, 'initialized', True)
    
    def calculate_gas_composition_from_fractions(self, component):
        # calculate the concentration of all molecules in the air at the current pressure, volume and temperarure of the component in mmol/l
        component.c_total = ((component.pres * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000
        
        # from the h2o fraction we can calculate the concentration and partial pressure of h2o in this component
        component.gas_concentrations[self.h2o_index] = component.fh2o * component.c_total
        component.gas_partial_pressures[self.h2o_index] = component.fh2o * component.pres
        
        # now calculate the new fractions (now H2O has been added) of wet air of the other compounds (o2, co2, argon, n2)
        for index, fraction in enumerate(component.gas_fractions):
            # convert the dry air fractions to the wet air fractions
            fraction = fraction - fraction * component.fh2o
            # store the new fraction
            component.gas_fractions[index] = fraction
            # calculate the new concentrations and partial pressures
            component.gas_concentrations[index] = fraction * component.c_total
            component.gas_partial_pressures[index] = fraction * component.pres
        
    def calculate_gas_composition(self, component):
        # first check whether the gas component has been initialized
        if component.initialized == False:
            self.initialize_gas_component(component)
            
        # check whether this gas component has a fixed composition
        if component.fixed_composition:
            # determine the composition from the fixed fraction
            self.calculate_gas_composition_from_fractions(component)
        else:
            # calculate the concentration of all molecules in the air at the current pressure, volume and temperarure of the component in mmol/l
            component.c_total = ((component.pres * component.vol) / (self.gas_constant * (273.15 + component.temp)) / component.vol) * 1000
            
            # from the h2o fraction we can calculate the concentration and partial pressure of h2o in this component
            component.gas_concentrations[self.h2o_index] = component.fh2o * component.c_total
            component.gas_partial_pressures[self.h2o_index] = component.fh2o * component.pres
            
            # now calculate the new fractions (now H2O has been added) of wet air of the other compounds (o2, co2, argon, n2)
            for index, fraction in enumerate(component.gas_fractions):
                # convert the dry air fractions to the wet air fractions
                fraction = component.gas_fractions[index]
                concentration = component.gas_concentrations[index]    
                # calculate the dry gas fractions
                fraction = concentration / component.c_total
                # convert the dry air fractions to wet air fractions
                fraction = fraction - (fraction * component.fh2o)
                # calculate the partial pressures
                component.gas_partial_pressures[index] = fraction * component.pres                
                # store the new fraction
                component.gas_fractions[index] = fraction
            
    def mix_gas(self, dvol, comp_to, comp_from):
        # check whether the compartments are initialized
        if (comp_to.initialized and comp_from.initialized):
            # calculate the new concentrations
            for index, concentration in enumerate(comp_to.gas_concentrations):
                # get the concentrations
                cc_to = comp_to.gas_concentrations[index]
                cc_from = comp_from.gas_concentrations[index]
                # calculate the change in concentration
                d_compound = (cc_from - cc_to) * dvol
                comp_to.gas_concentrations[index] = (cc_to * comp_to.vol + d_compound) / comp_to.vol
                
    