import numpy as np

import pandas as pd

class pointcloud():
	"""
	Point Cloud database
	"""

	def __init__(self, points):
		self.points = points.tolist()
		self.min_index = None
		self.ground_points = []
		self.surface_points = []
		self.minmax_xy = [np.min(points[:, 0]),
		                  np.min(points[:, 1]),
		                  np.max(points[:, 0]),
		                  np.max(points[:, 1])]  # minX,minY,maxX,maxY

	def filter(self, radius, angle):
		"""
		Filter ot the points in two types according to threshold algorithm

		:param radius: Searched radius in meters
		:param angle: Treshold angle in degrees
		:return: Two lists of points ground and objects
		:type radius: float
		:type angle: float
		:rtype: list,list
		"""
		self.tan_angle_power2 = np.tan(angle) ** 2
		self.radius2 = radius ** 2

		def dist_power2(point_1, point_2):
			return (point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2

		for i in range(0, len(self.points)):
			temp_list = []
			for j in range(0, len(self.points)):
				dist2 = dist_power2(self.points[i], self.points[j])
				if  dist2 < self.radius2:
					temp_list.append([self.points[j],dist2])

			kmax = int(len(temp_list))
			added_to_surface = False
			for k in range(0,kmax):
				if temp_list[k][1] == 0.0:
					continue
				if  ((temp_list[k][0][2]-self.points[i][2])**2)/temp_list[k][1] > self.tan_angle_power2:
					if temp_list[k][0][2] < self.points[i][2]:
						self.surface_points.append(self.points[i])
						added_to_surface = True
						break
			if not added_to_surface:
				self.ground_points.append(self.points[i])


	def getlists(self):
		return self.ground_points,self.surface_points
