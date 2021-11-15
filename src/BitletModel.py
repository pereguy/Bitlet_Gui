import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from src.BitletModelParams import BitletParams


class BitletModel:
  
    def __init__(self,model_params=None):
        # self.params = BitletParams.get_params(params_dict)
        self.params = model_params
        
  
    def pim_throughput(self,rows,xbs,cc,ct):
        result = None
        result = ((rows * xbs) / (cc * ct))  * (10^6)
        return result
    
    def cpu_throughput(self,dio,bw):
        result = None
        result = (bw / dio)  * (10^12)
        return result
    
    def combined_throughput(self,rows,xbs,cc,ct,dio,bw):
        result = None
        cpu_throughput = self.cpu_throughput(dio,bw)
        pim_throughput = self.pim_throughput(rows,xbs,cc,ct)
        result = (1 / ((1 / pim_throughput) + (1 / cpu_throughput)))
        return result 
    
    def pim_power(self,rows,xbs,ebitpim,ct):
        result = None
        result = ( (ebitpim * rows * xbs) / ct )
        return result
    
    def cpu_power(self,bw,ebitcpu):
        result = None
        result = (bw * ebitcpu)
        return result
    
    def combined_power_throughput(self,rows,xbs,cc,ct,dio,bw,ebitcpu,ebitpim):
        result = None
        cpu_throughput = self.cpu_throughput(dio,bw)
        pim_throughput = self.pim_throughput(rows,xbs,cc,ct)
        combined_throughput = self.combined_throughput(rows,xbs,cc,ct,dio,bw)
        cpu_power = self.cpu_power(bw,ebitcpu)
        pim_power = self.pim_power(dio,xbs,ebitpim,ct)
        combined_power = ( (pim_power / pim_throughput) + (cpu_power / cpu_throughput) ) * combined_throughput
        return combined_throughput, combined_power
      
      
    def update_param(self,param_name, value):
        self.params.__setattr__(param_name,value)