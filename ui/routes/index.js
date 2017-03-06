
/*
 * GET home page.
 */

var subtitles
function readSubtitle(filename) {
	process.stdout.write('loading subtitle...')

	const fs = require('fs')
	var i, contents = fs.readFileSync('public/'+filename, 'utf8').split('\n')
	subtitles = {}
	for(i = 0; i < contents.length; i++) {
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

readSubtitle('other/video3.txt')
var data = {
	name: 'CS50 2016 - Week 8 - Python',
	url: 'videos/video3.mp4',
	segments: []
}
addSegment(0, '//show accumulated code', 'js')
addSegment(410, '#todo', 'py')
addSegment(3600, '', 'c')

exports.view = function(req, res) {
	res.render('index', data)
}

exports.transcript = function(req, res) {
	res.send(subtitles[req.params.time])
}

exports.closest = function(req, res) {
	res.send(nextSubtitle(req.params.time))
}