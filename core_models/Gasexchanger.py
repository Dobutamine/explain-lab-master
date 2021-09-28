import math

class Gasexchanger:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        self.flux_o2 = 0
        self.flux_co2 = 0
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the model
        self.model = model
        
        self.initialized = False
        
        self.update_interval = 0.015
        self.update_counter = 0
        self.modeling_stepsize = 0.0005
        
        # self.initialize()
  
    def model_step(self):
        if self.is_enabled:
            if (self.initialized == False):
                self.initialize()
            pass
            #self.exchange_gas()

            
    
    def initialize (self):
        self.comp_blood = self.model.components[self.comp_blood]
        self.comp_gas = self.model.components[self.comp_gas]
        self.modeling_interval = self.model.modeling_stepsize
        self.initialized = True
        print(self.comp_blood)
        
    def exchange_gas(self):
        
        self.flux_o2 = -0.00001 # (self.comp_blood.po2 - self.comp_gas.po2) * (self.dif_o2) * self.modeling_interval
        self.flux_co2 = (self.comp_blood.pco2 - self.comp_gas.pco2) * (self.dif_co2) * self.modeling_interval
        
        # change the oxygen content of the blood_compartment
        new_to2 = ((self.comp_blood.to2 * self.comp_blood.vol) - self.flux_o2) / self.comp_blood.vol
        if (new_to2 < 0):
            new_to2 = 0
        
        self.comp_blood.compound_concentrations[0] = new_to2
        self.comp_blood.to2 = new_to2
            
        # change the oxygen content of the gas_compartment
        new_co2 = (self.comp_gas.co2 * self.comp_gas.vol + self.flux_o2) / self.comp_gas.vol
        if (new_co2 < 0):
            new_co2 = 0
            
        # we have to update the fractions of o2 in the gas compartment
        self.comp_gas.fo2 = new_co2 / self.comp_gas.c_total_dry
        self.comp_gas.gas_fractions[self.comp_gas.o2_index] = self.comp_gas.fo2
        self.comp_gas.gas_concentrations[self.comp_gas.o2_index] = new_co2
        
        
        
#         # change the carbon dioxide content of the blood_compartment
#         new_tco2 = (self.comp_blood.tco2 * self.comp_blood.vol - self.flux_co2) / self.comp_blood.vol
#         if (new_tco2 < 0):
#             new_tco2 = 0
            
#         self.comp_blood.compound_concentrations[1] = new_tco2
#         self.comp_blood.tco2 = new_tco2
            
#         # change the carbon dioxide content of the gas_compartment
#         self.comp_gas.cco2 = (self.comp_gas.cco2 * self.comp_gas.vol + self.flux_co2) / self.comp_gas.vol
#         if (self.comp_gas.cco2 < 0):
#             self.comp_gas.cco2 = 0
        
#         # we have to update the fractions of co2 in the gas compartment
#         self.comp_gas.fco2 = self.comp_gas.cco2 / self.comp_gas.c_total_dry
#         self.comp_gas.gas_fractions[self.comp_gas.co2_index] = self.comp_gas.fco2
#         self.comp_gas.gas_concentrations[self.comp_gas.co2_index] = self.comp_gas.cco2
        
        
            
        
        
    
    