import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from ModelParams import BitletParams


class BitletModel:
  
    def __init__(self):
        self.params = BitletParams()
    

    def set_params(self, params_dict):
        self.params = BitletParams(params_dict)
        
  
    def pim_throughput(self):
        result = None
        row = self.params.rows
        mats = self.params.mats
        cc = self.params.cc
        ct = self.params.ct
        if all([row.is_valid(), mats.is_valid(), cc.is_valid(), ct.is_valid()]):
            result = ((row.value * mats.value) / (cc.value * ct.value))
        return result
    
    def cpu_throughput(self):
        result = None
        bw = self.params.bw
        dio = self.params.dio
        if all([bw.is_valid(), dio.is_valid()]):
            result = (bw.value / dio.value)
        return result
    
    def combined_throughput(self):
        result = None
        cpu_throughput = self.cpu_throughput()
        pim_throughput = self.pim_throughput()
        if cpu_throughput and pim_throughput:
            result = (1 / ((1 / pim_throughput) + (1 / cpu_throughput)))
        return result
    
    def pim_power(self):
        result = None
        row = self.params.rows
        mats = self.params.mats
        ebitspim = self.params.ebitpim
        ct = self.params.ct
        if all([row.is_valid(), mats.is_valid(), ebitspim.is_valid(), ct.is_valid()]):
            result = ( (ebitspim.value * row.value * mats.value) / ct.value )
        return result
    
    def cpu_power(self):
        result = None
        bw = self.params.bw
        ebitscpu = self.params.ebitcpu
        if all([bw.is_valid(), ebitscpu.is_valid()]):
            result = (bw.value * ebitscpu.value)
        return result
    
    def combined_power(self):
        result = None
        cpu_throughput = self.cpu_throughput()
        pim_throughput = self.pim_throughput()
        combined_throughput = self.combined_throughput()
        cpu_power = self.cpu_power()
        pim_power = self.pim_power()
        if combined_throughput and cpu_power and pim_power:
            result = ( (pim_power / pim_throughput) + (cpu_power / cpu_throughput) ) * combined_throughput
        return result
        
    
    def pim_energy(self):
        result = None
        pim_throughput = self.pim_throughput()
        pim_power = self.pim_power()
        if pim_throughput and pim_power:
            result = ( pim_power / pim_throughput )
        return result
        
    def cpu_energy(self):
        result = None
        cpu_throughput = self.pim_throughput()
        cpu_power = self.pim_power()
        if cpu_throughput and cpu_power:
            result = ( cpu_power / cpu_throughput )
        return result

    def combined_energy(self):
        result = None
        combined_throughput = self.combined_throughput()
        combined_power = self.combined_power()
        if combined_throughput and combined_power:
            result = ( combined_power / combined_throughput )
        return result
      
      
      