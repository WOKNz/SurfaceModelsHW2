import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import uic, QtWidgets, QtCore
import vtkmodules.util.numpy_support as npsup
import numpy as np


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
		self.vtk_widget = GlyphViewer(self.ui.vtk_panel,points)
		self.ui.vtk_layout = QtWidgets.QHBoxLayout()
		self.ui.vtk_layout.addWidget(self.vtk_widget)
		self.ui.vtk_layout.setContentsMargins(0,0,0,0)
		self.ui.vtk_panel.setLayout(self.ui.vtk_layout)
		self.ui.threshold_slider.setValue(50)
		self.ui.threshold_slider.valueChanged.connect(self.vtk_widget.set_threshold)
		self.ui.threshold_slider.valueChanged.connect(self.set_lb_3)

	def set_lb_3(self):
		self.ui.label_3.setText(str(self.ui.threshold_slider.value()))

	def initialize(self):
		self.vtk_widget.start()


class GlyphViewer(QtWidgets.QFrame):
	"""
	Full Vtk sequence class

	"""

	def __init__(self, parent, points):
		"""
		Builder
		:param points: An array of points (x,y,z)
		:type points: ndarray (nx3)
		"""
		super(GlyphViewer, self).__init__(parent)

		self.points = points
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


		# print(vtk_points_data)


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

	def set_threshold(self, new_value):

		# Create color scalars
		rgb3 = vtk.vtkUnsignedCharArray()
		# Setting number of scalars, number of colo channels
		rgb3.SetNumberOfComponents(3)
		rgb3.SetName("Colors")



		test = np.ones((self.points.shape))*new_value
		vtk_test = npsup.numpy_to_vtk(test,deep=1)
		vtk_test.SetName("Colors")

		rgb3.ShallowCopy(vtk_test)
		self.vtk_vertex.GetPointData().SetScalars(rgb3)
		self.mapper.SetInputData(self.vtk_vertex)
		self.mapper.Modified()
		self.actor.GetProperty().Modified()
		self.render_window.Render()

