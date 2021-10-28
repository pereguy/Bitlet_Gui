
import numpy  as np


bitlet_params = {
    'cc': dict(name='CC',  value=1, step=1, limits=[1, 65536], units='Cycles', factor=0), 
    'ct':dict(name='CT',  value=10.0, step=0.1, limits=[1.0, 100.0], units='ns',factor=-9), #10^-9
    'rows': dict(name='Rows', value=1024.0, step=8, limits=[16, 1024],factor=0), 
    # 'cols':dict(name='Columns',  value=32, step=32, limits=[32, 1024]),
    'mats': dict(name='MATs', value=1, step=1, limits=[1, 64], units='K',factor=3), # 2^10, 10^3
    'bw': dict(name='BW', value=1.0, step=0.1,limits=[0.1, 16.0], units='Tbit',factor=12), #10^12
    'dio': dict(name='DIO',  value=16, step=8, limits=[1, 256], units='bit',factor=0), 
    'ebitpim': dict(name='EbitPIM',  value=0.01, step=0.01, limits=[0.01, 1.0], units='pJ',factor=-12), #10^-12
    'ebitcpu': dict(name='EbitCPU', value=1.0, step=0.01, limits=[1.0, 100.0], units='pJ',factor=-12) #10^-12
}
VALUES = 2000
class Param:
    def __init__(self, name, limits, step, value=None, units=None, fixed=True, factor=1):
        self.name = name
        self.factor = factor
        self.min = limits[0] 
        self.max = limits[1] 
        self.step = step 
        self.units = units
        self.fixed = fixed
        self.value = value 

        
    # def is_valid(self):
    #     if not self.fixed: return True
    #     return self.value in self.range

    # def set_value(self,val):
    #     self.value = val
    #     return self.is_valid()
    
    def set_fixed(self,fixed):
        self.fixed = fixed
        # if not fixed:
        #     self.value = self.range

    def get_copy(self):
        new_obj = Param(name=self.name, limits=[self.min,self.max], step=self.step,
                        value=self.value, units=self.units, fixed=self.fixed)
        return new_obj

    def to_numpy(self, values):
        if self.fixed:
            return np.array([self.value])
        else:
            return  np.linspace(self.min, self.max, values)
    

class BitletParams:
    def __init__(self):
        self.cc = Param(**bitlet_params['cc'],fixed=False).to_numpy()
        self.ct = Param(**bitlet_params['ct'],fixed=False).to_numpy()
        self.bw = Param(**bitlet_params['bw'],fixed=False).to_numpy()
        self.rows = Param(**bitlet_params['rows'],fixed=False).to_numpy()
        self.mats = Param(**bitlet_params['mats'],fixed=False).to_numpy()
        self.dio = Param(**bitlet_params['dio'],fixed=False).to_numpy()
        self.ebitpim = Param(**bitlet_params['ebitpim'],fixed=False).to_numpy()
        self.ebitcpu = Param(**bitlet_params['ebitcpu'],fixed=False).to_numpy()
                             
    @classmethod
    def get_params(cls,parameter_list, x,y):
        model_params = BitletParams()
        x_axis = x.to_numpy()
        y_axis = y.to_numpy()
        x_axis, y_axis = np.meshgrid(x_axis,y_axis, copy=True)
        model_params.__setattr__(x.name.lower(), x_axis)
        model_params.__setattr__(y.name.lower(), y_axis)
        for pname, prm in parameter_list.items():
            model_params.__setattr__(pname,prm.value)
        return model_params
    