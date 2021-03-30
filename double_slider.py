import sys
import numpy as np
import math
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal

class DoubleSlider(QtWidgets.QSlider):
    doubleValueChanged = pyqtSignal(float)
    
    def __init__(self, minimum, maximum, step, value=None):
        super(DoubleSlider,self).__init__()
        self._min_value = minimum
        self._max_value = maximum 
        self._step = step
        self.cast = (type(step) != int)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setTracking(False)
        # self.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        
        self.setSingleStep(step)
        self.setValue(value)
        self.setMinimum(0)
        self.setMaximum(self._step_count)
        self.valueChanged.connect(self.emitDoubleValueChanged)
        self.setStyleSheet(super(DoubleSlider, self).styleSheet())
    
    def emitDoubleValueChanged(self):
        value = (float(super(DoubleSlider, self).value())  * self._step) + self._min_value
        self.doubleValueChanged.emit(value)

    @property
    def _step_count(self):
        return int(math.ceil((self._max_value - self._min_value) / self._step))

    def value(self):
        int_value = super(DoubleSlider, self).value()
        return (float(int_value)  * self._step ) + self._min_value
            

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int((value - self._min_value) / self._step))

    def setRange(self, range_min, range_max):
        assert range_min < range_max
        self._min_value = range_min
        self._max_value = range_max
        super(DoubleSlider, self).setRange(0, self._step_count)

    def singleStep(self):
        return self._step

    def setSingleStep(self, value):
        self._step = value
        assert value > 0
        assert self._step_count > 0
        super(DoubleSlider, self).setRange(0, self._step_count)
        return super(DoubleSlider, self).setSingleStep(1)
    
    # def setMinimum(self, value):
    #     if value > self._max_value:
    #         raise ValueError("Minimum limit cannot be higher than maximum")

    #     self._min_value = value
    #     self.setValue(self.value())

    # def setMaximum(self, value):
    #     if value < self._min_value:
    #         raise ValueError("Minimum limit cannot be higher than maximum")

    #     self._max_value = value
    #     self.setValue(self.value())

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value
    
    
    
