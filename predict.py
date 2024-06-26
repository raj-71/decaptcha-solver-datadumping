# DO NOT CHANGE THE NAME OF THIS METHOD OR ITS INPUT OUTPUT BEHAVIOR
# INPUT CONVENTION
# filenames: a list of strings containing filenames of images

# OUTPUT CONVENTION
# The method must return a list of strings. Make sure that the length of the list is the same as
# the number of filenames that were given. The evaluation code may give unexpected results if
# this convention is not followed.

import pickle
import cv2
import numpy as np

def decaptcha( filenames ):
	loaded_model = pickle.load(open('model.sav', 'rb'))
	d = {0 : 'ALPHA',1: 'BETA',2: 'CHI',3: 'DELTA',4: 'EPSILON',5: 'ETA',6: 'GAMMA',7: 'IOTA',8: 'KAPPA',9: 'LAMDA',10: 'MU',11: 'NU',12: 'OMEGA',13: 'OMICRON',14: 'PHI',
 15: 'PI',16: 'PSI',17: 'RHO',18: 'SIGMA',19: 'TAU',20: 'THETA',21: 'UPSILON',22: 'XI',23: 'ZETA'}
	dfX = []
	dfy = []

	for i in filenames:
		img = cv2.imread(i)
        # get shape of the image
		y_dim, x_dim = img.shape[:2]
        
        # Find corner pixel with max freq     
		corners = np.array([img[0,0] ,img[0,-1] ,img[-1,0] ,img[-1,-1] ])
		unique, counts = np.unique(corners, axis = 0,  return_counts = True)
		backgnd = unique[np.argmax(counts)]

        # change the background to white
		background = np.where((img[:,:,0]==backgnd[0]) & (img[:,:,1]==backgnd[1]) & (img[:,:,2]==backgnd[2]))
		img[background] = np.array([255,255,255], dtype = np.uint8)

        # Now Dilate the image 
		kernel = np.ones((5, 5), np.uint8)
		img_dilation = cv2.dilate(img, kernel, iterations=1)

        # convert image to grayscale
		gray = cv2.cvtColor(img_dilation, cv2.COLOR_BGR2GRAY)

        # Segment image into 3 characters 
        # Get the cordinates of the bounding box of each character
		start = True
		countPrev = 0
		boundingList = []
		for i in range(500):
			vertgrayfreq = np.sum(gray[:,i] < 250)
			if vertgrayfreq > 12:
				if start:
				    # print(i)
					startindex = i
					start = False
				countPrev += 1
			if vertgrayfreq == 0:
				if start == False:
				# print(i)
					if countPrev > 30:
						sizediff = i-startindex
						if (sizediff < 150):
							x_temp = startindex - int((150 - sizediff)/2)
							x = x_temp if x_temp > 0 else 0
							x = x if x + 150 < 500 else 350
							y = 0
						else:
							x = i
							y = 0
						boundingList.append((x , y, 150, 150))
						countPrev = 0
					start = True    
		listSize = len(boundingList)
		if listSize != 3 :
			boundingList = [(15 , 0 , 150, 150),(175, 0, 150, 150),(335, 0, 150, 150)]
		
        # Got the segment of the image + compressed it into 30x30 pixel image
        # And then flatten the image in 1D array 
        # Then append it into dataframeX (dfX)
		for boxIndex in range(3):
			x, y = boundingList[boxIndex][0], boundingList[boxIndex][1]
			finalImage = gray[y:y + 150, x:x + 150]
			finalImage = cv2.resize(finalImage, (30, 30))
			finalImage = finalImage.flatten()
			dfX.append(finalImage)

    # Load the model 
	y_pred = loaded_model.predict(dfX)

    # combine three predicted character for each image
	finalpred = []
	for eachpred in range(0,len(y_pred),3):
		s = ""
		s = s + d[y_pred[eachpred]] + ','
		s = s + d[y_pred[eachpred+1]] + ','
		s = s + d[y_pred[eachpred+2]] 
		finalpred.append(s)
	
	return finalpred