dbug = False # new

import diff_match_patch as dmp
import arrow_keys as kb
import ocr, unidecode, re, sys

vnum, fnum, fps = 3, 49, 24
print 'starting with frame', fnum, '\n'

path = '../public/extracts/video'+str(vnum)

code, prev = [''], 'begin'
read, th = True, 0
while True:
	# read number of segments
	try:
		file = open(path+'/frame%d-segment1.txt' % fnum)
		# if not read: print
		print '\r%d: frame%d, segment1' % (len(code)-1, fnum),
		sys.stdout.flush()
		read = True
	except IOError:
		if read and fnum > th:
			print
			th += 5000
		print '\r%d: no more files...     ' % (len(code)-1),
		sys.stdout.flush()
		read = False
	s = 3 # int(file.read())
	file.close()

	# todo: ignore entire windows, language detection

	# read text from each segment
	for snum in range(s):
		try: file = open(path+'/frame%d-segment%d.txt' % (fnum, snum))
		except IOError: continue

		txt = file.read()
		txt = txt.decode('ascii', 'ignore')
		keywords = ocr.strict_check(txt)
		tag = ''
		if(len(keywords) > 0):
			if dbug: print 'check:', len(keywords)
		else:
			keywords = ocr.check_for_keywords(txt)
			if(len(keywords) > 0):
				tag = 'maybe'
			else:
				tag = 'unlikely'
		file.close()

		# show any text extracted
		if txt != '':
			if txt == code[-1] or txt in code:
				if dbug: print fnum, 'identical=======\n'
				prev = 'blink'

				# d = dmp.diff_match_patch()
				# diffs = d.diff_main(code[-1], txt)
				f = open(path+'/%s/frame%d-segment%di.html' % (tag, fnum, snum), 'w')
				# todo: move related files

				# f.write('<meta http-equiv="refresh" content="1">')
				# f.write(d.diff_prettyHtml(diffs))

				# just code instead of diff
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
				# if len(code) > 4:
					# todo: print '\nreached buffer capacity'
					# code.pop(0)
				code.append(txt)

				d = dmp.diff_match_patch()
				# a = d.diff_linesToWords(code[-2], code[-1]) # check -2
				# lineText1, lineText2 = a[0], a[1]
				# lineArray = a[2]
				diffs = d.diff_main(code[-2], code[-1], False)
				# diffs = d.diff_main(lineText1, lineText2, False)
				# d.diff_charsToLines(diffs, lineArray) # works for words too
				d.diff_cleanupSemantic(diffs)
				if dbug or fnum == 4897: print '\ndiffs:\n'
				if dbug or fnum == 4897:
					l, total, change = 1, 0, 0
					for x in diffs:
					# if x[0] != 0: # unchanged, iirc
						lines = re.split('\n|\\n', x[1])
						for part in lines:
							if len(part)>1:
								print l, len(part),
								total += len(part)
								if x[0] == -1:
									print '-', part.rstrip(), '\t',
									change += len(part)
								elif x[0] == 1:
									print '+', part.rstrip(), '\t',
									change += len(part)
								else: print '~',
								# print part.rstrip(), '\t',
								if part != lines[-1]: l += 1; print
						# print
					print str(int(round(change*100./total)))+'%'

				# move related files too
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')
				if dbug: print path+'/frame%d.html' % fnum

				# f.write('<meta http-equiv="refresh" content="1">')
				f.write(d.diff_prettyHtml(diffs))
				f.close()

				#patches = d.patch_make(code[-2], diffs) # check -2
				#if dbug: print d.patch_toText(patches)

				if dbug: print 'code:',
				if dbug: print code[-1].rstrip()
				if dbug: print '----------------'
				prev = ''
		else:
			# if prev != 'blank':
				# if dbug: print fnum, 'empty'
			prev = 'blank'

	# go to next frame
	fnum += fps
