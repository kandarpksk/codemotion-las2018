video_file_path = 'segment/images/rJeP65u84ec_1_1080p.mp4'
TAB = "   " # macros?

fps, debug, times = 24, False, [135, 150, 625, 630, 645, 650, 655, 710, 730, 735]

import cv2, os, re, subprocess, sys
import HTMLParser, operator, codecs
parser = HTMLParser.HTMLParser()

vidcap = cv2.VideoCapture(video_file_path)
success,image = vidcap.read()
count = -1
while success:
	count += 1
	success,image = vidcap.read()
	minute = int((count/fps)/60)
	second = int(round((count/float(fps))%60))
	print '\rprocessing frame #'+str(count)+' at', '%d:%02d' % (minute, second),
	
	if count/24 in times or (count % 24 == 0 and not debug): # first frame each second
		# extract image frame
		cv2.imwrite("./outputs/2_frame%d.ppm" % count, image)
		
		# get segment images
		arguments = "0.33 500 40000 outputs/2_frame" + str(count) + ".ppm" + " outputs/2_frame" + str(count)
		seg_cmd = "./segment/code/segment " + arguments
		c = int(re.search(r'\d+', subprocess.check_output([seg_cmd], shell=True)).group())
		
		print "\ncrunching...",
		sys.stdout.flush() # show incomplete line
		
		# run ocr and fix spacing
		for i in range(c):
			image = "outputs/2_frame%d_segment%d.ppm " % (count, i)
			output = "outputs/2_frame%d_segment%d" % (count, i)
			ocr_command = "tesseract " + image+output + " config.txt hocr 2>/dev/null"
			os.system(ocr_command)

			# hocr output conversion
			res = [] # distance, code
			with open("outputs/2_frame%d_segment%d.hocr" % (count, i)) as hocr_output:
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
				os.system("rm outputs/2_frame%d_segment%d.*" % (count, i))
				if i == c-1:
					if subprocess.call("ls outputs/2_frame%d_segment*.ppm 1>/dev/null 2>/dev/null" % count, shell=True) != 0:
						os.system("mv outputs/2_frame%d.ppm outputs/2_frame%d_del.ppm" % (count, count))

			else:
				os.system("rm outputs/2_frame%d_segment%d.hocr" % (count, i))
				base = min(res, key=operator.itemgetter(0))[0]

				# yet to address case when 30,33,62 happens
				temp = [r for r in res if r[0] > base*1.09] # base = 0 case
				if len(temp) == 0:
					lines = ""
					for r in res:
						lines += r[1] + "\n"

					f = codecs.open("outputs/2_frame%d_segment%d_dis.txt" % (count, i), 'w', 'utf-8')
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

					f = codecs.open("outputs/2_frame%d_segment%d_ind.txt" % (count, i), 'w', 'utf-8')
					f.write(indented_lines)

		print "done\n"

# find outputs -empty | sed 's/^/rm /g'
# find outputs -empty | sed 's/.txt/.ppm/g' | sed 's/^/rm /g'

# find outputs -size -3c -delete
