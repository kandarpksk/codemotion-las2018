import diff_match_patch as dmp
import ocr, re, sys, numpy

vnum, fnum, fps = 3, 49, 24
print 'starting with frame', fnum, '\n'

path = '../public/extracts/video'+str(vnum)

def compare(known, txt):
	d = dmp.diff_match_patch()
	diffs = d.diff_main(known, txt, False)
	d.diff_cleanupSemantic(diffs)
	l, total, change = [[]], 0, 0
	for x in diffs:
		lines = re.split('\n|\\n', x[1])
		for part in lines:
			total += len(part)
			if len(part)>1:
				if x[0] == 1:
					if l[-1] and l[-1][-1] == 'mod':
						l[-1].pop() # big changes?
					else: l[-1].append('new')
					change += len(part)
				elif x[0] == -1:
					l[-1].append('mod')
					change += len(part)
				else:
					l[-1].append('sim')

				if part != lines[-1]:
					l.append([]) #print list(set(l[-2]))
	return int(round(change*100./total)), d, diffs

buffer = ['']
change_measure, past_measure = [], []
total_frames, unmatched_measure = 0, []
read, th, inc = True, 0, 0
while fnum < 216000:
	s = 3 # read number of segments
	try:
		file = open(path+'/frame%d-segment1.txt' % fnum)
		#if not read: print
		sys.stdout.write("\r100%\033[K")
		# previous count
		print '\r%d: frame %d' % (len(buffer)-1, fnum),
		sys.stdout.flush()
		read = True
	except IOError:
		if read and fnum > th:
			print
			th += 5000
		sys.stdout.write("\r100%\033[K")
		# previous count
		print '\r%d: frame %d missing' % (len(buffer)-1, fnum),
		sys.stdout.flush()
		read = False
		#s = 0 #maybe
	file.close()

	# read text from each segment
	for snum in range(s):
		try: file = open(path+'/frame%d-segment%d.txt' % (fnum, snum))
		except: continue
		total_frames += 1
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
			if txt == buffer[-1] or txt in buffer:
				f = open(path+'/%s/frame%d-segment%di.html' % (tag, fnum, snum), 'w')
				# todo: move related files
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
				merged = False
				for i in range(min(len(buffer), 10)):
					pc, d, diffs = compare(buffer[len(buffer)-i-1], txt)
					if pc < 70:
						change_measure.append(pc)
						past_measure.append(i+1)
						inc += 1
						buffer[-1] = txt # todo: account for scrolling
						merged = True
						break
					else:
						unmatched_measure.append(pc)
				if not merged:
					buffer.append(txt)

				# if len(buffer) > 4:
					# todo: print '\nreached buffer capacity'
					# buffer.pop(0)

				#move related files too
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')

				f.write(d.diff_prettyHtml(diffs))
				f.close()

	# go to next frame
	fnum += fps

# but not identical
print '\n\nframes with incremental changes:', inc
print 'average extent of edit (%):', round(numpy.mean(change_measure), 2)
print 'average change on breaking (%):', round(numpy.mean(unmatched_measure), 2)
print 'average depth of successful lookback:', round(numpy.mean(past_measure), 2)
print 'total frames:', total_frames

# {
# 	"start": [0],
# 	"code": [[""]],
# 	"l": [["Python"]]
# }
