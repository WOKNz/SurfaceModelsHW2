import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor  # Not at error!
from PyQt5 import uic, QtWidgets, QtCore
import vtkmodules.util.numpy_support as npsup  # Set data without loops in vtk
import numpy as np
import tkinter as tk
from tkinter import filedialog, Tk
from pathlib import Path
import os
from time import time


class GlyphViewerApp(QtWidgets.QMainWindow):
	"""
	PyQt5 Main Window Class
	"""

	def __init__(self, points):
		super(GlyphViewerApp, self).__init__()
		self.vtk_widget = None
		self.ui = None
		self.setup(points)

	def setup(self, points):
		"""
		Function that creates the link to qVtk including interface elements

		:param points:nx3 points data
		:type points: ndarray
		"""
		import glyph_ui
		self.ui = glyph_ui.Ui_MainWindow()
		self.ui.setupUi(self)
		self.vtk_widget = GlyphViewer(self.ui.vtk_panel, points)
		self.ui.vtk_layout = QtWidgets.QHBoxLayout()
		self.ui.vtk_layout.addWidget(self.vtk_widget)
		self.ui.vtk_layout.setContentsMargins(0, 0, 0, 0)
		self.ui.vtk_panel.setLayout(self.ui.vtk_layout)
		self.ui.button_load.clicked.connect(self.vtk_widget.button_load)
		self.vtk_widget.filename_status.connect(self.set_status_loaded)
		self.ui.button_run.clicked.connect(self.run)

	def set_status_loaded(self, filename):
		"""
		Updates label with which files has been loaded
		"""
		self.ui.label_status.setText(filename)

	def initialize(self):
		"""
		Initializes Vtk Widget
		"""
		self.vtk_widget.start()

	def run(self):
		"""
		Initiates filtering process with set parameters
		"""
		self.ui.frame.setDisabled(True)
		self.vtk_widget.run_filter(self.ui.line_radius.text(), self.ui.line_angle.text(),
		                           self.ui.combo_type.currentIndex(), self.ui.check_ground.isChecked(),
		                           self.ui.check_surface.isChecked())
		self.ui.frame.setDisabled(False)


class GlyphViewer(QtWidgets.QFrame):
	"""
	Full Vtk frame class
	"""
	filename_status = QtCore.pyqtSignal(str)

	def __init__(self, parent, points):
		super(GlyphViewer, self).__init__(parent)

		# Setting the conectivity
		interactor = QVTKRenderWindowInteractor(self)
		self.layout = QtWidgets.QHBoxLayout()
		self.layout.addWidget(interactor)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)

		# Setup VTK environment
		renderer = vtk.vtkRenderer()
		render_window = interactor.GetRenderWindow()
		render_window.AddRenderer(renderer)

		interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
		render_window.SetInteractor(interactor)
		renderer.SetBackground(0.2, 0.2, 0.2)


		# Create Point object
		vtk_points_data = vtk.vtkPoints()
		# Create color scalars
		rgb = vtk.vtkUnsignedCharArray()
		# Setting number of scalars, number of colo channels
		rgb.SetNumberOfComponents(3)
		# Setting name of scalars set
		rgb.SetName("Colors")

		# Creating id objects for PolyData
		vtk_points_topology = vtk.vtkCellArray()

		# Setting up PolyData - Vertices
		points_list_ids = []
		vtk_points_data.SetData(npsup.numpy_to_vtk(points[:, 0:3]))
		vtk_points_topology.InsertNextCell(points.shape[0], list(range(0, len(points))))
		# print('len of points:',len(points_list_ids))
		# Initializing PolyData (vertices)
		vtk_vertex = vtk.vtkPolyData()


		# Set the vertices we created as the geometry and topology of the polydata
		vtk_vertex.SetPoints(vtk_points_data)
		vtk_vertex.SetVerts(vtk_points_topology)

		# Create Mapper
		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputData(vtk_vertex)

		# Create and connect Actor
		actor = vtk.vtkActor()
		actor.SetMapper(mapper) # Passing the mapped source to actor
		actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Setting color of the source
		renderer.AddActor(actor)
		renderer.ResetCamera()

		render_window.Render()

		# Make variables belong to the Vtk widget
		self.vtk_points_data = vtk_points_data
		self.vtk_points_topology = vtk_points_topology
		self.mapper = mapper
		self.vtk_vertex = vtk_vertex
		self.actor = actor
		self.renderer = renderer
		self.interactor = interactor
		self.render_window = render_window
		self.rgb = rgb

	def start(self):
		"""
		Starts the Vtk presentation
		"""
		self.interactor.Initialize()
		self.interactor.Start()

	def button_load(self):
		"""
		Loading points file and start preview of it
		"""

		def pull():
			root = tk.Tk()
			root.withdraw()
			files = filedialog.askopenfilename(multiple=True)
			return root.tk.splitlist(files)

		Tk().withdraw()
		file_path = pull()[0]
		self.file_path = file_path.replace("/", "\\")
		self.temp_points = np.genfromtxt(self.file_path)  # (X,Y,Z)
		self.filename_status.emit(Path(self.file_path).stem)
		# print(self.filename_status)
		# Passing points to rerender
		self.reredner_points([[self.temp_points, [255, 255, 255]]])

	def reredner_points(self, list_of_points):
		"""
		Updates label with which files has been loaded

		:param list_of_points: List of points xyz, xn3
		:type list_of_points: ndarray
		"""
		temp_RGB = np.array([[0, 0, 0]]).reshape((1, 3))
		temp_points = np.array([[0, 0, 0]]).reshape((1, 3))

		# Creating temp array for colors
		rgb3 = vtk.vtkUnsignedCharArray()
		# Setting number of scalars, number of colo channels
		rgb3.SetNumberOfComponents(3)
		rgb3.SetName("Colors")

		# Creating array of RGB and points
		for points in list_of_points:
			# Setting color
			R = np.ones((points[0].shape[0], 1)) * points[1][0]
			G = np.ones((points[0].shape[0], 1)) * points[1][1]
			B = np.ones((points[0].shape[0], 1)) * points[1][2]
			temp_RGB = np.append(temp_RGB, np.concatenate((R, G, B), axis=1), axis=0)
			temp_points = np.append(temp_points, points[0], axis=0)

		# Removing null row
		temp_RGB = np.delete(temp_RGB, 0, 0)
		temp_points = np.delete(temp_points, 0, 0)

		# Converting to VTKArray and updating points+colors
		self.vtk_points_data.SetData(npsup.numpy_to_vtk(temp_points[:, 0:3]))
		self.vtk_points_topology = vtk.vtkCellArray()
		self.vtk_points_topology.InsertNextCell(temp_points.shape[0], list(range(0, temp_points.shape[0])))
		self.vtk_vertex.SetVerts(self.vtk_points_topology)

		vtk_test = npsup.numpy_to_vtk(temp_RGB, deep=1)
		vtk_test.SetName("Colors")

		# Copying data to proper array type
		rgb3.ShallowCopy(vtk_test)

		# Adding colors to points
		self.vtk_vertex.GetPointData().SetScalars(rgb3)

		# Update interface
		# self.actor.RotateX(np.pi)
		# self.actor.RotateY(0)
		# self.actor.RotateZ(0)
		self.renderer.ResetCamera()
		self.render_window.Render()

	def start(self):
		self.interactor.Initialize()
		self.interactor.Start()

	def run_filter(self, radius, angle, db_type, is_ground_pnts, is_objects_pnts):
		"""
		Starting the process of filtering of loaded file with set parameters

		:param radius: Searched radius in meters
		:param angle: Treshold angle in degrees
		:param db_type: Type of database (Point Cloud = 0, Equal Cells = 1, K-d tree = 2)
		:param is_ground_pnts: Parameter to show or not ground points
		:param is_objects_pnts: Parameter to show or not objects points
		:type radius: str
		:type angle: str
		:type db_type: int
		:type is_ground_pnts: bool
		:type is_objects_pnts: bool
		"""

		from pointcloud import pointcloud
		from equalcells import eqlcells
		from kdtree import kdtree

		def databaseType(db_type: int, points):
			"""
			Returns db object depended on db type
			"""
			if db_type == 0:
				return pointcloud(points)
			elif db_type == 1:
				return eqlcells(points)
			elif db_type == 2:
				return kdtree(points, False, 10)

		# Calling for object creating
		self.db_object = databaseType(db_type, self.temp_points)

		start = time()
		# Filtering
		self.db_object.filter(float(radius), (float(angle) * np.pi) / 180.0)
		finish = time()
		self.time_results = finish - start

		list1, list2 = self.db_object.getlists()

		# Displaying according to set parameter of visibility (user)
		if is_ground_pnts and is_objects_pnts:
			self.reredner_points([[np.array(list1), [0, 255, 0]], [np.array(list2), [255, 0, 0]]])
		elif is_objects_pnts and not is_ground_pnts:
			self.reredner_points([[np.array(list2), [255, 0, 0]]])
		elif is_ground_pnts and not is_objects_pnts:
			self.reredner_points([[np.array(list1), [0, 255, 0]]])
		else:
			pass

		# Creating output txt file with brief resutls
		f = open("result.txt", "w+")
		f.write("Bounding box: " + str(self.db_object.minmax_xy) + " (minX,minY,maxX,maxY)\n")
		f.write("Radius: " + radius + "(m)\n")
		f.write("Angle: " + angle + "deg\n")
		f.write("Number of points: " + str(self.temp_points.shape[0]) + "\n")
		f.write("Number of ground points: " + str(len(list1)) + "\n")
		f.write("Number of object points: " + str(len(list2)) + "\n")
		f.write("Rate of object points: " + str(len(list2) / self.temp_points.shape[0]) + "\n")
		if db_type == 1:
			f.write("Avg points per cell: " + str(int(self.temp_points.shape[0] / 100.0)) + "\n")
		f.write("Runtime of filtering: " + str(self.time_results) + "s\n")
		f.close()

		osCommandString = "notepad.exe result.txt"
		os.system(osCommandString)
