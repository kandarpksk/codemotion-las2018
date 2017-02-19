debug = False

# input = 'preview/resources5/frame16412.jpg'
# output = 'houghlines1.jpg'
# input = 'preview/resources2/frame3505.jpg'
# output = 'houghlines2.jpg'
input = 'preview/resources2/frame30817.jpg'
output = 'houghlines3.jpg'
fraction = 1./10 # distance (as fraction of smaller dimension) to cluster within

import cv2
import numpy as np
from auxiliary import *

img = cv2.imread(input)
demo = img if debug else np.zeros(img.shape, np.uint8)
if debug: demo += 255
radius = min(img.shape[0], img.shape[1])*fraction
corners = [(0,0), (0,img.shape[0]), (img.shape[1],0), (img.shape[1],img.shape[0])]

# step: detect lines in frame [o/p: lines] | third parameter (of canny) 150
#############################
edges = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 50, 20, apertureSize = 3)
minLineLength, maxLineGap = 100, 10
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)

def drawPoint((x,y), color=white, thickness=4, image=demo):
	cv2.circle(image, (x,y), thickness, color, -1, 8)
	# cv2.circle(image, (x,y), radius, color, 0, 8) # "locator"

# step: find (end points of) less tilted horizontal or vertical lines [o/p: points]
##############################################
points = []
def smallSlope(p1, p2, axis, theta=15): # tilted less than theta
	if axis == 'x':
		p1 = (p1[1], p1[0])
		p2 = (p2[1], p2[0])
	return p1[1]-p2[1] and abs(float(p1[0])-p2[0])/abs(p1[1]-p2[1]) < np.sin(theta*np.pi/180)
for x1,y1,x2,y2 in lines[0]:
	# later: slightly more relaxed angle acceptable?
	along_y = abs(y1-y2) > 0.2*img.shape[0] and smallSlope((x1,y1), (x2,y2), 'y', 11)
	along_x = abs(x1-x2) > 0.2*img.shape[1] and smallSlope((x1,y1), (x2,y2), 'x')
	if along_x or along_y:
		points.extend([(x1,y1), (x2,y2)])
		# cv2.line(demo, (x1,y1), (x2,y2), white, 5) # draw an outline for clarity
		if debug:
			cv2.line(demo, (x1,y1), (x2,y2), randomColor(), 2)
# also include corners of entire image
# for p in corners:
	# drawPoint(p, white, 5)
# points.extend(corners) # todo | useful?

# step: heuristic clustering of points [o/p: clusters]
############################
def put(p, g):
	global radius
	if g != []:
		added = False
		index = -1
		for c in g: # cluster, group
			index += 1
			for point in c:
				if d2(p, point) < radius**2:
					g[index].append(p)
					added = True
					break
			if added:
				break
		if not added:
			g.append([p])
	else:
		g.append([p])
clusters = []
for p in points:
	put(p, clusters)

# step: choose representative point of cluster [o/p: ends]
##############################################
ends = []
def closestCorner(p):
	return minima([(corner, d2(p, corner)) for corner in corners])[0]
# later: handle ambiguous case
for c in clusters:
	color = randomColor()
	closestCorners = []
	rep = ()
	for p in c:
		# drawPoint(p, color)
		co = closestCorner(p)
		if co[0] not in closestCorners:
			closestCorners.append(co[0])
			rep = (p, co[1])
		elif co[1] > rep[1]:
			rep = (p, co[1])
	if len(closestCorners) != 1:
		print 'unhandled case: multiple corners close to cluster'
	corner = closestCorners[0]
	ends.append(rep[0])
	if debug or True: # temporary
		drawPoint(rep[0], white, 7)

# convex hull :|
def showPolygon(poly):
	for i in range(len(poly)):
		p1 = (poly[i-1][0][0],poly[i-1][0][1])
		p2 = (poly[i][0][0],poly[i][0][1])
		cv2.line(demo, p1, p2, randomColor(), 5)
		print p2
if debug:
	hull = cv2.convexHull(np.array(ends))
	showPolygon(hull)

# idea: lines between clusters
import random
edges = []
for e1 in ends:
	along_x = [(e1, e2) for e2 in ends if smallSlope(e1, e2, 'x', 5)]
	along_y = [(e1, e2) for e2 in ends if smallSlope(e2, e1, 'y', 4)]
	pairs = along_x + along_y # todo: choose only least tilted ones
	if len(pairs) > 1:
		edges.append(pairs)
	else:
		drawPoint(e1, (0,0,0), 7)
for pairs in edges:
	print pairs[0][0], '...',
	for pair in pairs:
		print pair[1],
	print

'''
if len(pairs) > 1: # todo: review
	print e1, '...',
	for pair in pairs:
		print pair[1],
	print '\n'
	color = randomColor()
	for pair in pairs:
		cv2.line(demo, pair[0], pair[1], color, 3+random.randrange(3))
'''

cv2.imwrite(output, demo)
