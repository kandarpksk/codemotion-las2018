import sys, cv2, math, numpy
import phase1, phase2

if len(sys.argv) < 2:
	print 'err: need argument mentioning video number'
	sys.exit()
vnum = int(sys.argv[1])
fps = 30. if vnum == 1 else 24 #60 #list
video = cv2.VideoCapture('../public/videos/video'+str(vnum)+'.mp4')

fnum = 0
success, image = video.read()
prev = numpy.zeros(image.shape, numpy.uint8)
while success:
	fnum += 1
	t_min = int((fnum/fps)/60)
	t_sec = int(math.floor((fnum/fps)%60)) #check

	if fnum%fps == 1: # process one frame each second
		diff = cv2.subtract(image, prev)
		imgray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
		ndiff = cv2.countNonZero(imgray)

		print '\rprocessing %d:%02d now' % (t_min, t_sec), # (<ndiff> differences)
		sys.stdout.flush()
		path = '../public/extracts/video'+str(vnum)

		segments = phase1.process(image, path+'/'+'frame'+str(fnum)+'-segment')

		phase2.process(fnum, segments, path)

		if ndiff > 7500: # show significant changes #improve
			marked = image.copy()
			ret, thresh = cv2.threshold(imgray, 60, 255, 0)
			contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			cv2.drawContours(marked, contours, -1, (0,255,0), 1)
			cv2.imwrite(path+'/diffs/'+'frame'+str(fnum)+'.jpg', marked)

		prev = image
		# end of if stmt

	success, image = video.read()
	# end of while loop #todo

print '\ndone'
