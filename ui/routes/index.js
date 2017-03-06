
/*
 * GET home page.
 */

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
	// limit duration
	while (subtitles[t] == undefined && t >= 0)
		t = t - 1
	return subtitles[t]
}

var codename = require('../public/js/codename.json')
function addSegment(start, text, l) {
	data.segments.push({
		start: start,
		voiceover: (closestSubtitle(start)) ? closestSubtitle(start) : '<subtitles here>',
		code: [
			// loop
			{ text: text, language: codename[l], l: l }
		]
	})
}

var data = {
	name: 'tutorial title',
	url: 'video_path',
	fps: 1,
	segments: []
}

var vnum
function initialize() {
	var metadata = { name: 'CS50 2016 - Week 8 - Python',
			fps: 24,
			start: [1, 1606, 3600],
			code: ['', '', ''],
			l: ['Text', 'Python', 'Python']
		} // dummy
	if (vnum != undefined)
		metadata = require('../public/other/video'+vnum+'.json')
	vnum = (vnum) ? vnum : 3
	
	readSubtitle('other/video'+vnum+'.txt')
	data.name = metadata.name
	data.fps = metadata.fps
	data.url = 'videos/video'+vnum+'.mp4'
	data.segments = []
	for (var i = 0; i < metadata.start.length; i++)
		addSegment(metadata.start[i], metadata.code[i], metadata.l[i])
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
	if(data.fps == 1) initialize()

	var frame = (req.params.time * data.fps) + 1
	try {
		var base = 'public/extracts/video3/frame'+frame
		var segments = parseInt(fs.readFileSync(base+'.txt', 'utf8'))

		var cs = '', count = 0
		for (var i = 0; i <= segments; i++) //ensure not zero
			try {
				var content = fs.readFileSync(base+'-segment'+i+'.txt', 'utf8')
				count += 1
				cs += content+'\n' //'-----------\n segment '+count+'\n-----------\n' + content
			} catch(error) {
				/* do nothing */
			}
		if(count == 0)
			res.json( { code: '# no code segments', language: codename['Text'], l: 'Text' } )
		else { /*'# '+count+' segment(s) at time '+req.params.time+'\n\n'+*/
			var lang = detect.contents('abc', cs)
			res.json( { code: cs, language: codename[lang], l: lang } )
		}
	} catch(error) {
		console.log('# no text segments found for frame', frame)
		res.json( { code: 'no code segments', language: codename['Text'], l: 'Text' } )
	}
}

exports.search = function(req, res) {
	res.json({ vid: data.segments[1].start, pos: [30, 50, 90] })
}
