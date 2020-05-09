import numpy as np

class kdtree():
	def __init__(self, points, is_axis_x, p_in_leaf):
		self.number_of_points = points.shape[0]
		self.is_axis_x = is_axis_x
		self.points = points
		self.is_leaf = False

		self.minmax_xy = [np.min(self.points[:, 0]),
		                  np.min(self.points[:, 1]),
		                  np.max(self.points[:, 0]),
		                  np.max(self.points[:, 1])]  # minX,minY,maxX,maxY

		# Checking for leaf
		if self.number_of_points < p_in_leaf:
			self.is_leaf = True
			return

		self.node1 = None
		self.node2 = None

		id = np.argsort(self.points[:, int(not is_axis_x)], kind='mergesort')
		self.points[:, :] = self.points[id, :]
		points_bottom_or_left = self.points[:int(len(id) / 2), :]
		points_top_or_right = self.points[int(len(id) / 2):, :]

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
		stack_list = list
		if tree.intersect_or_inside(point, radius, tree.minmax_xy):
			if tree.is_leaf:
				return tree.points.tolist()
			else:
				stack_list = tree.pointsInRadius(tree.node1, point, radius, stack_list) \
				             + tree.pointsInRadius(tree.node2, point, radius, stack_list)

		return stack_list

	def filter(self, radius, angle):
		self.tan_angle_power2 = np.tan(angle) ** 2
		self.radius2 = radius ** 2
		self.ground_points = []
		self.surface_points = []

		def dist_power2(point_1, point_2):
			return (point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2

		pr = cProfile.Profile()
		pr.enable()

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
			if i == 20000:
				pr.disable()
				pr.dump_stats('profile400.pstat')
				print()

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

	from pathlib import Path
	import datetime
	import pandas as pd

	# tests = [[1,0.5,15],[2,0.75,15],[3,1.0,15],[4,1.5,15],[5,2,65],[6,3,65],[7,4,65],[8,5,65]]
	tests = [[1, 0.5, 15]]
	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz']
	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz','ullmann_subset.xyz']
	# paths = ['AD9_2.xyz']
	paths = ['ullmann_subset.xyz']

	for path in paths:
		time_results = []
		filename = Path(path).stem
		full_path = 'Data/DataPoints/' + path
		for test in tests:
			ground_p_str = 'results3/' + filename + '_ground_' + str(test[0]) + '.xyz'
			surface_p_str = 'results3/' + filename + '_surface_' + str(test[0]) + '.xyz'
			temp_points = np.genfromtxt(full_path)

			kdtree1 = kdtree(temp_points, False, 40)

			start = datetime.datetime.now()

			import cProfile

			kdtree1.filter(test[1], (test[2] * np.pi) / 180.0)
			finish = datetime.datetime.now()
			time_results.append([filename, test[0], finish - start])
			list1, list2 = kdtree1.getlists()
			np.savetxt(ground_p_str, np.array(list1))
			np.savetxt(surface_p_str, np.array(list2))
		time_results_pd = pd.DataFrame(time_results)
		time_results_pd.to_csv('speedtest/' + filename + 'resutls_KdTree.csv')
		print('File:' + filename + '\nDone!')
