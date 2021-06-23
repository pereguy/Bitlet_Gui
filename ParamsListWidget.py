# from BitletPlotWidget import ParametersPlotWidget

import numpy as np
import collections
import sys, os
import pyqtgraph as pg
from copy import deepcopy
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from BitletModelParams import BitletParams, bitlet_params, Param
from double_slider import DoubleSlider

class AxisesListWidget(QtWidgets.QGroupBox):
    axisesSelected = pyqtSignal(str,str)
    
    def __init__(self):
        super().__init__()
        self.axises_list_indexes = {v['name']: i for i,v in enumerate(bitlet_params.values())}
        
        # self.axis_widget = QtWidgets.QGroupBox('Select Axis')
        self.axis_layout = QtWidgets.QVBoxLayout()
        self.x_list = QtWidgets.QComboBox() 
        self.x_list.addItems( [v['name'] for v in bitlet_params.values()])
        self.x_list.setPlaceholderText("Select X")
        self.x_list.setCurrentIndex(-1)
        self.y_list = QtWidgets.QComboBox() 
        self.y_list.addItems( [v['name'] for v in bitlet_params.values()])
        self.y_list.setPlaceholderText("Select Y")
        self.y_list.setCurrentIndex(-1)
        self.btn_start = pg.FeedbackButton("Plot")
        
        self.axis_layout.addWidget(self.x_list)
        self.axis_layout.addWidget(self.y_list)
        self.axis_layout.addWidget(self.btn_start)
        # self.axis_widget.setLayout(self.axis_layout)
        self.setLayout(self.axis_layout)
        self.btn_start.clicked.connect(self.start_plot)
        
    def start_plot(self):
        x_param = self.x_list.currentText()
        y_param = self.y_list.currentText()
        if (self.x_list.currentIndex() == -1) or (self.y_list.currentIndex() == -1):
            self.error_msg("You Must Choose Both Axis")
        elif (x_param != y_param) :
            self.axisesSelected.emit(x_param, y_param)
        elif (x_param == y_param):
            self.error_msg("Choose Different Axis")
        else:
            self.error_msg("Error")
        
    
    def error_msg(self,msg):
        msg_box = QtWidgets.QMessageBox.warning(self, "Error", msg)



class ParametersListWidget(QtWidgets.QWidget):
    
    paramValueChanged = pyqtSignal(str,object)
    
    def __init__(self ,title='ParamsList'):
        super().__init__()        
        self.title = title
        self.setupUi()
        self.setLayout(self.paramsListLayout)
        self.show()
        
        

    def setupUi(self):
        self.paramsListLayout = QtWidgets.QVBoxLayout()
        self.paramsListLayout.setObjectName(u"verticalLayout_2")
        # self.paramsListLayout.setContentsMargins(0, 0, 0, 0)    
        
        self.params = {
            'cc' : BitletSlider(**bitlet_params['cc']),
            'ct' : BitletSlider(**bitlet_params['ct']),
            'bw' : BitletSlider(**bitlet_params['bw']),
            'rows' : BitletSlider(**bitlet_params['rows']),
            # 'columns' : ScrollSpinParam(**bitlet_params['cols']),
            'mats' : BitletSlider(**bitlet_params['mats']),
            'dio' : BitletSlider(**bitlet_params['dio']),
            'ebitpim' : BitletSlider(**bitlet_params['ebitpim']),
            'ebitcpu' : BitletSlider(**bitlet_params['ebitcpu'])
        }
        
        self.axises_list_indexes = {v['name']: i for i,v in enumerate(bitlet_params.values())}

        self.params_widget = QtWidgets.QGroupBox('Parameters')
        self.paramsLayout = QtWidgets.QVBoxLayout()
        self.paramsLayout.addWidget(self.params['bw'])
        self.paramsLayout.addWidget(self.params['rows'])
        self.paramsLayout.addWidget(self.params['cc'])
        self.paramsLayout.addWidget(self.params['ct'])
        # self.paramsLayout.addWidget(self.params['columns'])
        self.paramsLayout.addWidget(self.params['mats'])
        self.paramsLayout.addWidget(self.params['dio'])
        self.paramsLayout.addWidget(self.params['ebitpim'])
        self.paramsLayout.addWidget(self.params['ebitcpu'])
        self.params_widget.setLayout(self.paramsLayout)
        
        for param in self.params:
            self.params[param].paramValueChanged.connect(self.param_update)
            self.params[param].set_role(False)
        self.paramsListLayout.addWidget(self.params_widget)
        self.setLayout(self.paramsListLayout)

    def param_update(self,param_name, value):
        self.paramValueChanged.emit(param_name, value)
        
    
    def start_params(self, x_param, y_param):
        self.x_param = x_param
        self.y_param = y_param
        for name, param in self.params.items():
            const = ((name != self.x_param.lower()) and (name != self.y_param.lower()))
            param.set_role(const)
     
    
    def reset_params(self):
        for param in self.params.values():
            param.reset()

        
    def extract_plot_params(self):
        params = dict()
        for name, param in self.params.items():
            if name != self.x_param.lower() and name != self.y_param.lower():
                params[name] = param.value
        return params

    def set_plot_params(self,axis_x,axis_y,params):
        prev_params = deepcopy(self.params)
        self.x_param = axis_x.name
        self.y_param = axis_y.name
        self.x_list.setCurrentIndex(self.axises_list_indexes[axis_x.name])
        self.y_list.setCurrentIndex(self.axises_list_indexes[axis_y.name])
        self.params[self.x_param] = axis_x
        self.params[self.y_param] = axis_y
        for name, param in params.items():
            self.params[name].changeValue(param)
        return prev_params
        
    def get_curr_params(self):
        prev_params = {k:v.value for k,v in self.params.items()}
        axis_x = self.params[self.x_param]
        axis_y = self.params[self.y_param]
        return axis_x,axis_y, prev_params
        
class BitletSlider(QtWidgets.QWidget):
    
    paramValueChanged = pyqtSignal(str,object)
    
    def __init__(self,name, value=0,limits=[],step=1,units='',fixed=False, factor=1):
        super(BitletSlider,self).__init__()
        self.name = name
        self.value = value
        self.limits = limits
        self.step = step
        self.units = units
        if units:
            self.funits = f'[{units}]'
        else:
            self.funits = '' 
        self.fixed = fixed
        self.initUI()

    def initUI(self):

        self.hbox = QtWidgets.QHBoxLayout()
        
        self.label = QtWidgets.QLabel()
        self.label.setText(self.name)
        self.label.setFixedSize(QtCore.QSize(70, 30))
        
        self.slid = DoubleSlider(minimum=self.limits[0], maximum=self.limits[1], step=self.step, value=self.value)
        self.slid.setFixedSize(QtCore.QSize(150,30))
        self.slid.doubleValueChanged.connect(self.changeValue)
        
        self.spinBox = QtWidgets.QDoubleSpinBox()
        self.spinBox.setValue(self.slid.value())
        self.spinBox.setMaximum(self.limits[1])
        self.spinBox.setMinimum(self.limits[0])
        
        
        self.value_label = QtWidgets.QLabel(f"{self.value} {self.funits}", self)
        self.value_label.setMinimumWidth(80)
        self.set_role(self.fixed)

        self.hbox.addWidget(self.label)
        # self.hbox.addSpacing(5)
        self.hbox.addWidget(self.slid)
        self.hbox.addSpacing(5)
        self.hbox.addWidget(self.value_label)

        self.setLayout(self.hbox)

        self.show()

    def format_value(self, value):
        if type(self.step) == int:
            return int(value)
        else:
            return np.round(value,2)
    
    def changeValue(self, value):
        formated = self.format_value(value)
        self.value = formated
        self.value_label.setText(f"{self.value} {self.funits}") 
        self.slid.setValue(value)   
        self.paramValueChanged.emit(self.name.lower(), formated)
    
    def get_param_object(self):
        return Param(self.name,self.limits,self.step,self.value,self.units,self.fixed)
                
    def set_role(self, role):
        self.fixed = role
        if role: 
            self.slid.setEnabled(True)
            self.value_label.setEnabled(True)
        else:
            self.slid.setEnabled(False)
            self.value_label.setEnabled(False)
    
    def reset(self):
        self.slid.setValue(bitlet_params[self.name.lower()]['value'])
        # self.set_role(False)
    
    def deep_copy(self):
        new_attr = self._get_params().copy()
        new_obj = BitletSlider(**new_attr)
        return new_obj  

    def _get_params(self):
        params = dict()
        params['name'] = self.name
        params['value'] = self.value 
        params['limits'] = self.limits
        params['step'] = self.step 
        params['units'] = self.units
        params['fixed'] = self.fixed 
        return params
    
    def to_numpy(self):
        return np.array([self.value])


class ScrollSpinParam(QtWidgets.QWidget):
    def __init__(self,name, value=0,limits=[],step=1,units='',constant=False):
        super(ScrollSpinParam,self).__init__()
        
        self.name = name
        self.value = value
        # self.param = Param(name,limits,step,value,units,constant)
        self.limits = limits
        self.step = step
        self.units = units 
        self.constant = constant  # constant == not X not Y
        self.values = (limits[1] - limits[0] + 1) // self.step
        # if self.step < 1:
        #     self.values = np.round(self.values,2).tolist()
        self.setupUi()
        # self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setLayout(self.paramLayout)
        self.show()
        
    
    # def slider_value(self,index=None,value=None):
    #     if index:
    #         return self.limits[0] + 
            
    
    def setupUi(self):
        self.paramLayout = QtWidgets.QGridLayout(self)
        self.paramLayout.setObjectName(u"param_layout")
        # self.paramLayout.setContentsMargins(0, 0, 0, 0)
        # self.paramLayout.columnMinimumWidth(40)
        
        self.label = QtWidgets.QLabel()
        self.label.setObjectName(self.name)
        self.label.setText(self.name)
        self.label.setFixedSize(QtCore.QSize(80, 30))
        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        self.paramLayout.addWidget(self.label, 0,0)
        if type(self.step) == int:
            self.spinBox = QtWidgets.QSpinBox()
        else:
            self.spinBox = QtWidgets.QDoubleSpinBox()
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setValue(self.value)
        self.spinBox.setRange(self.limits[0],self.limits[1])
        self.spinBox.setSingleStep(self.step)
        self.spinBox.setFixedSize(QtCore.QSize(80, 30))
        self.paramLayout.addWidget(self.spinBox, 0,2)

        self.horizontalSlider = QtWidgets.QSlider()
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setValue(self.values.index(self.value))
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(len(self.values)-1)
        # self.horizontalSlider.setTickInterval(int(self.step * self.factor))
        self.horizontalSlider.setSingleStep(1)
        # self.horizontalSlider.setPageStep(int(self.step * self.factor))
        # self.horizontalSlider.setSizePolicy()
        self.paramLayout.addWidget(self.horizontalSlider, 0,3)
        self.set_role(self.constant)
        
    
    def value_changed(self,who):
        self.disconnect_widgets()
        if who == 'spin':
            val = self.spinBox.value()
            self.horizontalSlider.setValue(self.values.index(val))
            self.values = val
        elif who == 'slider':
            val = self.horizontalSlider.value()
            self.spinBox.setValue(self.values[val])
            self.value = self.values[val]
        self.connect_widgets()
        

    
    def connect_widgets(self):
        self.spinBox.valueChanged.connect(lambda x: self.value_changed('spin')) ##self.spinbox_changed)
        self.horizontalSlider.valueChanged.connect(lambda x: self.value_changed('slider')) ##(self.slider_changed)
    
    def disconnect_widgets(self):
        self.horizontalSlider.valueChanged.disconnect()
        self.spinBox.valueChanged.disconnect()
    
    def set_role(self,constant):
        self.connect_widgets()
        self.constant = constant  
        if constant:
            self.spinBox.setEnabled(True)
            self.horizontalSlider.setEnabled(True)
        else:
            self.spinBox.setEnabled(False)
            self.horizontalSlider.setEnabled(False) 
            
    
    def reset(self):
        self.disconnect_widgets()
        self.value = bitlet_params[self.name.lower()]['value']
        self.spinBox.setValue(bitlet_params[self.name.lower()]['value']) ##(self.spinBox.minimum())
        self.horizontalSlider.setValue(bitlet_params[self.name.lower()]['value']) ##(self.horizontalSlider.minimum())
        # self.spinBox.setEnabled(False)
        # self.horizontalSlider.setEnabled(False)
    
    def get_copy(self):
        new_attr = deepcopy(bitlet_params[self.name.lower()])
        new_attr['value'] = deepcopy(self.value)
        new_attr['constant'] = deepcopy(self.constant)
        new_obj = ScrollSpinParam(**new_attr)
        return new_obj
    
    def get_param_object(self):
        return Param(self.name,self.limits,self.step,self.value,self.units,self.constant)
        
        


        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    paramss = {
            'cc' : ScrollSpinParam(**bitlet_params['cc']),
            'rows' : ScrollSpinParam(**bitlet_params['rows']),
            # 'columns' : ScrollSpinParam(**bitlet_params['cols']),
            'mats' : ScrollSpinParam(**bitlet_params['mats']),
            'dio' : ScrollSpinParam(**bitlet_params['dio']),
            'ebitpim' : ScrollSpinParam(**bitlet_params['ebitpim']),
            'ebitcpu' : ScrollSpinParam(**bitlet_params['ebitcpu'])
        }
    x = Param(**bitlet_params['ct']),
    y = Param(**bitlet_params['bw']),
    
    main = QtWidgets.QMainWindow()
    main.setCentralWidget(plt)
    main.show()
    app.exec_()