import math

class Breathing:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the local properties
        self.spont_breathing_enabled = True
        self.spont_resp_rate = 35
        self.ref_minute_volume = 0.63
        self.ref_tidal_volume = 0.018
        self.target_minute_volume = 0.630
        self.target_tidal_volume = 0.018
        self.vtrr_ratio = 0.00038
        self.resp_muscle_pressure = 0
        self.max_amp = 50
        self.breath_duration = 1000
            
        self._amp = 8.0
        self._temp_min_volume = 10000;
        self._temp_max_volume = -10000;
        self._volume_time_counter = 0;
        self._breath_timer_period = 0;
        self._breath_timer_counter = 0;
        self._volume_time_counter = 0
        
        self.tidal_volume = 0;
        self.minute_volume = 0;
    
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # get a reference to the rest of the model
        self.model = model
  
    def model_step(self):
        if self.is_enabled:
            self.breathing_cycle()
            

    def breathing_cycle(self):
        # determine the breathing timings
        if self.spont_resp_rate > 0 and self.spont_breathing_enabled:
            self._breath_timer_period = 60 / self.spont_resp_rate
        else:
            self._breath_timer_period = 60
            
        # calculate the respiratory rate depending on the target minute volume and the vt_rr ratio
        self.vt_rr_controller()
        
        # is it time for a new breath yet?
        if (self._breath_timer_counter > self._breath_timer_period):
            self.start_breath()
            
        # generate the muscle signal
        if self.spont_resp_rate > 0 and self.spont_breathing_enabled:
            self.resp_muscle_pressure = self.generate_muscle_signal()
        else:
            self.resp_muscle_pressure = 0
            
        # transfer the respiratory muscle force to the chestwalls
        for target in self.targets:
            self.model.components[target].pres_outside = self.resp_muscle_pressure
        
        # store the current volumes
        volume = self.model.components["ALL"].vol + self.model.components["ALR"].vol
        
        if volume > self._temp_max_volume:
            self._temp_max_volume = volume
        if volume < self._temp_min_volume:
            self._temp_min_volume = volume
            
        # calculate the volumes if not breathing quickly enough
        if self._volume_time_counter > 5.0:
            self.calculate_volumes()
            

        #increase the timers
        self._volume_time_counter += self.model.modeling_stepsize;
        self._breath_timer_counter += self.model.modeling_stepsize;
            

    def calculate_volumes(self):
        # calculate the tidal and minute volumes
        self.tidal_volume = self._temp_max_volume - self._temp_min_volume;
        self.minute_volume = self.tidal_volume * self.spont_resp_rate;

        # reset max and mins
        self._temp_min_volume = 10000;
        self._temp_max_volume = -10000;

        # reset the volumes counter
        self._volume_time_counter = 0;
    
    def start_breath(self):
        
        # calculate the current tidal and minute volume
        self.calculate_volumes()

        # has the target tidal volume been reached or exceeded?
        d_tv = self.tidal_volume - self.target_tidal_volume

        # adjust the respiratory power to the resp muscles
        if d_tv < -0.0001:
            self._amp -= 0.05 * d_tv * 1000
            
        if self._amp > self.max_amp:
            self._amp = self.max_amp;
      

        if d_tv > 0.0001:
            self._amp -= 0.05 * d_tv * 1000
      
        if self._amp < 0:
            self._amp = 0;

        # reset the breathing timer
        self._breath_timer_counter = 0;
    
    def generate_muscle_signal(self):
         return (-self._amp * math.exp(-25 * (math.pow(self._breath_timer_counter - self.breath_duration / 2, 2) / math.pow(self.breath_duration, 2))));

    
    def vt_rr_controller(self):
        # calculate the spontaneous resp rate depending on the target minute volume (from ANS) and the set vt-rr ratio
        self.spont_resp_rate = math.sqrt(self.target_minute_volume / self.vtrr_ratio)
        
        # calculate the target tidal volume depending on the target resp rate and target minute volume (from ANS)
        self.target_tidal_volume = self.target_minute_volume / self.spont_resp_rate;
