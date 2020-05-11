import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import uic, QtWidgets, QtCore
import vtkmodules.util.numpy_support as npsup
import numpy as np
import tkinter as tk
from tkinter import filedialog, Tk
from pathlib import Path
import batchtests
from time import time


class GlyphViewerApp(QtWidgets.QMainWindow):
	def __init__(self, points):
		super(GlyphViewerApp, self).__init__()
		self.vtk_widget = None
		self.ui = None
		self.setup(points)


	def setup(self, points):
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
		self.ui.label_status.setText(filename)

	def initialize(self):
		self.vtk_widget.start()

	def run(self):
		self.ui.frame.setDisabled(True)
		self.vtk_widget.run_filter(self.ui.line_radius.text(), self.ui.line_angle.text(),
		                           self.ui.combo_type.currentIndex(), self.ui.check_ground.isChecked(),
		                           self.ui.check_surface.isChecked())
		self.ui.frame.setDisabled(False)


class GlyphViewer(QtWidgets.QFrame):
	"""
	Full Vtk sequence class
	:param points: An array of points (x,y,z)
	:type points: ndarray (nx3)
	"""
	filename_status = QtCore.pyqtSignal(str)

	def __init__(self, parent, points):
		super(GlyphViewer, self).__init__(parent)

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
		actor.GetProperty().SetColor(1.0, 0.0, 0.0) # Setting color of the source
		renderer.AddActor(actor)
		renderer.ResetCamera()





		render_window.Render()


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
		self.interactor.Initialize()
		self.interactor.Start()

	def button_load(self):
		def pull():
			root = tk.Tk()
			root.withdraw()
			files = filedialog.askopenfilename(multiple=True)
			return root.tk.splitlist(files)

		Tk().withdraw()
		file_path = pull()[0]
		file_path = file_path.replace("/", "\\")
		self.temp_points = np.genfromtxt(file_path)  # (X,Y,Z)
		self.filename_status.emit(Path(file_path).stem)
		# print(self.filename_status)
		# Passing points to rerender
		self.reredner_points([[self.temp_points, [255, 255, 255]]])

	def reredner_points(self, list_of_points):

		temp_RGB = np.array([[0, 0, 0]]).reshape((1, 3))
		temp_points = np.array([[0, 0, 0]]).reshape((1, 3))

		# Creating temp array for colors
		rgb3 = vtk.vtkUnsignedCharArray()
		# Setting number of scalars, number of colo channels
		rgb3.SetNumberOfComponents(3)
		rgb3.SetName("Colors")

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

		# Updating points
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

		from pointcloud import pointcloud
		from equalcells import eqlcells
		from kdtree import kdtree

		def databaseType(db_type: int, points):

			if db_type == 0:
				return pointcloud(points)
			elif db_type == 1:
				return eqlcells(points)
			elif db_type == 2:
				return kdtree(points, False, 10)

		db_object = databaseType(db_type, self.temp_points)

		start = time()
		db_object.filter(float(radius), (float(angle) * np.pi) / 180.0)
		finish = time()
		self.time_results = finish - start

		list1, list2 = db_object.getlists()

		# 	np.savetxt(ground_p_str, np.array(list1))
		# 	np.savetxt(surface_p_str, np.array(list2))
		# 	time_results_pd = pd.DataFrame(time_results)
		# 	time_results_pd.to_csv(output_folder + 'speedtest/' + filename + 'speed_results.csv')
		#
		# print(radius)
		# print(angle)
		# print(db_type)
		# print(is_ground_pnts)
		# print(is_objects_pnts)

		if is_ground_pnts and is_objects_pnts:
			self.reredner_points([[np.array(list1), [0, 255, 0]], [np.array(list2), [255, 0, 0]]])
		elif is_objects_pnts and not is_ground_pnts:
			self.reredner_points([[np.array(list2), [255, 0, 0]]])
		elif is_ground_pnts and not is_objects_pnts:
			self.reredner_points([[np.array(list1), [0, 255, 0]]])
		else:
			pass
