
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

var codename = { 'py': 'python',
			 'js': 'javascript',
			 'c': 'c_cpp',
			 'cpp': 'c_cpp' }
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
	var metadata = { name: 'Sample Video',
			fps: 24,
			start: [0, 410, 3600],
			code: ['//show accumulated code', '#todo', ''],
			l: ['js', 'py', 'c']
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

exports.code = function(req, res) {
	if(data.fps == 1) initialize()

	var frame = (req.params.time * data.fps) + 1
	try {
		var base = 'public/extracts/video3/frame'+frame
		var segments = parseInt(fs.readFileSync(base+'.txt', 'utf8'))

		var contents = '', count = 0
		for (var i = 0; i <= segments; i++) //ensure not zero
			try {
				var content = fs.readFileSync(base+'-segment'+i+'.txt', 'utf8')
				count += 1
				contents += content+'\n' //'-----------\n segment '+count+'\n-----------\n' + content
			} catch(error) {
				/* do nothing */
			}
		if(count == 0) res.send('# no code segments')
		else res.send('# '+count+' segment(s) at time '+req.params.time+'\n\n'+contents)
	} catch(error) {
		console.log('# no text segments found for frame', frame)
		res.send('no code segments')
	}
}
