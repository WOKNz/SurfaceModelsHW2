import numpy as np
from pathlib import Path
import pandas as pd


class eqlcells():
	def __init__(self, points):
		self.points = points.tolist()
		self.points_np = points
		self.min_index = None
		self.ground_points = []
		self.surface_points = []
		self.minmax_xy = [np.min(self.points_np[:, 0]),
		                  np.min(self.points_np[:, 1]),
		                  np.max(self.points_np[:, 0]),
		                  np.max(self.points_np[:, 1])]  # minX,minY,maxX,maxY
		self.diffX = self.minmax_xy[2] - self.minmax_xy[0]
		self.diffY = self.minmax_xy[3] - self.minmax_xy[1]

		# Creating initial grid coordinates
		self.x_grid_corners = np.linspace(self.minmax_xy[0], self.minmax_xy[2], 11, endpoint=True)
		self.y_grid_corners = np.linspace(self.minmax_xy[3], self.minmax_xy[1], 11, endpoint=True)
		self.x_grid, self.y_grid = np.meshgrid(self.x_grid_corners, self.y_grid_corners)
		self.grid = np.stack((self.x_grid, self.y_grid), axis=2)
		self.cells_list = []

		# Creating Grid of cells
		for row in range(1, self.grid.shape[1]):
			temp_list = []
			for column in range(1, self.grid.shape[0]):
				temp_list.append(self.cell(self.grid[row - 1:row + 1, column - 1:column + 1, :]))
				# np.savetxt('test/cell_' + str(row) + 'x' + str(column)+'.xyz', np.array(temp_list[-1].getCorners()))
			self.cells_list.append(temp_list)

		# Add points to cells
		for point in self.points:
			self.addPointsToCells(point)


		# print('debug')

	class cell():
		def __init__(self, corners, points=None):
			self.corners = corners
			if points is None:
				self.points = []
			else:
				self.points = points

		def getPoints(self):
			return self.points

		def getCorners(self):
			temp_list = []
			temp_list.append([self.corners[0,0,0],self.corners[0,0,1]])
			temp_list.append([self.corners[0,1,0],self.corners[0,1,1]])
			temp_list.append([self.corners[1,0,0],self.corners[1,0,1]])
			temp_list.append([self.corners[1,1,0],self.corners[1,1,1]])
			return temp_list

		def addPoint(self, point):
			self.points.append(point)

	def addPointsToCells(self, point):
		cell_column = int((point[0] - self.minmax_xy[0]) * 10.0 / self.diffX)
		cell_row = int((point[1] - self.minmax_xy[1]) * 10.0 / self.diffY)
		if cell_row == 10:
			cell_row = cell_row - 1
		if cell_column == 10:
			cell_column = cell_column - 1
		self.cells_list[9-cell_row][cell_column].addPoint(point)
		# if cell_row == 0 or cell_column == 0 or cell_row == 9 or cell_column == 0:
		#np.savetxt('test/first_box' + str(cell_row)+'x'+str(cell_column)+ '.xyz', np.array(self.cells_list[cell_row][cell_column].getCorners()))

	def intersect(self, center, radius, cell):
		if center[1] + radius < cell.corners[1, 0, 1] or center[1] - radius > cell.corners[0, 0, 1]:
			return False
		elif center[0] + radius < cell.corners[0, 0, 0] or center[0] - radius > cell.corners[0, 1, 0]:
			return False
		else:
			return True

	def pointsInRadius(self, point, radius):
		temp_list = []
		for row in range(0, len(self.cells_list)):
			for column in range(0, len(self.cells_list[0])):
				if self.intersect(point, radius, self.cells_list[row][column]):
					temp_list.append(self.cells_list[row][column].getPoints())

		flat_list = []
		for sublist in temp_list:
			for item in sublist:
				flat_list.append(item)
		return flat_list

	def filter(self, radius, angle):
		self.tan_angle_power2 = np.tan(angle) ** 2
		self.radius2 = radius ** 2

		def dist_power2(point_1, point_2):
			return (point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2

		for i in range(0, len(self.points)):
			relevant_points_cells = self.pointsInRadius(self.points[i], radius)
			# if i == 308:
			# 	np.savetxt('test/points2_' + str(i)+'.xyz', np.array(relevant_points_cells))
			# 	np.savetxt('test/point2_' + str(i)+'.xyz', np.array([self.points[i]]))


			relevant_points_radius = []
			for j in range(0, len(relevant_points_cells)):
				dist2 = dist_power2(self.points[i], relevant_points_cells[j])
				if dist2 < self.radius2:
					relevant_points_radius.append([self.points[j], dist2])

			# if i == 300:
			# 	np.savetxt('cells.xyz', np.array(relevant_points_cells))
			# 	np.savetxt('radius.xyz', np.array(relevant_points_radius))

			kmax = int(len(relevant_points_radius))
			added_to_surface = False
			for k in range(0, kmax):
				if relevant_points_radius[k][1] == 0.0:
					continue
				if ((relevant_points_radius[k][0][2] - self.points[i][2]) ** 2) / relevant_points_radius[k][
					1] > self.tan_angle_power2:
					if relevant_points_radius[k][0][2] < self.points[i][2]:
						self.surface_points.append(self.points[i])
						added_to_surface = True
						break
			if not added_to_surface:
				self.ground_points.append(self.points[i])

	def getlists(self):
		return self.ground_points, self.surface_points


if __name__ == '__main__':
	# path = 'Data/DataPoints/AD9_2.xyz'
	# (X,Y,Z,R,G,B)
	# temp_points = np.array([[-1,-1,0],
	# 						[-1,1,0],
	# 						[1,-1,0],
	# 						[1,1,0],
	# 						[0,0,10]])

	import datetime

	tests = [[0.5,0.5,15],[2,0.75,15],[3,1.0,15],[4,1.5,15],[5,2,65],[6,3,65],[7,4,65],[8,5,65]]
	# tests = [[1, 2, 15]]
	paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz']
	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz','ullmann_subset.xyz']
	# paths = ['AD9_2.xyz']
	# paths = ['ullmann_subset.xyz']

	for path in paths:
		time_results = []
		filename = Path(path).stem
		full_path = 'Data/DataPoints/' + path
		for test in tests:
			ground_p_str = 'results2/' + filename + '_ground_' + str(test[0]) + '.xyz'
			surface_p_str = 'results2/' + filename + '_surface_' + str(test[0]) + '.xyz'
			temp_points = np.genfromtxt(full_path)
			eqlcl1 = eqlcells(temp_points)

			start = datetime.datetime.now()
			eqlcl1.filter(test[1], (test[2] * np.pi) / 180.0)
			finish = datetime.datetime.now()
			time_results.append([filename, test[0], finish - start])
			list1, list2 = eqlcl1.getlists()
			np.savetxt(ground_p_str, np.array(list1))
			np.savetxt(surface_p_str, np.array(list2))
		time_results_pd = pd.DataFrame(time_results)
		time_results_pd.to_csv('speedtest/' + filename + 'resutls_equallcells.csv')
		print('File:' + filename + '\nDone!')

# import datetime
#
# # test = [1,0.5,15]
# # time_results = []
# # full_path = 'Data/DataPoints/AD9_2.xyz'
# #
# # ground_p_str = 'results2/'+'AD9_2'+'_ground_'+str(test[0])+'.xyz'
# # surface_p_str = 'results2/'+'AD9_2'+'_surface_'+str(test[0])+'.xyz'
# # temp_points = np.genfromtxt(full_path)
#
#
# eqlcells1 = eqlcells(temp_points)
# start = datetime.datetime.now()
# eqlcells1.filter(test[1], (test[2] * np.pi) / 180.0)
# finish = datetime.datetime.now()
# time_results.append(['AD9_2',test[0],finish-start])
# list1, list2 = eqlcells1.getlists()
# np.savetxt(ground_p_str, np.array(list1))
# np.savetxt(surface_p_str, np.array(list2))
# time_results_pd = pd.DataFrame(time_results)
# time_results_pd.to_csv('AD9_2'+'resutls_eqlcells.csv')
