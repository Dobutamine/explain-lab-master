import math

class Container:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # properties
        self.name = ""                      # name of the compliance
        self.model_type = "Container"      # type of the model component
        self.content = ""                   # content of the component (blood/gas/lymph)
        self.is_enabled = True              # determines whether or not the compliance is enabled
        self.vol = 0                        # holds the volume in liters
        self.u_vol = 0                      # holds the unstressed volume in liters
        self.pres = 0                       # holds the transmural pressure in mmHg
        self.recoil_pressure = 0            # holds the recoil pressure in mmHg
        self.pres_outside = 0               # holds the pressure which is exerted on the compliance from the outside
        self.p_atm = 0
        self.el_base = 1                    # holds the baseline elastance
        self.el_k = 0                       # holds the constant for the non-linear elastance function
        self.initialized = False
    
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
    
        # get a reference to the model
        self.model = model
  
    def model_step(self):
        if self.is_enabled:
            self.calculate_pressure()

    def calculate_pressure(self):
        # first calculate the volume of the container
        self.vol = self.calculate_volume()
        
        # calculate the volume above the unstressed volume
        vol_above_unstressed = self.vol - self.u_vol

        # calculate the elastance, which is volume dependent in a non-linear way
        elastance = self.el_base + self.el_k * pow(vol_above_unstressed, 2)

        # calculate pressure in the compliance
        self.recoil_pressure = vol_above_unstressed * elastance

        # calculate the transmural pressure
        self.pres = self.recoil_pressure + self.pres_outside + self.p_atm
        
        # transfer the transmural pressures to the objects inside the container
        for enclosed_object in self.comps:
            self.model.components[enclosed_object].pres_outside = self.pres
        
    def calculate_volume(self):
        # iterate over the enclosed objects to calculate the volumes
        volume = 0
        for enclosed_object in self.comps:
            volume += self.model.components[enclosed_object].vol
            
        return volume
