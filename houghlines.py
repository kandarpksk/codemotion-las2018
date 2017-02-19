debug = False

import sys
input = sys.argv[1]
output = sys.argv[2]
fraction = 1./10 # distance (as fraction of smaller dimension) to cluster within

import cv2
import numpy as np
from auxiliary import *

img = cv2.imread(input)
demo = img.copy() if True else np.zeros(img.shape, np.uint8) # not a copy?
if debug: demo += 255
radius = min(img.shape[0], img.shape[1])*fraction
corners = [(0,0), (0,img.shape[0]), (img.shape[1],0), (img.shape[1],img.shape[0])]

# step: detect lines in frame [o/p: lines] | third parameter (of canny) 150
#############################
edgy = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 50, 20, apertureSize = 3)
minLineLength, maxLineGap = 100, 10
lines = cv2.HoughLinesP(edgy, 1, np.pi/180, 100, minLineLength, maxLineGap)
print 'lines'
for line in lines[0]:
	print line,
print

def drawPoint((x,y), color=white, thickness=4, image=demo):
	cv2.circle(image, (x,y), thickness, color, -1, 8)
	# cv2.circle(image, (x,y), radius, color, 0, 8) # "locator"

# step: find (end points of) less tilted horizontal or vertical lines [o/p: points]
##############################################
points = []
def slope(p1, p2, axis='x'):
	if axis == 'x':
		return (p1[1]-p2[1])/(float(p1[0])-p2[0])
	else:
		return (p1[0]-p2[0])/(float(p1[1])-p2[1])
def smallSlope(p1, p2, axis, theta=15): # tilted less than theta
	not_perpendicular = (p1[0]-p2[0] if axis == 'x' else p1[1]-p2[1])
	return not_perpendicular and abs(slope(p1, p2, axis)) < np.sin(theta*np.pi/180)
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
print 'points'
print points

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

# convex hull (ignore)
def showPolygon(poly, debug=False):
	for i in range(len(poly)):
		p1 = (poly[i-1][0][0],poly[i-1][0][1])
		p2 = (poly[i][0][0],poly[i][0][1])
		if not debug:
			cv2.line(demo, p1, p2, randomColor(), 5)
		print p2,
	print
if debug:
	hull = cv2.convexHull(np.array(ends))
	showPolygon(hull)

# idea: lines between clusters

import random
edges, ignoreList = [], []
crop = []
for e1 in ends:
	along_x = [((e1, e2), round(abs(slope(e1, e2)), 2)) for e2 in ends if smallSlope(e1, e2, 'x', 5)]
	if len(along_x) > 1:
		along_x = [minima(along_x)[0]]
		# how about longer lines??
	along_y = [((e1, e2), round(abs(slope(e1, e2, 'y')), 2)) for e2 in ends if smallSlope(e1, e2, 'y', 4)]
	if len(along_y) > 1:
		along_y = [minima(along_y)[0]]
	pairs = [p[0] for p in along_x] + [p[0] for p in along_y] # todo: choose only least tilted ones
	if len(pairs) > 1 or along_y: # todo: review | don't ignore separators!
		edges.append(pairs)
	else:
		ignoreList.append(e1)
		if debug:
			print 'ignored point:', e1
		drawPoint(e1, (50,50,50), 7)
for pairs in edges:
	# print pairs[0][0], '...',
	offset = 0
	for i in range(len(pairs)):
		if pairs[i-offset][1] in ignoreList:
			del pairs[i-offset]
			offset += 1
			continue
		# print pairs[i-offset][1],
	# print
	color, t, count = randomColor(), random.randrange(3), 0
	for pair in pairs:
		ignored = True
		for pairs in edges:
			if (pair[1], pair[0]) in pairs:
				if debug:
					cv2.line(demo, pair[0], pair[1], color, 3+t)
				if count == 0:
					crop.append(pair[0])
					print pair[0], '...'
				print '\t', pair[1]
				count += 1
				ignored = False
		# if ignored:
			# print '\t', pair[1], 'ignored'
	if count == 0:
		if debug:
			print 'ignored point:', pairs[0][0]
		drawPoint(pairs[0][0], (50,50,50), 7)

if len(crop) < 3:
	crop.extend(corners)
	for p in corners:
		drawPoint(p, white, 20)

from surrounding_box import *
hull = cv2.convexHull(np.array(crop))
print '\npolygon ...', '\n\t',
showPolygon(hull, 'debug')
lx_ly = (hull[0][0][0], hull[0][0][1])
lx_hy, hx_ly, hx_hy = lx_ly, lx_ly, lx_ly
for p in hull:
	p = p[0] # issues??
	if p[0] < lx_ly[0]:
		lx_ly = (p[0], lx_ly[1])
		lx_hy = (p[0], lx_hy[1])
	if p[1] < lx_ly[1]:
		lx_ly = (lx_ly[0], p[1])
		hx_ly = (hx_ly[0], p[1])
	if p[0] > hx_hy[0]:
		hx_hy = (p[0], hx_hy[1])
		hx_ly = (p[0], hx_ly[1])
	if p[1] > hx_hy[1]:
		hx_hy = (hx_hy[0], p[1])
		lx_hy = (lx_hy[0], p[1])
print '\nrectange ...', '\n\t',
def show(poly, debug=False):
	c = randomColor()
	for i in range(len(poly)):
		p1 = (poly[i-1][0][0],poly[i-1][0][1])
		p2 = (poly[i][0][0],poly[i][0][1])
		if not debug:
			cv2.line(demo, p1, p2, c, 10)
		print p2,
	print
show([[lx_ly], [lx_hy], [hx_hy], [hx_ly]])
demo = img[lx_ly[1]:hx_hy[1], lx_ly[0]:hx_hy[0]]

# print minimum_bounding_rectangle(crop)
# .astype(int)

def addBorder(image, frac=0.02, type=cv2.BORDER_CONSTANT):
	top = (int) (frac*demo.shape[0])
	bottom = top
	left = (int) (frac*demo.shape[1])
	right = left
	return cv2.copyMakeBorder(image, top, bottom, left, right, type);
demo = addBorder(demo)

def scale(image, multiplier):
	# INTER_NEAREST
	return cv2.resize(image, None, fx=multiplier, fy=multiplier)
demo = scale(demo, 2)

import remove_border as rb
# print rb.crop_border(demo)

cv2.imwrite(output, demo)
print
