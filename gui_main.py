
import sys, os
from PyQt5 import QtWidgets, QtCore
from gui import BitletModelGUI
from ParamsListWidget import ParametersListWidget
from BitletPlotWidget import BitletPlotWidget
import qtmodern.windows
import qtmodern.styles


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    main = BitletModelGUI()
    dwin = qtmodern.windows.ModernWindow(main)
    dwin.show()
    app.exec_()
