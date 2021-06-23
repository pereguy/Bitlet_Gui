
import sys, os
from PyQt5 import QtWidgets
from gui import BitletModelGUI
import qtmodern.styles
from qt_material import apply_stylesheet


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    # import pyqtgraph.examples
    # pyqtgraph.examples.run()
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # qtmodern.styles.dark(app)
    main = BitletModelGUI()
    apply_stylesheet(app, theme='dark_blue.xml')
    
    # dwin = qtmodern.windows.ModernWindow(main)
    # dwin.show()
    main.show()
    app.exec_()
