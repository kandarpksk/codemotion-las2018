dbug = False # new

import diff_match_patch as d
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
		print '\rframe%d, segment1' % fnum,
		sys.stdout.flush()
		read = True
	except IOError:
		if read and fnum > th:
			print
			th += 5000
		print '\rno more files...     ',
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
			if txt == code[-1]:
				if dbug: print fnum, 'identical=======\n'
				prev = 'blink'

				# dmp = d.diff_match_patch()
				# diffs = dmp.diff_main(code[-1], txt)
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')
				# todo: move related files

				# f.write('<meta http-equiv="refresh" content="1">')
				# f.write(dmp.diff_prettyHtml(diffs))

				# just code instead of diff
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
				if len(code) > 4:
					# todo: print '\nreached buffer capacity'
					code.pop(0)
				code.append(txt)

				dmp = d.diff_match_patch()
				diffs = dmp.diff_main(code[-2], code[-1])
				dmp.diff_cleanupSemantic(diffs)
				if dbug: print 'diffs:'
				if dbug:
					for x in diffs:
					# if x[0] != 0:
						for line in re.split('\n|\\n', x[1]) :
							if x[0] == -1: print '-',
							elif x[0] == 1: print '+',
							else: print '=',
							print line.rstrip()

				# move related files too
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')
				if dbug: print path+'/frame%d.html' % fnum

				# f.write('<meta http-equiv="refresh" content="1">')
				f.write(dmp.diff_prettyHtml(diffs))
				f.close()

				#patches = dmp.patch_make(code[-2], diffs)
				#if dbug: print dmp.patch_toText(patches)

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
