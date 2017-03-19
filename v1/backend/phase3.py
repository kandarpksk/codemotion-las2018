import diff_match_patch as d
import arrow_keys as kb
import ocr, unidecode, re

vnum, fnum, fps = 4, 1, 30.001050 # fnum: 94009#47401
print 'starting with frame', fnum, '\n'

code, prev = ['', '', '', '', ''], 'lo'
while True:
	#if prev == '': next = kb.get()
	#if next == 'right' or next == 'down' or prev != '':
		# read number of segments
		try: file = open('preview/resources%d/frame%d.txt' % (vnum, fnum))
		except IOError: print 'no more files'; break
		s = int(file.read())
		file.close()
		
		# read text from all segments
		new_text = ''
		for snum in range(s):
			try: file = open('preview/resources%d/frame%d_segment%d.txt' % (vnum, fnum, snum))
			except IOError: continue
			# distance text from separate segments
			if new_text != '': new_text += '\n'
			txt = file.read()
			txt = txt.decode('ascii', 'ignore')
			keywords = ocr.strict_check(txt)
			if(len(keywords) > 0):
				# print 'txt:', txt
				print 'check:', len(keywords)
				# print keywords
				new_text += txt
			else:
				keywords = ocr.check_for_keywords(txt)
				if(len(keywords) > 0):
					new_text += '\n# maybe\n' + txt
				else:
					new_text += '\n# unlikely\n' + txt
			file.close()
		
		# show any text extracted
		if new_text != '':
			if new_text == code[4]:
				print fnum, 'identical=======\n'
				prev = 'id'

				# dmp = d.diff_match_patch()
				# diffs = dmp.diff_main(code[4], new_text)
				f = open('preview/resources%d/frame%d.html' % (vnum, fnum), 'w')
				# f.write('<meta http-equiv="refresh" content="1">')
				# f.write(dmp.diff_prettyHtml(diffs))
				f.write('<pre>' + new_text.replace('\n', '<br/>') + '</pre>') # code, not diff
				f.close()
			else:
				code.pop(0)
				code.append(new_text)
				
				dmp = d.diff_match_patch()
				diffs = dmp.diff_main(code[3], code[4])
				dmp.diff_cleanupSemantic(diffs)
				print 'diffs:'
				for x in diffs:
					# if x[0] != 0:
						for line in re.split('\n|\\n', x[1]) :
							if x[0] == -1: print '-',
							elif x[0] == 1: print '+',
							else: print '=',
							print line.rstrip()

				f = open('preview/resources%d/frame%d.html' % (vnum, fnum), 'w')
				print 'preview/resources%d/frame%d.html' % (vnum, fnum)
				# f.write('<meta http-equiv="refresh" content="1">')
				f.write(dmp.diff_prettyHtml(diffs))
				f.close()

				#patches = dmp.patch_make(code[3], diffs)				
				#print dmp.patch_toText(patches)
				
				print 'code:',
				print code[4].rstrip()
				print '----------------'
				prev = ''
		else:
			# if prev != 'bl':
				# print fnum, 'empty'
			prev = 'bl'
		
		# go to next frame
		fnum += fps
	
	#else: print 'break'; break