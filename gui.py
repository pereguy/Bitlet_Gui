
import numpy as np

import sys, os
from PyQt5 import QtWidgets, QtCore

from ParamsListWidget import ParametersListWidget
from BitletPlotWidget import BitletPlotWidget


class BitletModelGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(BitletModelGUI,self).__init__()
        #config main
        self.setupUI()
        self.plot_count = 0
        self.curr_index = -1
        self.plotting_widgets = []
        
        
    def setupUI(self):
        self.setWindowTitle("Bitlet Model")
        self.resize(1350, 957)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        
        self.params_widget = ParametersListWidget()
        self.params_widget.btn_plot.clicked.connect(self.start_new_tab)
        
        self.params_dock = QtWidgets.QDockWidget("Parameters", self)
        self.params_dock.setWidget(self.params_widget)
        self.params_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures) 
        # self.params_dock.setAllowedAreas(QtWidgets.QDockWidget) 
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.params_dock)

        self.plotting_tabs = QtWidgets.QTabWidget(self)
        self.plotting_tabs.setDocumentMode(True)
        self.plotting_tabs.setTabsClosable(True)
        self.plotting_tabs.tabCloseRequested.connect(lambda x: self.plotting_tabs.removeTab(x))
        self.plotting_tabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.setCentralWidget(self.plotting_tabs)
        

    def start_new_tab(self):
        axis_x,axis_y, plot_params = self.params_widget.extract_plot_params()
        plot_wdg = BitletPlotWidget(axis_x,axis_y, plot_params)
        self.plotting_widgets.append(plot_wdg)
        self.curr_index = self.plotting_tabs.addTab(plot_wdg, f"Plot {self.plot_count + 1}")
        self.plotting_tabs.setCurrentIndex(self.curr_index)
        self.plot_count += 1 
        self.params_widget.reset()

        
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
    
    
