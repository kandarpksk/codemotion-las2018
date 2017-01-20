video_file_path = "segment/images/5aP9Bl9hcqI_2_1080.mp4"
op = "preview/resources" # 62481
TAB = "   " # macros?

fps, debug, times = 23.976150, False, [2724.] #[135, 150, 625, 630, 645, 650, 655, 710, 730, 735]

import cv, cv2, os, re, subprocess, sys
import HTMLParser, operator, codecs
parser = HTMLParser.HTMLParser()

time = 43*60+26
vidcap = cv2.VideoCapture(video_file_path)
# print vidcap.get(cv.CV_CAP_PROP_FPS)
vidcap.set(1, 65352) # int(time*fps)
success,image = vidcap.read()
count = 65352-1 # 120
if success:
	count += 1
	# success,image = vidcap.read()
	minute = int((count/fps)/60)
	second = int(round((count/float(fps))%60))
	print '\rframe #'+str(count)+' at', '%d:%02d' % (minute, second),
	
	if count/24. in times or (count % 24 == 0 or not debug): # first frame each second # fix
		os.system("rm "+op+"/v2_frame%d* 2>/dev/null" % count);

		# extract image frame
		cv2.imwrite(op+"/v2_frame%d.ppm" % count, image)
		cv2.imwrite(op+"/v2_frame%d.jpg" % count, image)
		
		# get segment images
		arguments = "0.33 500 40000 "+op+"/v2_frame" + str(count) + ".ppm" + " "+op+"/v2_frame" + str(count)
		seg_cmd = "./segment/code/segment " + arguments
		c = int(re.search(r'\d+', subprocess.check_output([seg_cmd], shell=True)).group())
		
		print "\ncrunching...",
		sys.stdout.flush() # show incomplete line
		
		# run ocr and fix spacing
		for i in range(c):
			image = op+"/v2_frame%d_segment%d.ppm " % (count, i)
			output = op+"/v2_frame%d_segment%d" % (count, i)
			ocr_command = "tesseract " + image+output + " ~/large/codemotion/git/config.txt 2>/dev/null"
			os.system(ocr_command)

			# hocr output conversion
			res = [] # distance, code
			with open(op+"/v2_frame%d_segment%d.hocr" % (count, i)) as hocr_output:
				for line in hocr_output:
					# find x-coordinate of upper left corner
					location = re.search(r'(?<=bbox ).+?(?=\s)', line)
					
					# ignore tags and extract code
					text = re.sub(r'<[^>]*>', '', line)
					# fix special characters
					text = text.strip().decode("utf8")
					# dumb down smark quotes
					text = text.replace(u'\u201c', '"').replace(u'\u201d', '"')
					# decode HTML-safe sequences
					text = parser.unescape(text)
					
					# sanity check for location and extract
					is_text_empty = (text == re.search(r'\w*', line).group(0))
					if location != None and not is_text_empty:
						res.append([int(location.group(0)), text])

			# spacing adjustment

			if len(res) == 0:
				os.system("rm "+op+"/v2_frame%d_segment%d.*" % (count, i))
				if i == c-1:
					if subprocess.call("ls "+op+"/v2_frame%d_segment*.ppm 1>/dev/null 2>/dev/null" % count, shell=True) != 0:
						os.system("echo 0 > "+op+"/v2_frame"+str(count)+".txt")
						# os.system("mv "+op+"/v2_frame%d.ppm "+op+"/v2_frame%d_del.ppm" % (count, count))

			else:
				cv2.imwrite(op+"/v2_frame%d_segment%d.jpg" % (count, i), cv2.imread(op+"/v2_frame%d_segment%d.ppm" % (count, i)))

				os.system("rm "+op+"/v2_frame%d_segment%d.hocr" % (count, i))
				base = min(res, key=operator.itemgetter(0))[0]

				# yet to address case when 30,33,62 happens
				temp = [r for r in res if r[0] > base*1.09] # when base = 0
				if len(temp) == 0:
					lines = ""
					for r in res:
						lines += r[1] + "\n"

					# _dis[placed]
					f = codecs.open(op+"/v2_frame%d_segment%d.txt" % (count, i), 'w', 'utf-8') # _check.txt
					f.write(lines)

				else:
					tab = min(temp, key=operator.itemgetter(0))[0]-base

					res = [[int(round((r[0]-float(base))/tab)), r[1]] for r in res]
					indented_lines = ""
					for r in res:
						indented = ""
						for x in range(r[0]):
							indented += TAB
						indented += r[1]
						indented_lines += indented + "\n"

					# _ind[ented]
					f = codecs.open(op+"/v2_frame%d_segment%d.txt" % (count, i), 'w', 'utf-8')
					f.write(indented_lines)

		write_max_segments = "echo "+str(i)+" > "+op+"/v2_frame"+str(count)+".txt"
		os.system("rm "+op+"/*.ppm; if [ ! -f "+op+"/v2_frame"+str(count)+".txt ]; then "+write_max_segments+"; fi")
		print "done\n"

# find outputs -empty | sed 's/^/rm /g'
# find outputs -empty | sed 's/.txt/.ppm/g' | sed 's/^/rm /g'

# find outputs -size -3c -delete
