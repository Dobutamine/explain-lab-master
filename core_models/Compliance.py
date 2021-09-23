import math

class Compliance:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()
    
    # properties
    self.name = ""                      # name of the compliance
    self.model_type = "Compliance"      # type of the model component
    self.content = ""                   # content of the component (blood/gas/lymph)
    self.compound_names = []            # compound names of the model component.
    self.compound_concentrations = []   # compound concentrations of the model component
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
    
    # set the independent properties (name, description, model_type, content, is_enabled, vol, u_vol, el_base, el_k) from the JSON configuration file
    for key, value in args.items():
      setattr(self, key, value)

    # get a reference to the model to access other model components
    self.model = model

  def model_step (self):
    # during every model step the transmural pressure is calculates
    self.calculate_pressure()
        
  def calculate_pressure (self):
    if self.is_enabled:
      # calculate the volume above the unstressed volume
      vol_above_unstressed = self.vol - self.u_vol

      # calculate the elastance, which is volume dependent in a non-linear way
      elastance = self.el_base + self.el_k * pow(vol_above_unstressed, 2)

      # calculate pressure in the compliance
      self.recoil_pressure = vol_above_unstressed * elastance

      # calculate the transmural pressure
      self.pres = self.recoil_pressure + self.pres_outside + self.p_atm


  def volume_in (self, dvol, comp_from):
    # this method is called when volume is added to this components
    if self.is_enabled:
      # add volume
      self.vol += dvol

      # mix the content of the components depending on what they contain (blood/gas/lymfe)
      if self.content == 'blood':
        # mix the blood
        self.mix_blood(dvol, self, comp_from)
    
      if self.content == 'gas':
        # use the gas mixing function of the gas model to mix the gas
        self.mix_gas(dvol, self, comp_from)

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def volume_out (self, dvol, comp_from):
    # this method is called when volume is removed from this components
    if self.is_enabled:
      # add volume
      self.vol -= dvol

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def protect_mass_balance (self):
    if (self.vol < 0):
      # if there's a negative volume it might corrupt the mass balance of the model so we have to return the amount of volume which could not be displaced to the caller of this function
      _nondisplaced_volume = -self.vol
      # set the current volume to zero
      self.vol = 0
      # return the amount volume which could not be removed
      return _nondisplaced_volume
    else:
      # massbalance is guaranteed
      return 0