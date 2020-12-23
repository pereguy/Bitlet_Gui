from PyQt5 import QtWidgets
import numpy as np
import collections
import sys, os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from ModelParams import bitlet_params, Param

class ParametersListWidget(QtWidgets.QWidget):
    def __init__(self, title='ParamsList'):
        super().__init__()
        
        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        
        self.title = title
        self.setupUi()
        
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
            'columns' : ScrollSpinParam(**bitlet_params['cols']),
            'mats' : ScrollSpinParam(**bitlet_params['mats']),
            'dio' : ScrollSpinParam(**bitlet_params['dio']),
            'ebitpim' : ScrollSpinParam(**bitlet_params['ebit_pim']),
            'ebitcpu' : ScrollSpinParam(**bitlet_params['ebit_cpu'])
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
        self.paramsLayout.addWidget(self.params['columns'])
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
                const = (name == x_param.lower()) or (name == y_param.lower())
                param.set_rule(const)
            self.btn_plot.setEnabled(True)
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
        self.btn_plot.setEnabled(False)
        
                



class ScrollSpinParam(QtWidgets.QWidget):
    def __init__(self,name, value=0,limits=[],step=1,units='',constant=True):
        super(ScrollSpinParam,self).__init__()
        
        self.name = name
        self.param = Param(name,limits,step,value,units,constant)
        if self.param.step < 1:
            self.factor = 1 / self.param.step
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
        self.label.setObjectName(self.param.name)
        self.label.setText(self.param.name)
        self.label.setFixedSize(QtCore.QSize(80, 30))
        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        self.paramLayout.addWidget(self.label, 0,0)

        self.spinBox = QtWidgets.QDoubleSpinBox()
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setRange(self.param.min,self.param.max)
        self.spinBox.setSingleStep(self.param.step)
        self.spinBox.setFixedSize(QtCore.QSize(80, 30))
        self.paramLayout.addWidget(self.spinBox, 0,2)

        self.horizontalSlider = QtWidgets.QSlider()
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setMinimum(self.param.min * self.factor)
        self.horizontalSlider.setMaximum(self.param.max * self.factor)
        self.horizontalSlider.setTickInterval(self.param.step * self.factor)
        self.horizontalSlider.setSingleStep(self.param.step * self.factor)
        self.horizontalSlider.setPageStep(self.param.step * self.factor)
        # self.horizontalSlider.setSizePolicy()
        self.paramLayout.addWidget(self.horizontalSlider, 0,3)

        self.spinBox.valueChanged.connect(self.spinbox_changed)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        
        self.spinBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
        
        
    def spinbox_changed(self, val):
        val = (val // self.param.step) * self.param.step
        self.value = val
        self.horizontalSlider.setValue(val * self.factor)
        self.spinBox.setValue(val)
    
    def slider_changed(self, val):
        self.value = val
        self.spinBox.setValue(val / self.factor)
    
    def set_rule(self,constant):
        self.param.const = constant
        if not constant:
            self.spinBox.setEnabled(True)
            self.horizontalSlider.setEnabled(True)
    
    def reset(self):
        self.value = self.param.min
        self.spinBox.setValue(self.spinBox.minimum())
        self.horizontalSlider.setValue(self.horizontalSlider.minimum())
        self.spinBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
        
            