import diff_match_patch as dmp
import ocr, re, sys, numpy, json

MIN_INTERVAL = 10

vnum, fnum, fnumf = int(sys.argv[1]), 1, 1.
fps = [15.002999, 29.970030, 30, 23.976150, 30, 29.970030, 30.001780, 30, 29.970030, 29.970030, 30, 15, 23.976024, 30, 15, 30, 29.873960, 30, 15, 25.000918, 30][vnum-1]
#... print 'starting with frame', fnum, '\n'

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
			if len(part)>1: # ignore lookalikes
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
output_time = [[0, 0]]
# start and end

buffer = ['']
change_measure, past_measure = [], []
total_frames, unmatched_measure = 0, []
read, th, inc, upd, txt = True, 0, 0, -1, ''
while fnum < 216000:
	s = 3 # read number of segments
	try:
		file = open(path+'/frame%d-segment1.txt' % fnum)
		file.close()
		#if not read: print
		# sys.stdout.write("\r100%\033[K")
		# previous count
		# print '\r%d: frame %d' % (len(buffer)-1, fnum),
		sys.stdout.flush()
		read = True
	except:# IOError:
		if read and fnum > th:
			# print #
			th += 5000
		# sys.stdout.write("\r100%\033[K")
		# previous count
		# print '\r%d: frame %d missing' % (len(buffer)-1, fnum),
		sys.stdout.flush()
		read = False
		#s = 0 #maybe

	# read text from each segment
	for snum in range(s):
		try: file = open(path+'/frame%d-segment%d.txt' % (fnum, snum))
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

		if txt != '' and tag == 'unlikely':
			f = open(path+'/%s/frame%d-segment%d.txt' % (tag, fnum, snum), 'w')
			f.write(txt)
			f.close()
		if txt != '' and tag != 'unlikely':
			if txt == buffer[-1]:
				output_time[-1][1] = (fnum-1)/24 # update end time
				f = open(path+'/%s/frame%d-segment%d.txt' % (tag, fnum, snum), 'w') #i
				# todo: move related files
				# f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.write(txt)
				f.close()
			else:
			# if txt not in buffer:
				merged = False
				for i in range(min(len(buffer), 10)):
					pc, d, diffs = compare(buffer[len(buffer)-i-1], txt)
					if pc == 0:
						past_measure.append(i+1)
						output_time[len(buffer)-i-1][1] = (fnum-1)/24
						buffer[len(buffer)-i-1] = txt # todo: account for scrolling
						merged = True
						break
					elif pc < 70:
						change_measure.append(pc)
						past_measure.append(i+1)
						inc += 1
						# update end time
						output_time[len(buffer)-i-1][1] = (fnum-1)/24
						# if upd != len(buffer)-i-1:
						#... print (fnum-1)/24, ': updated end time of interval', len(buffer)-i-1
							# upd = len(buffer)-i-1
						buffer[len(buffer)-i-1] = txt # todo: account for scrolling
						# if i != 0: # update output code?
							# print 'update output code'
						merged = True
						break
					else:
						unmatched_measure.append(pc)
				if not merged:
					output_code.append([buffer[-1], snum])
					output_time.append([(fnum-1)/24, (fnum-1)/24])
					#... print (fnum-1)/24, ': starting interval', len(buffer), '(segment', str(snum)+')'
					buffer.append(txt)

				# if len(buffer) > 4:
					# todo: print '\nreached buffer capacity'
					# buffer.pop(0)

				# move related files too?
				f = open(path+'/%s/frame%d-segment%d.txt' % (tag, fnum, snum), 'w')
				# if merged: f.write(d.diff_prettyHtml(diffs))
				# else: f.write('<pre>' + txt.replace('\n', '<br/>') + '</pre>')
				f.write(txt)
				f.close()

	# go to next frame
	fnumf += fps
	fnum = int(round(fnumf))
# todo: if not merged
output_code.append([txt, -1])

# but not identical
if change_measure: print round(sum(change_measure)/len(change_measure), 2)
if unmatched_measure: print round(sum(unmatched_measure)/len(unmatched_measure), 2)
if past_measure: print round(sum(past_measure)/len(past_measure), 3)
print len(buffer)-1
print '...'
print total_frames

def eprint(t):
	sys.stderr.write(t)

last = -1
for i in range(len(output_code)):
	if last == -1 or output_time[i][0]-output_time[last][0] > MIN_INTERVAL:
		eprint('\t['+json.dumps(output_code[i][0])+'], \n')
		last = i
	# else:
	# 	eprint('\t,'+json.dumps(output_code[i][0])+'\n\n')
