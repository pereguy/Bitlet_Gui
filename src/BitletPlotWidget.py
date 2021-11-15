from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.text as text
from matplotlib import cm
from matplotlib.pyplot import figure, xlabel
from matplotlib import ticker 
from matplotlib.scale import LogScale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas,NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors 

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import QAction, QApplication, QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QSpinBox, QVBoxLayout , QWidget, QPushButton, QToolBar
from PyQt5.QtWidgets import QLabel , QGridLayout, QDesktopWidget, QSizePolicy

from src.BitletModel import BitletModel


class PlotWindow(FigureCanvas):
    def __init__(self,x_axis,y_axis,params,resolution=1000):
        self.plot_colorbar = None
        self.resolution = resolution
        self.plot_figure = figure(figsize=(8,15))
        FigureCanvas.__init__(self, self.plot_figure)  
        self.axes = self.plot_figure.gca()
        self.setWindowTitle("Plot") 
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.params = params
        self.x_lim = (self.x_axis.min,self.x_axis.max)
        self.y_lim = (self.y_axis.min,self.y_axis.max)
        self.bitlet_model = BitletModel()
        
    def draw_2d_graph(self):  # Function for graph plotting
        self.clear_plot()
        x_axis , y_axis = np.meshgrid(self.x_axis.to_numpy(self.resolution), self.y_axis.to_numpy(self.resolution))
        self.params[self.x_axis.name.lower()] = x_axis
        self.params[self.y_axis.name.lower()] = y_axis
        z,z2 = self.bitlet_model.combined_power_throughput(**self.params)
        norm = colors.LogNorm()
        cf = self.axes.pcolormesh(x_axis,y_axis,z,norm=norm,vmin=z.min(),vmax=z.max(),cmap=plt.get_cmap('RdYlGn'))
        cbar = plt.colorbar(cf,ax=self.axes,  extend='max')
        cbar.ax.set_ylabel('Combined Throughput [GOPS]', fontsize=16)
        locator = ticker.LogLocator(base=2)
        pwr_ax = self.axes.contour(x_axis, y_axis, z2,colors='blue',locator=locator,extend='both')
        trh_ax = self.axes.contour(x_axis, y_axis, z,colors='black',locator=locator,extend='both')
        trh_labels_loc = []
        for l in trh_ax.allsegs:
            if len(l) > 0:
                mid = len(l[0]) // 2 - 2
                # mid = -3
                trh_labels_loc.append(l[0][mid])
        pwr_labels_loc = []
        for l in pwr_ax.allsegs:
            if len(l) > 0:
                mid = len(l[0]) // 2 - 2
                # mid = -3
                pwr_labels_loc.append(l[0][mid])

        trh_ax.clabel( fontsize=12,use_clabeltext=True,  inline=False, fmt= lambda x: f'TP = {x:.3f} [GOPS]',manual=trh_labels_loc)
        pwr_ax.clabel(fontsize=12, use_clabeltext=True, inline=False, fmt= lambda x: f'P = {x:.3f} [W]',manual=pwr_labels_loc)
        self.axes.set_xlim(xmin=self.x_lim[0] , xmax=self.x_lim[1])
        self.axes.set_ylim(ymin=self.y_lim[0], ymax=self.y_lim[1])
        self.axes.set_xlabel(f"{self.x_axis.name} {self.x_axis.units}")
        self.axes.set_ylabel(f"{self.y_axis.name} {self.y_axis.units}")
        # self.axes.legend()
        self.axes.set_xscale("log",basex=2)
        self.axes.set_yscale("log",basey=2)
        self.draw()
    
    
    def clear_plot(self):
        self.plot_figure.clf()
        if self.axes is not None:    
            self.axes.clear()
        #     self.axes.remove()
        if self.plot_colorbar is not None:  # avoids adding one more colorbar at each draw operation
            self.plot_colorbar.remove()
        self.axes = self.plot_figure.gca()
        plt.subplots_adjust(top=0.934,bottom=0.098,left=0.084,right=1.0,hspace=0.2,wspace=0.2)
    
    def update_value(self,param_name,value):
        self.params[param_name] = np.array([value])
        self.x_lim = self.axes.get_xlim()
        self.y_lim = self.axes.get_ylim()
        self.draw_2d_graph()
    
    def update_resolution(self,res):
        self.x_lim = self.axes.get_xlim()
        self.y_lim = self.axes.get_ylim()
        self.resolution = res
        self.draw_2d_graph()
        
        

    
        
  
# Main Window      
class BitletPlotWidget(QWidget):
    
    def __init__(self,x_axis, y_axis,params):
        super(BitletPlotWidget,self).__init__()
        self.params_sliders = params
        self.resolution = 1000
        self.x_param = x_axis
        self.y_param = y_axis
        self.params = dict()
        self.set_ui()
        self.bitlet_model = BitletModel()
        self.canvas.draw_2d_graph()

    def set_ui(self):
        x_axis,y_axis = np.meshgrid(self.x_param.to_numpy(self.resolution),self.y_param.to_numpy(self.resolution))
        # params = {k:v.value for k,v in self.params_sliders.items()}
        # params[self.x_param.name.lower()] = x_axis
        # params[self.y_param.name.lower()] = y_axis
        
        self.curr_plot = '2d'
        self.canvas = PlotWindow(self.x_param,self.y_param,self.params_sliders,self.resolution)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        to_remove = ['Subplots', 'Customize']
        for action in self.toolbar.actions():
            if action.text() in to_remove:
                self.toolbar.removeAction(action)
        # self.params_widget = QtWidgets.QWidget(self)
        # self.paramsLayout = QGridLayout(self)
        
        # for i, param in enumerate(self.params_sliders):
        #     # self.paramsLayout.addWidget(self.params_sliders[param], i // 3, i % 3 )
        #     self.params_sliders[param].paramValueChanged.connect(self.canvas.update_value)
               
        # self.params_widget.setLayout(self.paramsLayout)
        ## setup layout
        res_hbox = QHBoxLayout()
        label = QLabel("Resolution: ",self)
        self.res_box = QComboBox(self)
        self.res_box.addItems([str(n) for n in range(500,5001,500)])
        self.res_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.res_box.setFixedSize(150,35)
        self.res_box.setCurrentIndex(1)
        self.res_box.currentIndexChanged.connect(self.update_resolution)
        
        
        res_hbox.addWidget(label)
        res_hbox.addWidget(self.res_box)
        hbox = QHBoxLayout()
        hbox.addWidget(self.toolbar)
        hbox.addLayout(res_hbox)
        
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(hbox)
        self.vbox.addWidget(self.canvas)
        # self.vbox.addWidget(self.params_widget)
        self.setLayout(self.vbox)
        
        
    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(32, 32))
        
        self.button_2d = QAction(QIcon("Icons/2d.png"), "2D", self)
        self.button_2d.setStatusTip("2D Plot")
        self.button_2d.setCheckable(True)
        self.button_2d.setChecked(True)
        
        self.button_3d = QAction(QIcon("Icons/3d.png"), "3D", self)
        self.button_3d.setStatusTip("3D Plot")
        self.button_3d.setCheckable(True)
        self.button_3d.setChecked(False)
        self.button_3d.setEnabled(False)
        # triggers
        self.button_2d.triggered.connect(lambda s: self.change_plot('2d'))

            
    def change_plot(self, who):
        if who == self.curr_plot:
            return 
        
        elif who == '2d' and self.curr_plot == '3d':
            self.curr_plot = '2d'
            self.canvas.draw_2d_graph()
  
            
    def update_resolution(self,n):
        selected =  int(self.res_box.currentText())
        self.resolution = selected
        self.canvas.update_resolution(selected)
        # self.canvas.draw_2d_graph()