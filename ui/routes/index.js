
/*
 * GET home page.
 */

// function readTextFile(filepath) {
// 	var rawFile = new XMLHttpRequest()
// 	rawFile.open('GET', filepath, false)
// 	rawFile.onreadystatechange = function () {
// 		if(rawFile.readyState === 4)
// 			if(rawFile.status === 200 || rawFile.status == 0) {
// 				var allText = rawFile.responseText
// 				alert(allText)
// 			}
// 	}
// 	rawFile.send(null)
// }

const fs = require('fs')
var contents = fs.readFileSync('public/other/video3.txt', 'utf8').split('\n')
// const rl = require('readline')
// var lineReader = rl.createInterface({ input: fs.createReadStream('public/other/video3.txt') })
var subtitles = {}, i
for(i = 0; i < contents.length; i++) {
	var j = contents[i].indexOf(' ')
	var t = contents[i].substr(0, j).split(':')
	subtitles[parseInt(t[0])*60 + parseInt(t[1])] = contents[i].substr(j+1)
}
// lineReader.on('line', function(line) {
// 	var i = line.indexOf(' ')
// 	var t = line.substr(0, i).split(':')
// 	subtitles[parseInt(t[0])*60 + parseInt(t[1])] = line.substr(i+1)
// })
// console.log(Object.keys(subtitles).length)

function closest(t) {
	while (subtitles[t] == undefined)
		t += 1
	return subtitles[t]
}

var dummy_data = {
	name: 'CS50 2016 - Week 8 - Python', // tutorial name
	segments: [
		{
			voiceover: closest(1),
			code: [
				{ text: '//show accumulated code', language: 'javascript', l: 'js' },
				//{ text: 'a2', language: 'c_cpp', l: 'c' }
				//multiple snippets?
			],
			url: 'videos/video3.mp4',
			start: 0
		},
			{
			voiceover: closest(410),
			code: [
				// format: code, highlight, shortened
				{ text: '# todo', language: 'python', l: 'py' },
				//{ text: 'b2', language: 'php', l: 'php' },
				//{ text: 'b3', language: 'ruby', l: 'ruby' }
			],
			url: 'videos/video3.mp4',
			start: 410
		}
	]
}

exports.view = function(req, res) {
  res.render('index', dummy_data)
}

exports.transcript = function(req, res) {
	res.send(subtitles[req.params.time])
}

exports.closest = function(req, res) {
	res.send(closest(req.params.time))
}