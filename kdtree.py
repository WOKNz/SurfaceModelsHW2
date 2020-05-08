#!python numbers=disable

# Copyleft 2008 Sturla Molden
# University of Oslo

# import psyco
# psyco.full()

import numpy as np


class kdtree():
	def __init__(self, data, leafsize=10):
		"""
		build a kd-tree for O(n log n) nearest neighbour search

		input:
			data:       2D ndarray, shape =(ndim,ndata), preferentially C order
			leafsize:   max. number of data points to leave in a leaf

		output:
			kd-tree:    list of tuples
		"""

		ndim = data.shape[0]
		ndata = data.shape[1]

		# find bounding hyper-rectangle
		hrect = np.zeros((2, data.shape[0]))
		hrect[0, :] = data.min(axis=1)
		hrect[1, :] = data.max(axis=1)

		# create root of kd-tree
		idx = np.argsort(data[0, :], kind='mergesort')
		data[:, :] = data[:, idx]
		splitval = data[0, int(ndata / 2)]

		left_hrect = hrect.copy()
		right_hrect = hrect.copy()
		left_hrect[1, 0] = splitval
		right_hrect[0, 0] = splitval

		self.tree = [(None, None, left_hrect, right_hrect, None, None)]

		stack = [(data[:, :int(ndata / 2)], idx[:int(ndata / 2)], 1, 0, True),
		         (data[:, int(ndata / 2):], idx[int(ndata / 2):], 1, 0, False)]

		# recursively split data in halves using hyper-rectangles:
		while stack:

			# pop data off stack
			data, didx, depth, parent, leftbranch = stack.pop()
			ndata = data.shape[1]
			nodeptr = len(self.tree)

			# update parent node

			_didx, _data, _left_hrect, _right_hrect, left, right = self.tree[parent]

			self.tree[parent] = (_didx, _data, _left_hrect, _right_hrect, nodeptr, right) if leftbranch \
				else (_didx, _data, _left_hrect, _right_hrect, left, nodeptr)

			# insert node in kd-tree

			# leaf node?
			if ndata <= leafsize:
				_didx = didx.copy()
				_data = data.copy()
				leaf = (_didx, _data, None, None, 0, 0)
				self.tree.append(leaf)

			# not a leaf, split the data in two
			else:
				splitdim = depth % ndim
				idx = np.argsort(data[splitdim, :], kind='mergesort')
				data[:, :] = data[:, idx]
				didx = didx[idx]
				nodeptr = len(self.tree)
				stack.append((data[:, :int(ndata / 2)], didx[:int(ndata / 2)], depth + 1, nodeptr, True))
				stack.append((data[:, int(ndata / 2):], didx[int(ndata / 2):], depth + 1, nodeptr, False))
				splitval = data[splitdim, int(ndata / 2)]
				if leftbranch:
					left_hrect = _left_hrect.copy()
					right_hrect = _left_hrect.copy()
				else:
					left_hrect = _right_hrect.copy()
					right_hrect = _right_hrect.copy()
				left_hrect[1, splitdim] = splitval
				right_hrect[0, splitdim] = splitval
				# append node to tree
				self.tree.append((None, None, left_hrect, right_hrect, None, None))


	# !python numbers=disable

	def intersect(self, hrect, r2, centroid):
		"""
		checks if the hyperrectangle hrect intersects with the
		hypersphere defined by centroid and r2
		"""
		maxval = hrect[1, :]
		minval = hrect[0, :]
		p = centroid.copy()
		idx = p < minval
		p[idx] = minval[idx]
		idx = p > maxval
		p[idx] = maxval[idx]
		return ((p - centroid) ** 2).sum() < r2

	def pointsInRadius(self, datapoint, radius):
		""" find all points within radius of datapoint """
		stack = [self.tree[0]]
		inside = []
		while stack:

			leaf_idx, leaf_data, left_hrect, \
			right_hrect, left, right = stack.pop()

			# leaf
			if leaf_idx is not None:
				param = leaf_data.shape[0]
				distance = np.sqrt(((leaf_data - datapoint.reshape((param, 1))) ** 2).sum(axis=0))
				near = np.where(distance <= radius)
				if len(near[0]):
					idx = leaf_idx[near]
					distance = distance[near]
					inside += (zip(distance, idx))

			else:

				if self.intersect(left_hrect, radius, datapoint):
					stack.append(self.tree[left])

				if self.intersect(right_hrect, radius, datapoint):
					stack.append(self.tree[right])

		return inside

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

	# tests = [[0.5,0.5,15],[2,0.75,15],[3,1.0,15],[4,1.5,15],[5,2,65],[6,3,65],[7,4,65],[8,5,65]]
	tests = [[1, 2, 15]]
	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz']
	# paths = ['AD9_2.xyz','AD12_1.xyz','AD14_3.xyz','airborne1.pts','DU9_2.xyz','ullmann_subset.xyz']
	paths = ['AD9_2.xyz']
	# paths = ['ullmann_subset.xyz']

	for path in paths:
		time_results = []
		filename = Path(path).stem
		full_path = 'Data/DataPoints/' + path
		for test in tests:
			ground_p_str = 'results3/' + filename + '_ground_' + str(test[0]) + '.xyz'
			surface_p_str = 'results3/' + filename + '_surface_' + str(test[0]) + '.xyz'
			temp_points = np.genfromtxt(full_path)

			kdtree1 = kdtree(temp_points.T)
			points_in_radius = kdtree1.pointsInRadius(np.array([[173221.697],[433859.048],[7.043]]),2)

			start = datetime.datetime.now()
			kdtree1.filter(test[1], (test[2] * np.pi) / 180.0)
			finish = datetime.datetime.now()
			time_results.append([filename, test[0], finish - start])
			list1, list2 = kdtree1.getlists()
			np.savetxt(ground_p_str, np.array(list1))
			np.savetxt(surface_p_str, np.array(list2))
		time_results_pd = pd.DataFrame(time_results)
		time_results_pd.to_csv(filename + 'resutls_equallcells.csv')
		print('File:'+filename+'\nDone!')
