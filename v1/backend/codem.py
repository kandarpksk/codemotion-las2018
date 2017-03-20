import sys, cv2, math, numpy
import phase1, phase2_

if len(sys.argv) > 2:
	print 'skipping to frame', sys.argv[2]

if len(sys.argv) < 2:
	print 'err: need argument mentioning video number'
	sys.exit()
vnum = int(sys.argv[1])
fps = 30. if vnum == 1 else 24. #60 #list
video = cv2.VideoCapture('../public/videos/video'+str(vnum)+'.mp4')

fnum = 0
# if len(sys.argv) == 3:
# 	duration = 7980
# 	fnum = int(sys.argv[2])-1
# 	video.set(2, fnum /(duration*fps));
success, image = video.read()
prev = numpy.zeros(image.shape, numpy.uint8)
while success:
	fnum += 1
	t_min = int((fnum/fps)/60)
	t_sec = int(math.floor((fnum/fps)%60)) #check

	if fnum%fps == 1 and (len(sys.argv) < 3 or fnum >= int(sys.argv[2])): # process one frame each second
		diff = cv2.subtract(image, prev)
		imgray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
		ndiff = cv2.countNonZero(imgray)

		print '\r%d:%02d processing... ' % (t_min, t_sec), # (<ndiff> differences)
		sys.stdout.flush()
		path = '../public/extracts/video'+str(vnum)
		print '\r%d:%02d finding segments... ' % (t_min, t_sec),
		sys.stdout.flush()
		segments = phase1.process(image, path+'/'+'frame'+str(fnum)+'-segment')
		print '\r%d:%02d extracting text... ' % (t_min, t_sec),
		sys.stdout.flush()
		phase2_.process(fnum, segments, path)

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
