
/*
 * GET home page.
 */

// function readTextFile(filepath) {
// 	var rawFile = new XMLHttpRequest()
// 	rawFile.open("GET", filepath, false)
// 	rawFile.onreadystatechange = function () {
// 		if(rawFile.readyState === 4)
// 			if(rawFile.status === 200 || rawFile.status == 0) {
// 				var allText = rawFile.responseText
// 				alert(allText)
// 			}
// 	}
// 	rawFile.send(null)
// }

var dummy_data = {
	name: 'CS50 2016 - Week 8 - Python', // tutorial name
	segments: [
		{
			voiceover: 'first segment voiceover',
			code: [
				{ text: '//show accumulated code', language: 'javascript', l: 'js' },
				// { text: 'a2', language: 'c_cpp', l: 'c' }
				// multiple snippets?
			],
			url: 'videos/5aP9Bl9hcqI_2_720p.mp4',
			start: 0
		},
			{
			voiceover: 'next segment voiceover', // •SRT
			code: [
				{ text: '# todo', language: 'python', l: 'py' }, // highlight, shortened
				// { text: 'b2', language: 'php', l: 'php' },
				// { text: 'b3', language: 'ruby', l: 'ruby' }
			],
			url: 'videos/5aP9Bl9hcqI_2_720p.mp4',
			start: 410
		}
	]
}

exports.view = function(req, res){
  res.render('index', dummy_data)
}