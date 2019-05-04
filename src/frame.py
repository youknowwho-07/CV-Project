import numpy as np 
import cv2
from helpers import *
from matplotlib import pyplot as plt
from skimage.measure import ransac
from skimage.transform import FundamentalMatrixTransform

class Frame(object):
	"""docstring for Frame"""
	def __init__(self, frame):
		super(Frame, self).__init__()
		self.image = frame
		(self.X, self.Y, self.Z) = frame.shape
		self.KeyPts = None
		self.des = None

def getFeatures(frame):
	orb = cv2.ORB_create()

	frame_gray = cv2.cvtColor(frame.image, cv2.COLOR_BGR2GRAY)
	corners = cv2.goodFeaturesToTrack(frame_gray,maxCorners=1000,qualityLevel=0.01,minDistance=10)

	KeyPts = []
	for i in corners:
		u,v = i.ravel()
		KeyPts.append(cv2.KeyPoint(u,v, _size=20))
	
	frame.KeyPts, frame.des = orb.compute(frame.image, KeyPts)

	# frame.KeyPts = [kp.pt for kp in KeyPts]
	# frame.des = des
	return

def matchFeatures(F1, F2):
	bf = cv2.BFMatcher(cv2.NORM_HAMMING)
	
	matches = bf.knnMatch(F1.des,F2.des, k=2)

	temp_matches = []
	for m,n in matches:
		if m.distance < 0.75*n.distance and m.distance < 32:
			temp_matches.append(m)


	pt1 = []
	pt2 = []
	good_matches = []
	# o=0
	for m in temp_matches:
		if m.queryIdx not in pt1 and m.trainIdx not in pt2:
			pt1.append(m.queryIdx)
			pt2.append(m.trainIdx)
			good_matches.append([F1.KeyPts[m.queryIdx].pt,F2.KeyPts[m.trainIdx].pt])
			# print('o  ', o)
			# o = o+1

	# print len(good_matches), len(matches), len(idx1), len(idx2)
	assert(len(good_matches) >= 8)

	pt1 = np.array(pt1)
	pt2 = np.array(pt2)

	good_matches = np.array(good_matches)


	new_good_match = transform_coordinates(good_matches)
	print(good_matches[1,1].shape, 'good points')
	print(new_good_match[1,0], 'aa')
	print(good_matches[1, 0], 'bb')

	model, inliers = ransac((new_good_match[:, 0], new_good_match[:, 1]),
                          	FundamentalMatrixTransform,
                          	min_samples=8,
                          	residual_threshold=0.02,
							max_trials=100)

	print(model.params)
	# a, b, c = np.linalg.svd(model.params) 
	# print(b)
	return pt1[inliers], pt2[inliers], good_matches[inliers], len(good_matches)#, Similarity(model)#, fundamentalToRt(model.params)

	# matches = sorted(matches, key = lambda x:x.distance)
	# img3 = F1.image

	# for m,n in matches:
	# 	print i, m.distance, n.distance
	# 	i = i + 1

	# cv2.drawMatches(F1.image,F1.KeyPts,F2.image,F2.KeyPts,matches[:10], outImg=img3, flags=2)
	# plt.imshow(img3),plt.show()
	# cv2.waitKey(0)
	return