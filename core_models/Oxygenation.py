import math

class Oxygenation:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # set local properties
        self.brentAccuracy = 1e-8
        self.maxIterations = 100
        self.lefto2 = 0.01
        self.righto2 = 1000
        self.alpha_o2p = 0.0095
        self.mmoltoml = 22.2674 # convert mmol to ml  (1 mmol of gas occupies 22.2674 ml)

        self.to2 = 0
        self.so2 = 0
        self.co2p = 0
        self.po2 = 0
        self.ph_odc = 7.4
        self.hb_odc = 10
        self.be_odc = 0.0
        self.temp_odc = 37.0
        self.dpg_odc = 5.0

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # get a reference to the rest of the model
        self.model = model
        
    def model_step(self):
        pass
    
    def calculate_oxygenation_from_to2(self, comp):
        
        # get the to2 from the component
        self.to2 = comp.to2
        
        # find the po2 where the difference between the to2 and the target to2 is zero mmol/l and the pO2 in kPa
        result = self.brent(self.dto2, self.lefto2, self.righto2, self.maxIterations, self.brentAccuracy)
        
        # set the oxygenation attributes
        
        self.calc_oxygenation(to2, result[0])
        
    
    def calc_oxygenation (self, to2, po2):
        co2p = po2 * self.alpha_o2p
        so2 = self.odc(po2)
        return(so2, po2)
    
    def odc (self, po2):
        a = 1.04 * (7.4 - self.ph_odc) + 0.005 * self.be_odc + 0.07 * (self.dpg_odc - 5.0)
        b = 0.055 * (self.temp_odc + 273.15 - 310.15)
        y0 = 1.875
        x0 = 1.875 + a + b
        h0 = 3.5 + a
        k = 0.5343
        x = math.log(po2, math.e)
        y = x - x0 + h0 * math.tanh(k * (x - x0)) + y0
        return 1.0 / (math.pow(math.e, -y) + 1.0);

    def dto2(self, po2):
        so2 = self.odc(po2)
        to2_new_estimate = (0.02325 * po2 + 1.36 * (self.hb_odc / 0.6206) * so2) * 10.0
        dto2 = self.to2 - to2_new_estimate / self.mmoltoml

        return dto2
    
    def brent(self, f, x0, x1, max_iter, tolerance):
 
        fx0 = f(x0)
        fx1 = f(x1)
 
        assert (fx0 * fx1) <= 0, "Root not bracketed" 
 
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

        return x1, steps_taken

