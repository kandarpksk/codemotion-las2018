import sys, cv2, math, numpy

if len(sys.argv) < 2:
	print 'err: need argument mentioning video number'
	sys.exit()
vnum = int(sys.argv[1])
fps = 30. if vnum == 1 else 60 #list
video = cv2.VideoCapture('../public/videos/video'+str(vnum)+'.mp4')

fnum = 0
success, image = video.read()
prev = numpy.zeros(image.shape, numpy.uint8)
ignoring = False
while success:
	fnum += 1
	t_min = int((fnum/fps)/60)
	t_sec = int(math.floor((fnum/fps)%60)) #check

	if fnum%fps == 1:
		diff = cv2.subtract(image, prev)
		imgray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

		ndiff = cv2.countNonZero(imgray)
		if ndiff < 1:
			if not ignoring: print
			ignoring = True
			print '\rignoring %d:%02d' % (t_min, t_sec),
		else:
			if ignoring: print
			ignoring = False
			marked = image.copy()
			ret, thresh = cv2.threshold(imgray, 60, 255, 0)
			contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			cv2.drawContours(marked, contours, -1, (0,255,0), 1)

			print '\rprocessing %d:%02d now (%d differences)' % (t_min, t_sec, ndiff),
			sys.stdout.flush()
			path = '../public/extracts/video'+str(vnum)
			name = str(fnum)+('ignore' if ndiff < 7500 else 'frame')+'.jpg'
			cv2.imwrite(path+'/'+name, marked)

			prev = image
			# end of else stmt
		# end of if stmt

	success, image = video.read()
	# end of while loop #todo

print '\ndone'
