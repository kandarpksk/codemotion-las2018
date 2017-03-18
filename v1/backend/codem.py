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
		if numpy.array_equal(image, prev):
			if not ignoring: print
			print '\rignoring %d:%02d' % (t_min, t_sec),
			ignoring = True
		else:
			ignoring = False
			diff = cv2.subtract(prev, image)
			marked = image.copy()
			imgray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
			ret, thresh = cv2.threshold(imgray, 60, 255, 0)
			contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			cv2.drawContours(marked, contours, -1, (0,255,0), 1)

			print '\rprocessing %d:%02d now' % (t_min, t_sec),
			sys.stdout.flush()
			cv2.imwrite('../public/extracts/video'+str(vnum)+'/frame'+str(fnum)+'.jpg', marked)

			prev = image
			# end of else stmt
		# end of if stmt

	success, image = video.read()
	# end of while loop #todo

print '\ndone'
