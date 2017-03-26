
const fs = require('fs')

var subtitles
function readSubtitle(filename) {
	process.stdout.write('loading subtitle...')

	var contents = fs.readFileSync('public/'+filename, 'utf8').split('\n')
	subtitles = {}
	for(var i = 0; i < contents.length; i++) {
		var j = contents[i].indexOf(' ')
		var t = contents[i].substr(0, j).split(':')
		subtitles[parseInt(t[0])*60 + parseInt(t[1])] = contents[i].substr(j+1)
	}
	// console.log(Object.keys(subtitles).length)

	console.log(' done!')
}

function closestSubtitle(t) {
	while (subtitles[t] == undefined && t >= 0)
		t = t - 1
	return subtitles[t]
}

function nextSubtitle(t) {
	// limit duration
	while (subtitles[t] == undefined) t += 1
	return subtitles[t]
}

var codename = require('../public/js/codename.json')
var interval_ends
function addSegment(start, end, text, l, duration) {
	interval_ends.push(end)
	var seg = {
		start: start,
		begin: Math.round(start/duration*100),
		end: Math.round(end/duration*100),
		voiceover: (closestSubtitle(start)) ?
				closestSubtitle(start) : nextSubtitle(start),
		code: []
	}
	for (i in text)
		seg.code.push({ text: text[i], language: codename[l[i]], l: l[i] })
	data.segments.push(seg)
}

var data = {
	name: 'tutorial title',
	url: 'video_path',
	fps: 1,
	segments: []
}

var vnum, finder, done = false
function initialize() {
	console.log('initializing backend')

	var metadata = { name: 'CS50 2016 - Week 8 - Python',
			width: 5,
			fps: 24,
			start: [0, 1606, 3600, 5400],
			duration: 7980,
			code: [['accumulated code', ''], [''], [''], ['']], // \n
			l: [['Text', 'Python'], ['Python'], ['C'], ['CPP']]
		} // dummy
	if (vnum != undefined)
		metadata = require('../public/other/video'+vnum+'.json')
		// probably just ask to refresh here
		// (as number of segments may differ)
	vnum = (vnum) ? vnum : 3

	readSubtitle('other/video'+vnum+'_sub.txt')
	data.name = metadata.name
	data.width = metadata.width
	data.fps = metadata.fps
	data.url = 'videos/video'+vnum+'.mp4'
	data.segments = []
	interval_ends = []
	for (var i = 0; i < metadata.start.length; i++)
		addSegment(metadata.start[i], (i+1 < metadata.start.length) ? metadata.start[i+1] : metadata.duration,
				metadata.code[i], metadata.l[i], metadata.duration)

	var fi = require('findit')
	finder = fi('public/extracts/video'+vnum+(vnum == 3 ? 'a' : '')) // temp
	finder.on('file', function(file) {
		if (file.search('segment') != -1) {
			fs.readFile(file, 'utf8', function(err, dat) {
				var fnum = (parseInt(file.substring(file.search('frame')+5, file.search('-')))-1)/24
				var words = dat.match(/\b(\w+)\b/g)
				for(i in words)
					if (table[words[i]]) {
						if(!table[words[i]].includes(fnum))
							table[words[i]].push(fnum)
					} else table[words[i]] = [fnum]
			})
		}
	})
	finder.on('end', function() { done = true })
}

exports.view = function(req, res) {
	vnum = req.query.vnum
	initialize()
	res.render('index', data)
}

exports.transcript = function(req, res) {
	try {
		res.send(subtitles[req.params.time])
	} catch(error) {
		console.log('couldn\'t read subtitles')
	}
}

exports.closest = function(req, res) {
	res.send(closestSubtitle(req.params.time))
}

var detect = require('language-detect')
exports.code = function(req, res) {
	if(data.fps == 1)
		initialize()

	var frame = (req.params.time * data.fps) + 1
	try {
		var base = 'public/extracts/video'+vnum+(vnum == 3 ? 'a' : '')+'/frame'+frame
		var segments = 3//parseInt(fs.readFileSync(base+'.txt', 'utf8'))

		var cs = [], count = 0
		for (var i = 0; i <= segments; i++) //ensure not zero
			try {
				var content = fs.readFileSync(base+'-segment'+i+'.txt', 'utf8')
				count += 1
				cs.push(content) //'-----------\n segment '+count+'\n-----------\n' + content
			} catch(error) {
				console.log('couldn\'t read frame '+frame+' segment '+i)
				/* do nothing */
			}
		if(count == 0)
			// todo: check out stackoverflow.com/questions/15903191
			// how-to-automatically-pick-a-mode-for-ace-editor-given-a-file-extension
			res.json( { code: ['# no code at this point'], language: [codename['Text']], l: ['Text'] } )
		else { /*'# '+count+' segment(s) at time '+req.params.time+'\n\n'+*/
			var l = []
			for (code_i in cs)
				l.push(detect.classify(cs[code_i]))
			var language = []
			for (lang_i in l)
				language.push(codename[l[lang_i]])
			res.json( { code: cs, language: language, l: l } )
		}
	} catch(error) {
		console.log('# no text segments found for frame', frame)
		res.json( { code: ['# no segments present'], language: [codename['Text']], l: ['Text'] } )
	}
}

var table = {}
exports.search = function(req, res) {
	if (vnum == undefined) // undefined
		initialize()

	if (done) {
		var terms = req.params.term.match(/\b(\w+)\b/g)
		//console.log(terms) // profile indexing
		var apos = table[terms[0]] ? table[terms[0]] : [] //[2394, 3990, 7182]

		// absolute position (i.e. time elapsed)
		res.json({ ie: interval_ends, apos: apos, error: 'none' })
	} else /*vid: data.segments, apos: [],*/
		res.json({ error: 'wait' })
}
