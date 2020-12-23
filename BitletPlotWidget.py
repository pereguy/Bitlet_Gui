import sys
import random

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
    
    def __init__(self,size=(5.0, 4.0), dpi=100):
        super(BitletPlotWidget,self).__init__()
        self.fig = Figure(size, dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.canvas)
        
        self.setLayout(self.vbox)

    def getFigure(self):
        return self.fig
        
    def draw(self):
        self.canvas.draw()



        
