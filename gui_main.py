import pyqtgraph as pg
from gui import RelativityGUI
from ParamsListWidget import ScrollSpinParam,ParametersListWidget
import qtmodern.windows
import qtmodern.styles

from PyQt5.QtGui import *

app = pg.mkQApp()
qtmodern.styles.dark(app)

win = pg.QtGui.QMainWindow()
win.setCentralWidget(RelativityGUI())
dock = pg.QtGui.QDockWidget()
dock.setWidget(ParametersListWidget())
win.addDockWidget(pg.QtCore.Qt.LeftDockWidgetArea,dock)
# win = RelativityGUI()
# win = ParametersListWidget()
# win = ScrollSpinParam()
win.setWindowTitle("Bitlet")
win.resize(1100,700)
dwin = qtmodern.windows.ModernWindow(win)
dwin.show()
# win.show()
# win.loadPreset(None, 'Twin Paradox (grid)')

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()
