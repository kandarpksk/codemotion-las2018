import cv2, os, re, subprocess, sys

vidcap = cv2.VideoCapture('segment-eff/images/rJeP65u84ec_1_1080p.mp4')
success,image = vidcap.read()
count = 0 #

sample = [3240, 3600, 15000, 15120, 15480, 15600, 15720, 17040, 17520, 17640]
while success:
  success,image = vidcap.read()
  print '\rreading frame at', str(int((count/24)/60))+':'+str(round((count/24.)%60, 2)),
  
  if count in sample:
  	print
  	cv2.imwrite("./outputs/2_frame%d.ppm" % count, image)	# save frame as JPEG file
  	c = int(re.search(r'\d+', subprocess.check_output(["./segment-eff/code/segment 0.33 500 40000 outputs/2_frame"
  									+str(count)+".ppm outputs/2_frame"+str(count)], shell=True)).group())
  	print "processing...",
  	sys.stdout.flush() # show "incomplete" line output
  	for i in range(c):
  		command = "tesseract outputs/2_frame%d_segment%d.ppm outputs/2_frame%d_segment%d 2>/dev/null" % (count, i, count, i)
  		os.system(command)
  	print "got", c, "components\n"

  count += 1

# find outputs -empty | sed 's/^/rm /g'
# find outputs -empty | sed 's/.txt/.ppm/g' | sed 's/^/rm /g'

# find outputs -size -19c