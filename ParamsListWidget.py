import numpy as np
import collections
import sys, os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


class ParametersListWidget(QtGui.QWidget):
    def __init__(self, title='ParamsList'):
        QtGui.QWidget.__init__(self)
        
        self.title = title
        self.setupUi()
        
        self.setLayout(self.paramsListLayout)
        self.show()
        
        

    def setupUi(self):
        self.verticalLayoutWidget = QtGui.QWidget()
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 40, 291, 161))
        self.paramsListLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.paramsListLayout.setObjectName(u"verticalLayout_2")
        self.paramsListLayout.setContentsMargins(0, 0, 0, 0)
        self.param1 = ScrollSpinParam('BW')
        self.param2 = ScrollSpinParam('Rows')
        self.button = pg.FeedbackButton("&Plot")


        self.paramsListLayout.addWidget(self.param1)
        self.paramsListLayout.addWidget(self.param2)
        self.paramsListLayout.addWidget(self.button)





class ScrollSpinParam(QtGui.QWidget):
    def __init__(self,label='param'):
        QtGui.QWidget.__init__(self)
        
        self.title = label
        self.setupUi()
        
        self.setLayout(self.paramLayout)
        self.show()
        
    
    def setupUi(self):
        self.gridLayoutWidget = QtGui.QWidget()
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 60, 361, 80))
        self.paramLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.paramLayout.setObjectName(u"gridLayout")
        self.paramLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.paramLayout.setHorizontalSpacing(12)
        self.paramLayout.setContentsMargins(5, 0, 1, 0)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(self.title)
        self.label.setText(self.title)
        self.label.setSizeIncrement(QtCore.QSize(8, 0))

        self.paramLayout.addWidget(self.label, 0, 0, 1, 1)

        self.spinBox = pg.SpinBox(self.gridLayoutWidget)
        self.spinBox.setObjectName(u"spinBox")

        self.paramLayout.addWidget(self.spinBox, 0, 1, 1, 1)

        self.horizontalSlider = QtGui.QSlider(self.gridLayoutWidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)

        self.paramLayout.addWidget(self.horizontalSlider, 0, 2, 1, 1)

        self.spinBox.valueChanged.connect(self.horizontalSlider.setValue)
        self.horizontalSlider.valueChanged.connect(self.spinBox.setValue)


