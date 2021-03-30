from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from BitletModelParams import BitletParams
from BitletModel import BitletModel
import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.pyplot import figure, xlabel
from matplotlib import ticker 
from matplotlib.scale import LogScale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors 

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import QAction, QApplication, QVBoxLayout , QWidget, QPushButton, QToolBar
from PyQt5.QtWidgets import QLabel , QGridLayout, QDesktopWidget, QSizePolicy




class PlotWindow(FigureCanvas):
    def __init__(self,x_axis,y_axis,params):
        self.plot_colorbar = None
        
        self.plot_figure = figure()
        FigureCanvas.__init__(self, self.plot_figure)  
        self.axes = None
        self.setWindowTitle("Plot") 
        self.x_axis = x_axis
        self.y_axis = y_axis
        # self.x_mesh,self.y_axis = np.meshgrid(self.x_axis.to_numpy(), self.y_axis.to_numpy())
        self.params = params
        self.bitlet_model = BitletModel()
        
    def draw_2d_graph(self):  # Function for graph plotting
        self.clear_plot()
        # self.axes = self.plot_figure.gca() 
        # x_axis , y_axis = np.meshgrid(self.x_axis.to_numpy(), self.y_axis.to_numpy())
        z,z2 = self.bitlet_model.combined_power_throughput(**self.params)
        # norm = colors.LogNorm(vmin=int(z.min()),vmax=int(z.max()),clip=True)
        norm = colors.LogNorm()
        self.axes = sns.heatmap(z, cmap=plt.get_cmap('RdYlGn'), linewidths=0, norm=norm)
        # levels = np.logspace(1,12,num=12,base=2,dtype=int)
        # plot_stuff = self.axes.pcolormesh(x_axis, y_axis, z, cmap=plt.get_cmap('RdYlGn'), norm=nrm)
        # eq_lines = self.axes.contourf(x_axis, y_axis, z,locator=ticker.LogLocator())
        # eq_lines = self.axes.contour(x_axis, y_axis, z,levels=levels)
        # self.axes.clabel(eq_lines,levels, inline=True,  fontsize=10, fmt='%d')
        self.axes.set_xlabel(f"{self.x_axis.name} {self.x_axis.units}")
        self.axes.set_ylabel(f"{self.y_axis.name} {self.y_axis.units}")
        minx = self.x_axis.min #* (10 ^ self.x_axis.factor)
        maxx = self.x_axis.max #* (10 ^ self.x_axis.factor)
        miny = self.y_axis.min #* (10 ^ self.y_axis.factor)
        maxy = self.y_axis.max #* (10 ^ self.y_axis.factor)
        self.axes.set_xlim(xmin=minx , xmax=maxx)
        self.axes.set_ylim(ymin=miny, ymax=maxy)
        self.axes.set_xscale("log",basex=2)
        self.axes.set_yscale("log",basey=2)
        # self.plot_colorbar = self.plot_figure.colorbar(plot_stuff)
        self.draw()
    
    
    def draw_3d_graph(self):  # Function for graph plotting
        self.clear_plot()
        self.plot_figure.clf()
        self.axes = self.plot_figure.gca(projection='3d') 
        x_axis , y_axis = np.meshgrid(self.x_axis.to_numpy(), self.y_axis.to_numpy())
        
        z,z2 = self.bitlet_model.combined_power_throughput(**self.params)
        plot_stuff = self.axes.plot_surface(x_axis, y_axis, z, linewidth=1, antialiased=False)
        # self.axes.zaxis.set_major_locator(ticker.LogLocator(10))
        # self.axes.zaxis.set_major_formatter(ticker.FormatStrFormatter('%.02f'))
        self.axes.set_xlabel(f"{self.x_axis.name} {self.x_axis.units}")
        self.axes.set_ylabel(f"{self.y_axis.name} {self.y_axis.units}")
        minx = self.x_axis.min #* (10 ^ self.x_axis.factor)
        maxx = self.x_axis.max #* (10 ^ self.x_axis.factor)
        miny = self.y_axis.min #* (10 ^ self.y_axis.factor)
        maxy = self.y_axis.max #* (10 ^ self.y_axis.factor)
        self.axes.set_xlim(minx, maxx)
        self.axes.set_ylim(miny, maxy)
        # Add a color bar which maps values to colors.
        self.plot_colorbar = self.plot_figure.colorbar(plot_stuff)
        # draw plot
        self.draw()
    
    def clear_plot(self):
        self.plot_figure.clf()
        if self.axes is not None:    
            self.axes.clear()
        #     self.axes.remove()
        if self.plot_colorbar is not None:  # avoids adding one more colorbar at each draw operation
            self.plot_colorbar.remove()
    
    def update_value(self,param_name,value):
        self.params[param_name] = np.array([value])
        self.draw_2d_graph()
        
        


    
        
  
# Main Window      
class BitletPlotWidget(QWidget):
    
    def __init__(self,x_axis, y_axis,params):
        super(BitletPlotWidget,self).__init__()
        self.params_sliders = params
        self.x_param = x_axis
        self.y_param = y_axis
        self.params = dict()
        self.set_ui()
        
        self.bitlet_model = BitletModel()
    
        # self.change_plot('3d')
        self.canvas.draw_2d_graph()

    def set_ui(self):
        self.setup_toolbar()
        ## set up params 
        ## setup canvas area
        x_axis,y_axis = np.meshgrid(self.x_param.to_numpy(),self.y_param.to_numpy())
        params = {k:v.value for k,v in self.params_sliders.items()}
        params[self.x_param.name.lower()] = x_axis
        params[self.y_param.name.lower()] = y_axis
        
        self.curr_plot = '2d'
        self.canvas = PlotWindow(self.x_param,self.y_param,params)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.params_widget = QtWidgets.QWidget(self)
        self.paramsLayout = QGridLayout(self)
        
        for i, param in enumerate(self.params_sliders):
            self.paramsLayout.addWidget(self.params_sliders[param], i // 3, i % 3 )
            self.params_sliders[param].paramValueChanged.connect(self.canvas.update_value)
               
        self.params_widget.setLayout(self.paramsLayout)
        ## setup layout
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.params_widget)
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
        self.button_3d.triggered.connect(lambda s: self.change_plot('3d'))
        self.button_2d.triggered.connect(lambda s: self.change_plot('2d'))
        
        self.toolbar.addAction(self.button_2d)
        self.toolbar.addAction(self.button_3d)
        
            
    def change_plot(self, who):
        if who == self.curr_plot:
            return 
        elif who == '3d' and self.curr_plot == '2d':
            self.button_2d.setChecked(False)
            self.button_3d.setChecked(True)
            self.curr_plot = '3d'
            self.canvas.draw_3d_graph()
        
        elif who == '2d' and self.curr_plot == '3d':
            self.button_3d.setChecked(False)
            self.button_2d.setChecked(True)
            self.curr_plot = '2d'
            self.canvas.draw_2d_graph()
        
    def param_update(self,param_name, value):
        # self.bitlet_model.update_param(param_name,value)
        self.comb_throughput = self.bitlet_model.combined_throughput()
        if self.curr_plot == '2d':
            self.canvas.draw_2d_graph()
        else:
            self.canvas.draw_3d_graph(self.x_param, self.y_param, self.comb_throughput)