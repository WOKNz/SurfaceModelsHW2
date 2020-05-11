from time import time
from pathlib import Path
import numpy as np
from pointcloud import pointcloud
from equalcells import eqlcells
from kdtree import kdtree
import pandas as pd
import os

if __name__ == '__main__':

	tests = [[1, 0.5, 15], [2, 0.75, 15], [3, 1.0, 15], [4, 1.5, 15], [5, 2, 65], [6, 3, 65], [7, 4, 65], [8, 5, 65]]
	paths = ['AD9_2.xyz', 'AD12_1.xyz', 'AD14_3.xyz', 'airborne1.pts', 'DU9_2.xyz']


	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz','ullmann_subset.xyz']

	def databaseType(db_type: int, points):
		"""
		Creates database from points according to id given and points
		:param points: ndarray, points xyz nx3
		:param db_type: 0 = pointcloud, 1 = equalcells, 2 = kdtree
		:return: Database object
		"""

		if db_type == 0:
			return pointcloud(points)
		elif db_type == 1:
			return eqlcells(points)
		elif db_type == 2:
			return kdtree(points, False, 10)


	for db_type in range(1, 3):

		# setting db type depended paths and params
		if db_type == 0:
			output_folder = './output/results_cloudpoints/'
		elif db_type == 1:
			output_folder = './output/results_equalcells/'
		elif db_type == 2:
			output_folder = './output/results_kdtree/'

		# creating folder for results
		if not os.path.exists(output_folder):
			os.makedirs(output_folder)
		if not os.path.exists(output_folder + 'speedtest/'):
			os.makedirs(output_folder + 'speedtest/')

		for path in paths:
			time_results = []
			filename = Path(path).stem
			full_path = 'Data/DataPoints/' + path
			temp_points = np.genfromtxt(full_path)
			db_object = databaseType(db_type, temp_points)
			for test in tests:
				ground_p_str = output_folder + filename + '_ground_' + str(test[0]) + '.xyz'
				surface_p_str = output_folder + filename + '_surface_' + str(test[0]) + '.xyz'

				start = time()
				db_object.filter(test[1], (test[2] * np.pi) / 180.0)
				finish = time()
				time_results.append([filename, test[0], finish - start])
				list1, list2 = db_object.getlists()
				np.savetxt(ground_p_str, np.array(list1))
				np.savetxt(surface_p_str, np.array(list2))
			time_results_pd = pd.DataFrame(time_results)
			time_results_pd.to_csv(output_folder + 'speedtest/' + filename + 'speed_results.csv')
