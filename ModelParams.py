
import numpy  as np


bitlet_params = {
    'cc': dict(name='CC',  value=1.00, step=1.0, limits=[1.0, 65536.0]),
    'ct':dict(name='CT',  value=0.1, step=0.1, limits=[0.1, 100], units='ns'),
    'rows': dict(name='Rows', value=32, step=32, limits=[32, 1024]),
    # 'cols':dict(name='Columns',  value=32, step=32, limits=[32, 1024]),
    'mats': dict(name='MATs', value=1, step=32, limits=[1, 1048579]),
    'bw': dict(name='BW', value=100, step=1,limits=[100, 16000], units='Gbit'),
    'dio': dict(name='DIO',  value=1, step=8, limits=[1, 128], units='bit'),
    'ebitpim': dict(name='EbitPIM',  value=0.01, step=0.01, limits=[0.01, 1], units='pJ'),
    'ebitcpu': dict(name='EbitCPU', value=1, step=0.01, limits=[1, 100], units='pJ')
}

class Param:
    def __init__(self, name, limits, step, value=None, units=None, const=True):
        self.name = name
        self.min = limits[0]
        self.max = limits[1]
        self.step = step
        self.units = units
        self.const = const
        self.range = np.arange(self.min, self.max, self.step)
        if not const:
            self.value = self.range
        else:
            self.value = value
        
    def is_valid(self):
        if not self.const: return True
        elif not self.value: return False
        return self.value in self.range

    def set_value(self,val):
        self.value = val
        return self.is_valid()
    
    def set_const(self,const):
        self.const = const
        if not const:
            self.value = self.range

    def get_copy(self):
        new_obj = Param(name=self.name, limits=[self.min,self.max], step=self.step,
                        value=self.value, units=self.units, const=self.const)
        return new_obj
    

class BitletParams:
    def __init__(self, params_dict):
        self.cc = params_dict['cc']
        self.ct = params_dict['ct']
        self.bw = params_dict['bw']
        self.rows = params_dict['rows']
        # self.cols = params_dict['cols']
        self.mats = params_dict['mats']
        self.dio = params_dict['dio']
        self.ebitpim = params_dict['ebitpim']
        self.ebitcpu = params_dict['ebitcpu']
    
    def set_const(self, param_name):
        param = self.__getattribute__(param_name)
        param.const = True