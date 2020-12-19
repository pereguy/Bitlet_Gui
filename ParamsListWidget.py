import numpy as np
import collections
import sys, os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

bitlet_params = {
    'cc': dict(name='CC',  value=1.00, step=1.0, limits=[1.0, 65536.0]),
    'ct':dict(name='CT',  value=0.1, step=0.1, limits=[0.1, 100], units='ns'),
    'rows': dict(name='Rows', value=32, step=32, limits=[32, 1024]),
    'cols':dict(name='Columns',  value=32, step=32, limits=[32, 1024]),
    'mats': dict(name='MATs', value=1, step=32, limits=[1, 1048579]),
    'bw': dict(name='BW', value=100, step=1,limits=[100, 16000], units='Gbit'),
    'dio': dict(name='DIO',  value=1, step=8, limits=[1, 128], units='bit'),
    'ebit_pim': dict(name='EbitPIM',  value=0.01, step=0.01, limits=[0.01, 1], units='pJ'),
    'ebit_cpu': dict(name='EbitCPU', value=1, step=0.01, limits=[1, 100], units='pJ')
}

class ParametersListWidget(QtGui.QWidget):
    def __init__(self, title='ParamsList'):
        QtGui.QWidget.__init__(self)
        
        self.title = title
        self.setupUi()
        
        self.setLayout(self.paramsListLayout)
        self.show()
        
        

    def setupUi(self):
        self.paramsListWidget = QtGui.QWidget()
        self.paramsListWidget.setObjectName(u"verticalLayoutWidget")
        # self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 40, 291, 161))
        self.paramsListLayout = QtGui.QVBoxLayout()
        self.paramsListLayout.setObjectName(u"verticalLayout_2")
        # self.paramsListLayout.setContentsMargins(0, 0, 0, 0)    
        
        self.params = {
            'CC' : ScrollSpinParam(**bitlet_params['cc']),
            'CT' : ScrollSpinParam(**bitlet_params['ct']),
            'BW' : ScrollSpinParam(**bitlet_params['bw']),
            'Rows' : ScrollSpinParam(**bitlet_params['rows']),
            'Columns' : ScrollSpinParam(**bitlet_params['cols']),
            'MATs' : ScrollSpinParam(**bitlet_params['mats']),
            'DIO' : ScrollSpinParam(**bitlet_params['dio']),
            'EbitPIM' : ScrollSpinParam(**bitlet_params['ebit_pim']),
            'EbitCPU' : ScrollSpinParam(**bitlet_params['ebit_cpu'])
        }
        
        self.axis_widget = QtGui.QGroupBox('Select Axis')
        # self.axis_widget.set
        self.axis_layout = QtGui.QVBoxLayout()
        self.x_list = pg.ComboBox(items=[''] + [v['name'] for v in bitlet_params.values()])
        self.y_list = pg.ComboBox(items=[''] + [v['name'] for v in bitlet_params.values()])
        self.btn_start = pg.FeedbackButton("Start")
        self.btn_start.clicked.connect(self.start_params)
        self.axis_layout.addWidget(self.x_list)
        self.axis_layout.addWidget(self.y_list)
        self.axis_layout.addWidget(self.btn_start)
        self.axis_widget.setLayout(self.axis_layout)

        self.params_widget = QtGui.QGroupBox('Parameters')
        self.paramsLayout = QtGui.QVBoxLayout()
        self.paramsLayout.addWidget(self.params['BW'])
        self.paramsLayout.addWidget(self.params['Rows'])
        self.paramsLayout.addWidget(self.params['CC'])
        self.paramsLayout.addWidget(self.params['CT'])
        self.paramsLayout.addWidget(self.params['Columns'])
        self.paramsLayout.addWidget(self.params['MATs'])
        self.paramsLayout.addWidget(self.params['DIO'])
        self.paramsLayout.addWidget(self.params['EbitPIM'])
        self.paramsLayout.addWidget(self.params['EbitCPU'])
        self.params_widget.setLayout(self.paramsLayout)
        
        
        
        self.btn_plot = QtGui.QPushButton("Plot")
        self.btn_reset = QtGui.QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_params)
        self.paramsListLayout.addWidget(self.axis_widget)
        self.paramsListLayout.addWidget(self.params_widget)
        self.paramsListLayout.addWidget(self.btn_plot)
        self.paramsListLayout.addWidget(self.btn_reset)
        # self.button.clicked.connect()
        
        self.paramsListWidget.setLayout(self.paramsListLayout)

    def start_params(self):
        x_param = self.x_list.value()
        y_param = self.y_list.value()
        
        if (x_param and y_param) and (x_param != y_param):
            for name, param in self.params.items():
                const = (name == x_param) or (name == y_param)
                param.set_rule(const)
        else:
            self.btn_start.failure("Error")
            self.reset_params()

            
    def reset_params(self):
        for param in self.params.values():
            param.reset()
        self.x_list.setCurrentIndex(0)
        self.y_list.setCurrentIndex(0)
        
                



class ScrollSpinParam(QtGui.QWidget):
    def __init__(self,name, value=0,limits=[],step=1,units='',constant=True):
        QtGui.QWidget.__init__(self)
        
        self.name = name
        
        self.min = limits[0]
        self.max = limits[1]
        self.step = step
        self.units = units
        self.value = value
        self.const = constant
        
        self.setupUi()
        self.setLayout(self.paramLayout)
        self.show()
        
    
    def setupUi(self):
        self.gridLayoutWidget = QtGui.QWidget()
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        # self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 60, 361, 80))
        self.paramLayout = QtGui.QGridLayout()
        self.paramLayout.setObjectName(u"gridLayout")
        # self.paramLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.paramLayout.setHorizontalSpacing(12)
        # self.paramLayout.setContentsMargins(5, 0, 1, 0)
        self.label = QtGui.QLabel()
        self.label.setObjectName(self.name)
        self.label.setText(self.name)
        # self.label.setSizeIncrement(QtCore.QSize(8, 0))
        self.label.setMinimumSize(QtCore.QSize(65, 30))
        self.paramLayout.addWidget(self.label, 0, 0, 1, 1)

        self.spinBox = pg.SpinBox()
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setRange(self.min,self.max)
        self.spinBox.setSingleStep(self.step)
        self.spinBox.setMinimumSize(QtCore.QSize(20, 30))
        self.paramLayout.addWidget(self.spinBox, 0, 1, 1, 1)

        self.horizontalSlider = QtGui.QSlider()
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setMinimum(self.min)
        self.horizontalSlider.setMaximum(self.max)
        self.horizontalSlider.setTickInterval(self.step)
        self.horizontalSlider.setSingleStep(self.step)
        
        self.paramLayout.addWidget(self.horizontalSlider, 0, 2, 1, 2)

        self.spinBox.valueChanged.connect(self.horizontalSlider.setValue)
        self.spinBox.valueChanged.connect(self.update_value)
        self.horizontalSlider.valueChanged.connect(self.spinBox.setValue)
        self.horizontalSlider.valueChanged.connect(self.update_value)
        
        self.spinBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)

    def update_value(self,val):
        self.value = val
    
    def set_value(self,val):
        self.value = val
        self.spinBox.setValue(val)
        self.horizontalSlider.setValue(val)
        
    
    def set_rule(self,constant):
        self.const = constant
        if not constant:
            self.spinBox.setEnabled(True)
            self.horizontalSlider.setEnabled(True)
    
    def reset(self):
        self.set_value(self.min)
        self.spinBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
        
