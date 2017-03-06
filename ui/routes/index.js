
/*
 * GET home page.
 */

var subtitles
function readSubtitle(filename) {
	process.stdout.write('loading subtitle...')

	const fs = require('fs')
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

function nextSubtitle(t) {
	// limit duration
	while (subtitles[t] == undefined)
		t += 1
	return subtitles[t]
}

var codename = { 'py': 'python',
			 'js': 'javascript',
			 'c': 'c_cpp',
			 'cpp': 'c_cpp' }
function addSegment(start, text, l) {
	data.segments.push({
		start: start,
		voiceover: nextSubtitle(start),
		code: [
			// loop
			{ text: text, language: codename[l], l: l }
		]
	})
}

var data = {
	name: 'tutorial title',
	url: 'video_path',
	segments: []
}

exports.view = function(req, res) {
	var vnum = (req.query.vnum) ? req.query.vnum : 3
	var metadata = { name: 'Sample Video',
			start: [0, 410, 3600],
			code: ['//show accumulated code', '#todo', ''],
			l: ['js', 'py', 'c']
		} // dummy
	if (req.query.vnum != undefined)
		metadata = require('../public/other/video'+vnum+'.json')
	
	readSubtitle('other/video'+vnum+'.txt')
	data.name = metadata.name
	data.url = 'videos/video'+vnum+'.mp4'
	data.segments = []
	for (var i = 0; i < metadata.start.length; i++)
		addSegment(metadata.start[i], metadata.code[i], metadata.l[i])

	res.render('index', data)
}

exports.transcript = function(req, res) {
	res.send(subtitles[req.params.time])
}

exports.closest = function(req, res) {
	res.send(nextSubtitle(req.params.time))
}