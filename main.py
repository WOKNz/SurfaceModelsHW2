import numpy as np
from vtkwindow import GlyphViewerApp
from PyQt5 import uic, QtWidgets


if __name__ == '__main__':

    # recompile ui
    with open('glyph_view.ui') as ui_file:
        with open('glyph_ui.py', 'w') as py_ui_file:
            uic.compileUi(ui_file, py_ui_file)

    app = QtWidgets.QApplication([])
    main_window = GlyphViewerApp(np.array([[0, 0, 0]]))  # Creating app window with one point
    main_window.show()
    main_window.initialize()
    app.exec_()