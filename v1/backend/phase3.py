dbug = False # new

import diff_match_patch as dmp
import arrow_keys as kb
import ocr, unidecode, re, sys

vnum, fnum, fps = 3, 49, 24
print 'starting with frame', fnum, '\n'

path = '../public/extracts/video'+str(vnum)

code, prev = [''], 'begin'
read, th, inc = True, 0, 0
while fnum < 216000:
	# read number of segments
	try:
		file = open(path+'/frame%d-segment1.txt' % fnum)
		# if not read: print
		sys.stdout.write("\r100%\033[K")
		# previous count
		print '\r%d: frame %d' % (len(code)-1, fnum),
		sys.stdout.flush()
		read = True
	except IOError:
		if read and fnum > th:
			print
			th += 5000
		sys.stdout.write("\r100%\033[K")
		# previous count
		print '\r%d: frame %d missing' % (len(code)-1, fnum),
		sys.stdout.flush()
		read = False
	s = 3 # int(file.read())
	file.close()

	# todo: ignore entire windows, language detection

	# read text from each segment
	for snum in range(s):
		# print snum,
		try: file = open(path+'/frame%d-segment%d.txt' % (fnum, snum))
		except: continue

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
		if txt != '' and tag != 'unlikely':
			if txt == code[-1] or txt in code:
				f = open(path+'/%s/frame%d-segment%di.html' % (tag, fnum, snum), 'w')
				# todo: move related files
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
				d = dmp.diff_match_patch()
				# a = d.diff_linesToWords(code[-2], code[-1]) # check -2
				# lineText1, lineText2 = a[0], a[1]
				# lineArray = a[2]
				diffs = d.diff_main(code[-1], txt, False)
				# diffs = d.diff_main(lineText1, lineText2, False)
				# d.diff_charsToLines(diffs, lineArray) # works for words too
				d.diff_cleanupSemantic(diffs)
				# if dbug or fnum == 4897:
					# print '\ndiffs:\n'
				l, total, change = [[]], 0, 0
				for x in diffs:
				# if x[0] != 0: # unchanged (check again)
					lines = re.split('\n|\\n', x[1])
					for part in lines:
						total += len(part)
						if len(part)>1:
							# print len(l),

							if x[0] == 1:
								# print '+', part.rstrip(), '\t',
								if l[-1] and l[-1][-1] == 'mod':
									l[-1].pop() # big changes?
								else: l[-1].append('new')
								change += len(part)
							elif x[0] == -1:
								# print '-', part.rstrip(), '\t',
								l[-1].append('mod')
								change += len(part)
							else:
								l[-1].append('sim')
								# print '~',
							## print part.rstrip(), '\t',

							if part != lines[-1]:
								l.append([])
								# print list(set(l[-2]))
					## print
				pc = int(round(change*100./total))
				# print str(pc)+'%',

				# if len(code) > 4:
					# todo: print '\nreached buffer capacity'
					# code.pop(0)
				if pc < 70:
					inc += 1
					code[-1] = txt
				else:
					# print '\n', txt
					code.append(txt)

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

print '\nframes with incremental changes:', inc
