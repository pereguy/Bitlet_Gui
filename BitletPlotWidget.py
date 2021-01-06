from BitletModel import BitletModel
import sys
import random
import seaborn as sbn
import pyqtgraph as pg
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BitletPlotWidget(QtWidgets.QWidget):
    """
    Implements a Matplotlib figure inside a QWidget.
    Use getFigure() and redraw() to interact with matplotlib.
    
    Example::
    
        mw = MatplotlibWidget()
        subplot = mw.getFigure().add_subplot(111)
        subplot.plot(x,y)
        mw.draw()
    """
    
    def __init__(self,size=(5.0, 4.0), dpi=100, params_list=None):
        super(BitletPlotWidget,self).__init__()
        self.params_widget = params_list
        
        self.bitlet_model = BitletModel(self.params_widget.get_model_params())
        
        self.fig = Figure(dpi=dpi)
        self.plot = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.params_widget)
        
        self.setLayout(self.vbox)
        # self.draw()

    def getFigure(self):
        return self.fig
        
    def draw(self):
        sbn.heatmap(self.bitlet_model.combined_throughput(),ax=self.plot)
        self.canvas.draw()



        
