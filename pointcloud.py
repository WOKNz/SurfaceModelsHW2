import numpy as np
from pathlib import Path
import pandas as pd

class pointcloud():
	def __init__(self, points):
		self.points = points.tolist()
		self.min_index = None
		self.ground_points = []
		self.surface_points = []

	def getGroundPointIndex(self):
		self.min_index = np.argmin(self.points[:,2])
		return self.min_index

	def filter(self, radius, angle):
		self.tan_angle_power2 = np.tan(angle)**2
		self.radius2 = radius**2

		def dist_power2(point_1, point_2):
			return (point_1[0]-point_2[0])**2+(point_1[1]-point_2[1])**2

		dist_2_np_matrix = np.zeros((self.points.shape[0],self.points.shape[0]))

		for row in range(0,self.points.shape[0]):
			for column in range(row,self.points.shape[0]):
				dist_2_np_matrix[row,column] = dist_power2()

		for i in range(0,len(self.points)):

			temp_list = []
			for j in range(0,len(self.points)):
				dist2 = dist_power2(self.points[i],self.points[j])
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

if __name__ == '__main__':
	# path = 'Data/DataPoints/AD9_2.xyz'
  # (X,Y,Z,R,G,B)
	# temp_points = np.array([[-1,-1,0],
	# 						[-1,1,0],
	# 						[1,-1,0],
	# 						[1,1,0],
	# 						[0,0,10]])

	import datetime

	tests = [[1,0.5,15],[2,0.75,15],[3,1.0,15],[4,1.5,15],[5,2,65],[6,3,65],[7,4,65],[8,5,65]]
	paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz','ullmann_subset.xyz']
	# paths = ['ullmann_subset.xyz']


	for path in paths:
		time_results = []
		filename = Path(path).stem
		full_path = 'Data/DataPoints/'+path
		for test in tests:
			ground_p_str = 'results/'+filename+'_ground_'+str(test[0])+'.xyz'
			surface_p_str = 'results/'+filename+'_surface_'+str(test[0])+'.xyz'
			temp_points = np.genfromtxt(full_path)
			pntc1 = pointcloud(temp_points)

			start = datetime.datetime.now()
			pntc1.filter(test[1], (test[2] * np.pi) / 180.0)
			finish = datetime.datetime.now()
			time_results.append([filename,test[0],finish-start])
			list1, list2 = pntc1.getlists()
			np.savetxt(ground_p_str, np.array(list1))
			np.savetxt(surface_p_str, np.array(list2))
		time_results_pd = pd.DataFrame(time_results)
		time_results_pd.to_csv(filename+'resutls_cloud.csv')