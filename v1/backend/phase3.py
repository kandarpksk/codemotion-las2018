import diff_match_patch as dmp
import ocr, re, sys

vnum, fnum, fps = 3, 49, 24
print 'starting with frame', fnum, '\n'

path = '../public/extracts/video'+str(vnum)

code = ['']
read, th, inc = True, 0, 0
while fnum < 216000:
	s = 3 # read number of segments
	try:
		file = open(path+'/frame%d-segment1.txt' % fnum)
		#if not read: print
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
		#s = 0
	file.close()

	# read text from each segment
	for snum in range(s):
		try: file = open(path+'/frame%d-segment%d.txt' % (fnum, snum))
		except: continue
		txt = file.read()
		file.close()

		txt = txt.decode('ascii', 'ignore')
		keywords = ocr.strict_check(txt)
		tag = ''
		if len(keywords) == 0:
			keywords = ocr.check_for_keywords(txt)
			if(len(keywords) > 0):
				tag = 'maybe'
			else:
				tag = 'unlikely'

		if txt != '' and tag != 'unlikely':
			if txt == code[-1] or txt in code:
				f = open(path+'/%s/frame%d-segment%di.html' % (tag, fnum, snum), 'w')
				# todo: move related files
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
				d = dmp.diff_match_patch()
				diffs = d.diff_main(code[-1], txt, False)
				d.diff_cleanupSemantic(diffs)
				l, total, change = [[]], 0, 0
				for x in diffs:
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

				#move related files too
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')

				f.write(d.diff_prettyHtml(diffs))
				f.close()

	# go to next frame
	fnum += fps

# but not identical
print '\nframes with incremental changes:', inc
