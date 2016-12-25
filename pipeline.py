import cv2, sys

vidcap = cv2.VideoCapture('segment-eff/images/rJeP65u84ec_720p.mp4')
success,image = vidcap.read()
count = 0 #

sample = [3240, 3600, 15000, 15120, 15480, 15600, 15720, 17040, 17520, 17640]
while success:
  success,image = vidcap.read()
  print '\rLast read frame at', str(int((count/24)/60))+':'+str(round((count/24.)%60, 2)),
  
  if count in sample:
  	cv2.imwrite("frame%d.ppm" % count, image)	# save frame as JPEG file

  count += 1