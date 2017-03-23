def process(frame, s, path):
	for i in range(1, s+1):
		import os, re, cv2, operator, codecs
		import HTMLParser
		from unidecode import unidecode
		parser = HTMLParser.HTMLParser()
		unit_indent = "   "

		image = path+"/frame%d-segment%d.jpg" % (frame, i)
		output = path+"/frame%d-segment%d" % (frame, i)
		ocr_command = "tesseract " + image+' '+output + " config.txt 2>/dev/null"
		os.system(ocr_command)

		# hocr output conversion
		res = [] # distance, code
		with codecs.open(path+"/frame%d-segment%d.hocr" % (frame, i), 'r', 'utf-8') as hocr_output:
			for line in hocr_output:
				# find x-coordinate of upper left corner
				location = re.search(r'(?<=bbox ).+?(?=\s)', line)
				spans = re.findall(r'<span[^>]*>.*?</span>', line)
				if len(spans) > 1:
					val = re.sub(r'<[^>]*>', '', spans[0])
					if val.isdigit(): # inside first inner span
						location = re.search(r'(?<=bbox ).+?(?=\s)', spans[1])

				# ignore tags and extract code
				text = re.sub(r'<[^>]*>', '', line.strip())
				text = re.sub(r'^\d+\b', '', text.strip()) # https://regex101.com
				# fix special characters
				text = unidecode(text).strip() # "untested"
				# text = text.replace(u'\u201c', '"').replace(u'\u201d', '"')
				# text = text.replace(u'\u2018', '\'').replace(u'\u2019', '\'')
				# decode HTML-safe sequences
				text = parser.unescape(text)

				if location != None:
					if re.findall(r'\w+', text):
						res.append([int(location.group(0)), text])

		# spacing adjustment

		if len(res) == 0:
			os.system("rm "+path+"/frame%d-segment%d.*" % (frame, i))

		else:
			os.system("rm "+path+"/frame%d-segment%d.hocr" % (frame, i))
			base = min(res, key=operator.itemgetter(0))[0]

			# yet to address case when 30,33,62 happens
			temp = [r for r in res if r[0] > base*1.09] # when base = 0
			if len(temp) == 0:
				lines = ""
				for r in res:
					lines += r[1] + "\n"

				# _dis[placed]
				f = codecs.open(path+"/frame%d-segment%d.txt" % (frame, i), 'w', 'utf-8') # _check.txt
				f.write(lines)

			else:
				tab = min(temp, key=operator.itemgetter(0))[0]-base

				res = [[int(round((r[0]-float(base))/tab)), r[1]] for r in res]
				indented_lines = ""
				for r in res:
					indented = ""
					for x in range(r[0]):
						indented += unit_indent
					indented += r[1]
					indented_lines += indented + "\n"

				# _ind[ented]
				f = codecs.open(path+"/frame%d-segment%d.txt" % (frame, i), 'w', 'utf-8')
				f.write(indented_lines)
