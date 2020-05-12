import numpy as np

class kdtree():
	"""
	Kd-tree object, builded recursively

	:param points: Points to be in kd tree
	:param is_axis_x: Initial axis seperator
	:param p_in_leaf: Max points in Leaf
	"""

	def __init__(self, points, is_axis_x, p_in_leaf):
		self.number_of_points = points.shape[0]
		self.is_axis_x = is_axis_x
		self.points = points
		self.is_leaf = False

		self.minmax_xy = [np.min(self.points[:, 0]),
		                  np.min(self.points[:, 1]),
		                  np.max(self.points[:, 0]),
		                  np.max(self.points[:, 1])]  # minX,minY,maxX,maxY

		# Checking for leaf max size
		if self.number_of_points < p_in_leaf:
			self.is_leaf = True
			return

		# Nodes
		self.node1 = None
		self.node2 = None

		id = np.argsort(self.points[:, int(not is_axis_x)], kind='mergesort')
		self.points[:, :] = self.points[id, :]
		points_bottom_or_left = self.points[:int(len(id) / 2), :]
		points_top_or_right = self.points[int(len(id) / 2):, :]

		# Creating sons (nodes), seperator axis changed!
		self.node1 = kdtree(points_bottom_or_left, not self.is_axis_x, p_in_leaf)
		self.node2 = kdtree(points_top_or_right, not self.is_axis_x, p_in_leaf)

	def intersect_or_inside(self, center, radius, corners):
		if center[1] + radius < corners[1] or center[1] - radius > corners[3]:
			return False
		elif center[0] + radius < corners[0] or center[0] - radius > corners[2]:
			return False
		else:
			return True

	@staticmethod
	def pointsInRadius(tree, point, radius, list=[]):
		"""
		Checks relevant nodes if the intersect with circle

		:param point: Examinated point
		:param radius: Radius from that point
		:param list: Empty list for backwards points collecting (recusively)
		:return: List of points that potentialy to be in radius
		:type point: list
		:type radius: float
		:rtype: list
		"""
		stack_list = list
		if tree.intersect_or_inside(point, radius, tree.minmax_xy):
			if tree.is_leaf:
				return tree.points.tolist()
			else:
				stack_list = tree.pointsInRadius(tree.node1, point, radius, stack_list) \
				             + tree.pointsInRadius(tree.node2, point, radius, stack_list)

		return stack_list

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
		self.ground_points = []
		self.surface_points = []

		def dist_power2(point_1, point_2):
			return (point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2

		# pr = cProfile.Profile()
		# pr.enable()

		for i in range(0, len(self.points)):

			relevant_points_leafs = self.pointsInRadius(self, self.points[i], radius)
			# if i == 308:
			# 	np.savetxt('test/points2_' + str(i)+'.xyz', np.array(relevant_points_leafs))
			# 	np.savetxt('test/point2_' + str(i)+'.xyz', np.array([self.points[i]]))

			relevant_points_radius = []
			for j in range(0, len(relevant_points_leafs)):
				dist2 = dist_power2(self.points[i], relevant_points_leafs[j])
				if dist2 < self.radius2:
					relevant_points_radius.append([self.points[j], dist2])

			# if i == 300:
			# 	np.savetxt('cells.xyz', np.array(relevant_points_leafs))
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

	# if i == 20000:
	#	pr.disable()
	#	pr.dump_stats('profile400.pstat')
	# print()

	def getlists(self):
		return self.ground_points, self.surface_points
