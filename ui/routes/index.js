
/*
 * GET home page.
 */

var dcode = [
				'function foo(items) {\n\
	var x = \"All this is syntax highlighted\";\n\
	return x;\n\
}',
				'# \n\
def foo(items):\n\
	x = \"All this is syntax highlighted\"\n\
	return x'
]

var dummy_data = {
	name: 'CS50 2016 - Week 8 - Python', // tutorial name
	segments: [
		{
			voiceover: 'first segment voiceover',
			code: [
				{ text: dcode[0], language: 'javascript', l: 'js' },
				{ text: 'a2', language: 'c_cpp', l: 'c' }
			],
			url: 'videos/5aP9Bl9hcqI_2_720p.mp4',
			start: 0
		},
			{
			voiceover: 'next segment voiceover',
			code: [
				{ text: dcode[1], language: 'python', l: 'py' },
				{ text: 'b2', language: 'php', l: 'php' },
				{ text: 'b3', language: 'ruby', l: 'ruby' }
			],
			url: 'videos/5aP9Bl9hcqI_2_720p.mp4',
			start: 410
		}
	]
}

exports.view = function(req, res){
  res.render('index', dummy_data)
}