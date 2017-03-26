import diff_match_patch as dmp
import ocr, re, sys, numpy, json

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

output_code = []
output_start = [0]

buffer = ['']
change_measure, past_measure = [], []
total_frames, unmatched_measure = 0, []
read, th, inc = True, 0, 0
while fnum < 216000:
	s = 3 # read number of segments
	try:
		file = open(path+'/main/frame%d-segment1.txt' % fnum)
		#if not read: print
		sys.stdout.write("\r100%\033[K")
		# previous count
		print '\r%d: frame %d' % (len(buffer)-1, fnum),
		sys.stdout.flush()
		read = True
	except:# IOError:
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
		try: file = open(path+'/main/frame%d-segment%d.txt' % (fnum, snum))
		except: continue
		total_frames += 1
		txt = file.read()
		file.close()

		txt = txt.decode('ascii', 'ignore') # todo
		keywords = ocr.strict_check(txt)
		tag = 'main'
		if len(keywords) == 0:
			keywords = ocr.check_for_keywords(txt)
			if(len(keywords) > 0):
				tag = 'maybe'
			else:
				tag = 'unlikely'

		if txt != '' and tag != 'unlikely':
			if txt in buffer:
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w') #i
				# todo: move related files
				f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()
			else:
			# if txt not in buffer:
				merged = False
				for i in range(min(len(buffer), 10)):
					pc, d, diffs = compare(buffer[len(buffer)-i-1], txt)
					if pc < 70:
						change_measure.append(pc)
						past_measure.append(i+1)
						inc += 1
						buffer[len(buffer)-i-1] = txt # todo: account for scrolling
						merged = True
						break
					else:
						unmatched_measure.append(pc)
				if not merged:
					output_code.append(buffer[-1])
					output_start.append((fnum-1)/24)
					buffer.append(txt)

				# if len(buffer) > 4:
					# todo: print '\nreached buffer capacity'
					# buffer.pop(0)

				# move related files too?
				f = open(path+'/%s/frame%d-segment%d.html' % (tag, fnum, snum), 'w')
				if merged: f.write(d.diff_prettyHtml(diffs))
				else: f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.close()

	# go to next frame
	fnum += fps
output_code.append(txt)

# but not identical
print '\n\nframes with incremental changes:', inc
print 'average extent of edit (%):', round(numpy.mean(change_measure), 2)
print 'average change on breaking (%):', round(numpy.mean(unmatched_measure), 2)
print 'average depth of successful lookback:', round(numpy.mean(past_measure), 2)
print 'total frames:', total_frames

def eprint(t):
	sys.stderr.write(t)

eprint('{\n')

eprint( # width options (4 for 720p, 5 for 540p)
'"name": "CS50 2016 - Week 8 - Python",\n\
"width": 5,\n\
"fps": 24,\n\
"duration": 7980,\n'
)

mi = len(output_start)-1
eprint('"start": [')
for i in range(len(output_start)):
	if i%10 == 0:
		eprint('\n\t')
	eprint(str(output_start[i])+', ')
	# next = output_start[i+1] if i < mi else 1886
	# eprint(str(next-output_start[i])+', ')

eprint('\n],\n')

eprint('"code": [\n')
for i in range(len(output_code)):
	eprint('\t['+json.dumps(output_code[i])+'], \n')

eprint('],\n')

eprint('"l": [')
for i in range(len(output_start)):
	if i%5 == 0:
		eprint('\n\t')
	eprint('["Python"]'+', ')

eprint('\n]\n')

eprint('}')
