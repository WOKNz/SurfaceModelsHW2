import numpy as np
import tkinter as tk
from tkinter import filedialog, Tk
from vtkwindow import GlyphViewerApp
from PyQt5 import uic, QtWidgets


if __name__ == '__main__':

    # Load data with TK
    # importing files

    # def pull():
    #     root = tk.Tk()
    #     root.withdraw()
    #     files = filedialog.askopenfilename(multiple=True)
    #     return root.tk.splitlist(files)
    #
    # Tk().withdraw()
    # file_path = pull()[0]
    #
    #
    # # Load Data
    # # Load points
    # file_path = file_path.replace("/", "\\")
    #
    #
    #
    #
    # points = np.genfromtxt(file_path) # (X,Y,Z,R,G,B)
    # # points = load(file_path, ' ') # (X,Y,Z,R,G,B)

    # recompile ui
    with open('glyph_view.ui') as ui_file:
        with open('glyph_ui.py', 'w') as py_ui_file:
            uic.compileUi(ui_file, py_ui_file)

    app = QtWidgets.QApplication([])
    main_window = GlyphViewerApp(np.array([[0,0,0]]))
    main_window.show()
    main_window.initialize()
    app.exec_()