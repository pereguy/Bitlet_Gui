
import numpy as np

import sys, os
from PyQt5 import QtWidgets, QtCore, QtGui

from ParamsListWidget import ParametersListWidget, AxisesListWidget
from BitletPlotWidget import BitletPlotWidget
from BitletModelParams import  bitlet_params, Param

class BitletModelGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(BitletModelGUI,self).__init__()
        #config main
        self.tabs_params = dict()
        self.plot_count = 0
        self.curr_index = 0
        self.setupUI()
        self.plotting_widgets = []
        self.plotting_params = dict()
        
        
        
    def setupUI(self):
        self.setWindowTitle("Bitlet Model")
        self.resize(1350, 957)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        
        self.axises_widget = AxisesListWidget()
        self.params_widget = ParametersListWidget()
        self.params_widget.paramValueChanged.connect(self.plot_value_changed)
        self.axises_widget.axisesSelected.connect(self.start_new_tab)
        self.tabs_params[0] = self.params_widget
        
        params_layout = QtWidgets.QVBoxLayout()
        params_layout.addWidget(self.axises_widget)
        params_layout.addWidget(self.params_widget)
        
        control_widgets = QtWidgets.QWidget()
        control_widgets.setLayout(params_layout)
        
        self.params_dock = QtWidgets.QDockWidget("Parameters", self)
        self.params_dock.setWidget(control_widgets)
        self.params_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures) 
        # self.params_dock.setAllowedAreas(QtWidgets.QDockWidget) 
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.params_dock)

        self.plotting_tabs = QtWidgets.QTabWidget(self)
        self.plotting_tabs.setDocumentMode(True)
        self.plotting_tabs.setTabsClosable(True)
        self.plotting_tabs.tabCloseRequested.connect(lambda x: self.plotting_tabs.removeTab(x))
        self.plotting_tabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.plotting_tabs.currentChanged.connect(self.change_tab)
        self.setCentralWidget(self.plotting_tabs)
        self.addWelcomeTab()
        
    def addWelcomeTab(self):
        # widget and layout
        welcome_widget = QtWidgets.QWidget()
        welcome_widget.setStyleSheet('background-color: lightgrey;')
        welcome_widget.setContentsMargins(10,10,10,10)
        
        verticalLayout = QtWidgets.QVBoxLayout(welcome_widget)
        verticalLayout.setContentsMargins(10, 10,10, 10)
        # verticalLayout.setStyleSheet('background-color: lightgrey;')
        verticalLayout.setSpacing(10)
        
        #  fonts 
        welcome_font = QtGui.QFont()
        welcome_font.setPointSize(24)
        welcome_font.setBold(True)
        welcome_font.setWeight(50)
        
        inst_font = QtGui.QFont()
        inst_font.setPointSize(12)
        
        #welcome label
        welcome_label = QtWidgets.QLabel("Welcome\nBitlet Model GUI",welcome_widget)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)

        # inst label
        inst_text = "In Order To Start Plotting:\n  -  Select Parameters For Axises X And Y \n  -  Hit The Plot Button\n  -  Adjust The Other Parameters Values And See The Plot Changing "
        inst_label = QtWidgets.QLabel(inst_text,welcome_widget) 
        inst_label.setFont(inst_font)

        # names_label
        names_label = QtWidgets.QLabel("By Noa Riklin & Guy Pereg", welcome_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(names_label.sizePolicy().hasHeightForWidth())
        names_label.setSizePolicy(sizePolicy)
        
        verticalLayout.addWidget(welcome_label)
        verticalLayout.addWidget(inst_label)
        verticalLayout.addWidget(names_label)
        
        welcome_widget.setLayout(verticalLayout)
        self.plotting_tabs.addTab(welcome_widget, "Welcome")





    def change_tab(self,tab_index):
        if self.plot_count < tab_index:
            return 
        # if self.curr_index > -1:
        #     axis_x,axis_y, plot_params = self.params_widget.get_curr_params()
        #     self.tabs_params[self.curr_index] = (axis_x,axis_y, plot_params)
        self.params_widget = self.tabs_params[tab_index]
        self.curr_index = tab_index
        self.plotting_tabs.setCurrentIndex(self.curr_index)
        self.update_param_widget()
        
        
    def plot_value_changed(self,param_name,value):
        self.plotting_widgets[self.curr_index].canvas.update_value(param_name,value)
        
    
    def start_new_tab(self, axis_x, axis_y):
        self.plot_count += 1
        if self.curr_index >= 0:
            param_widget = ParametersListWidget()
            param_widget.start_params(axis_x['name'], axis_y['name'])
            param_widget.paramValueChanged.connect(self.plot_value_changed)
            self.tabs_params[self.plot_count] =  param_widget
            self.params_widget = param_widget
            self.update_param_widget()
        else:
            self.params_widget.start_params(axis_x['name'], axis_y['name'])
        plot_params = self.params_widget.extract_plot_params()
        # try:
        param_x = Param(**bitlet_params[axis_x['name'].lower()])
        param_x.fixed = False
        param_x.min = axis_x['min']
        param_x.max = axis_x['max']
        param_y = Param(**bitlet_params[axis_y['name'].lower()])
        param_y.fixed = False
        param_y.min = axis_y['min']
        param_y.max = axis_y['max']
        plot_wdg = BitletPlotWidget(param_x,param_y, plot_params)
        # except TypeError:
        #     msg_box = QtWidgets.QMessageBox.warning(self, "Error", "Unknown Error")
        #     if self.plotting_tabs.currentIndex() > -1:
        #         self.change_tab(self.plotting_tabs.currentIndex())
        #     return 
        self.plotting_widgets.append(plot_wdg)
        self.curr_index = self.plotting_tabs.addTab(plot_wdg, f"Plot {self.plot_count}")
        self.plotting_tabs.setCurrentIndex(self.curr_index)
    
    
    def update_param_widget(self):
        params_layout = QtWidgets.QVBoxLayout()
        params_layout.addWidget(self.axises_widget)
        params_layout.addWidget(self.params_widget)
        control_widgets = QtWidgets.QWidget()
        control_widgets.setLayout(params_layout)
        self.params_dock.setWidget(control_widgets)
        self.params_dock.show()
        
    def save(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save State..", "untitled.cfg", "Config Files (*.cfg)")
        if isinstance(filename, tuple):
            filename = filename[0]  # Qt4/5 API difference
        if filename == '':
            return
        state = self.params.saveState()
        
    def load(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Save State..", "", "Config Files (*.cfg)")
        if isinstance(filename, tuple):
            filename = filename[0]  # Qt4/5 API difference
        if filename == '':
            return
        state = QtWidgets.readConfigFile(str(filename)) 
        self.loadState(state)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    main.show()
    app.exec_()
    
    
