from PyQt5 import QtWidgets
import numpy as np
import collections
import sys, os
import pyqtgraph as pg
from copy import deepcopy
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.metaarray.MetaArray import axis
from ModelParams import BitletParams, bitlet_params, Param

class ParametersListWidget(QtWidgets.QWidget):
    def __init__(self, title='ParamsList'):
        super().__init__()
        
        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        
        self.title = title
        self.setupUi()
        self.x_param = None
        self.y_param = None
        self.setLayout(self.paramsListLayout)
        self.show()
        
        

    def setupUi(self):
        self.paramsListLayout = QtWidgets.QVBoxLayout()
        self.paramsListLayout.setObjectName(u"verticalLayout_2")
        # self.paramsListLayout.setContentsMargins(0, 0, 0, 0)    
        
        self.params = {
            'cc' : ScrollSpinParam(**bitlet_params['cc']),
            'ct' : ScrollSpinParam(**bitlet_params['ct']),
            'bw' : ScrollSpinParam(**bitlet_params['bw']),
            'rows' : ScrollSpinParam(**bitlet_params['rows']),
            # 'columns' : ScrollSpinParam(**bitlet_params['cols']),
            'mats' : ScrollSpinParam(**bitlet_params['mats']),
            'dio' : ScrollSpinParam(**bitlet_params['dio']),
            'ebitpim' : ScrollSpinParam(**bitlet_params['ebitpim']),
            'ebitcpu' : ScrollSpinParam(**bitlet_params['ebitcpu'])
        }
        
        self.axis_widget = QtWidgets.QGroupBox('Select Axis')
        self.axis_layout = QtWidgets.QVBoxLayout()
        self.x_list = pg.ComboBox(items=[''] + [v['name'] for v in bitlet_params.values()])
        self.y_list = pg.ComboBox(items=[''] + [v['name'] for v in bitlet_params.values()])
        self.btn_start = pg.FeedbackButton("Start")
        self.btn_start.clicked.connect(self.start_params)
        self.axis_layout.addWidget(self.x_list)
        self.axis_layout.addWidget(self.y_list)
        self.axis_layout.addWidget(self.btn_start)
        self.axis_widget.setLayout(self.axis_layout)

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
        
        
        self.btn_plot = QtWidgets.QPushButton("Plot")
        self.btn_plot.setEnabled(False)
        self.btn_reset = QtWidgets.QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset)
        self.paramsListLayout.addWidget(self.axis_widget)
        self.paramsListLayout.addWidget(self.params_widget)
        self.paramsListLayout.addWidget(self.btn_plot)
        self.paramsListLayout.addWidget(self.btn_reset)
        
        self.setLayout(self.paramsListLayout)

    
    def start_params(self):
        x_param = self.x_list.value()
        y_param = self.y_list.value()
        
        if (x_param and y_param) and (x_param != y_param):
            for name, param in self.params.items():
                const = ((name != x_param.lower()) and (name != y_param.lower()))
                param.set_rule(const)
            self.btn_plot.setEnabled(True)
            self.x_param = x_param.lower()
            self.y_param = y_param.lower()
        elif (x_param == y_param):
            self.error_msg("Choose Different Axis")
            self.reset_params()
        else:
            self.error_msg("You Must Choose Both Axis")
            self.reset_params()
               
            
    def error_msg(self,msg):
        msg_box = QtWidgets.QMessageBox.warning(self, "Error", msg)
            
    def reset(self):
        self.x_list.setCurrentIndex(0)
        self.y_list.setCurrentIndex(0)
        self.reset_params()      
    
    def reset_params(self):
        for param in self.params.values():
            param.reset()
        self.x_param = None
        self.y_param = None
        self.btn_plot.setEnabled(False)
        
    def extract_plot_params(self):
        axis_x = None
        axis_y = None
        params = dict()
        for name, param in self.params.items():
            if name == self.x_param:
                axis_x = param.get_param_object()
            elif name == self.y_param:
                axis_y = param.get_param_object()
            else:
                params[name] = param.get_copy()
        plot_params = ParametersPlotWidget(axis_x,axis_y,params)
        return plot_params
        
        
        
                
class ParametersPlotWidget(QtWidgets.QWidget):
    def __init__(self,axis_x, axis_y,params_widgets):
        super().__init__()
        self.x_axis = axis_x
        self.y_axis = axis_y
        self.params_widgets = params_widgets
        
        self.paramsLayout = QtWidgets.QGridLayout(self)
        for i, param in enumerate(self.params_widgets):
            self.paramsLayout.addWidget(self.params_widgets[param], i // 3, i % 3 )
        
        self.setLayout(self.paramsLayout)
        
    def get_model_params(self):
        params_dict = dict()
        params_dict[self.x_axis.name.lower()] = self.x_axis
        params_dict[self.y_axis.name.lower()] = self.y_axis
        
        for i, param in enumerate(self.params_widgets):
            params_dict[param] = self.params_widgets[param].get_param_object()
        return params_dict
        
        


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
        if self.step < 1:
            self.factor = int(1 / self.step)
        else:
            self.factor = 1 
        
        self.setupUi()
        # self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setLayout(self.paramLayout)
        self.show()
        
    
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
        self.horizontalSlider.setValue(int(self.value * self.factor))
        self.horizontalSlider.setMinimum(int(self.limits[0] * self.factor))
        self.horizontalSlider.setMaximum(int(self.limits[1] * self.factor))
        self.horizontalSlider.setTickInterval(int(self.step * self.factor))
        self.horizontalSlider.setSingleStep(int(self.step * self.factor))
        self.horizontalSlider.setPageStep(int(self.step * self.factor))
        # self.horizontalSlider.setSizePolicy()
        self.paramLayout.addWidget(self.horizontalSlider, 0,3)

        self.spinBox.valueChanged.connect(self.spinbox_changed)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        
        self.set_rule(self.constant)
        
        
    def spinbox_changed(self, val):
        val = (val // self.step) * self.step
        self.value = val
        self.horizontalSlider.setValue(int(val * self.factor))
        # self.spinBox.setValue(val)
    
    def slider_changed(self):
        val = self.horizontalSlider.value()
        self.value = val
        self.spinBox.setValue(round(val / self.factor, 2))
    
    def set_rule(self,constant):
        self.constant = constant  
        if constant:
            self.spinBox.setEnabled(True)
            self.horizontalSlider.setEnabled(True)
        else:
            self.spinBox.setEnabled(False)
            self.horizontalSlider.setEnabled(False) 
            
    
    def reset(self):
        self.value = self.limits[0]
        self.spinBox.setValue(self.spinBox.minimum())
        self.horizontalSlider.setValue(self.horizontalSlider.minimum())
        self.spinBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
    
    def get_copy(self):
        new_attr = deepcopy(bitlet_params[self.name.lower()])
        new_attr['value'] = self.value
        new_attr['constant'] = self.constant
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
    plt = ParametersPlotWidget(x,y,paramss)
    main.setCentralWidget(plt)
    main.show()
    app.exec_()