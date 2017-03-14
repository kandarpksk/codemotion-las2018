function initializeScrubbers() {
	$('.video-container').each(function() {
		$(this).find('video').bind('timeupdate', videoTimeUpdater)
		$(this).find('#scrubber').bind('mousedown', scrubberMouseDown)
	})
}

var forceUpdate = false
function videoTimeUpdater(e) {
	// console.log('video-time-updater')
	var percent = this.currentTime / this.duration
	updateProgressWidth($(this.parentNode).find('#progress'), percent, this.currentTime, this.duration)

	var fnum = Math.floor(this.currentTime)
	var editor_id = $(this.parentNode.parentNode).find('.editor')[0].id
	var video = this
	$.get('/code/'+fnum,
		function(resp) {
			// console.log('get-code')
			var cc = 0
			if(!video.paused || forceUpdate) {
				var editor = ace.edit(editor_id), changed = false
				var notEmpty = resp.code[0] != '# no code at this point'
						&& resp.code[0] != '# no segments present'
				var mod = (editor.session.getValue() != resp.code[cc])
				// console.log(mod ? 'modified' : 'consistent')
				if ((notEmpty || forceUpdate) && mod) {
					editor.session.setValue(resp.code[cc])
					// console.log('updated code (frame: '+fnum+')')
					changed = true
					editor.getSession().setMode('ace/mode/'+(resp.language[cc] ? resp.language[cc] : 'text'))
				} // not sure about previous line
				var pills = $('#'+editor_id).parent().parent().find('.pills')
				if (pills.html() != resp.l[cc] && changed) {
					// temporarily add (and then hide) other languages
					if (resp.l[cc] != 'Shell')
						console.log(resp.l[cc])
					pills.each(function() {
						if ($(this).html().trim() == resp.l[cc])
							$(this).addClass('badge-info')
						else $(this).removeClass('badge-info')
					})
					// pills.fadeOut(video.paused ? 50 : 300, function() {
					// 	$(this).text(resp.l[cc]).fadeIn(video.paused ? 50 : 300)
					// })
				}
				// $('#lf').append('<br>'+resp.l)
				forceUpdate = false
				highlightWords()
			}
	}).fail(function() {
		console.log('couldn\'t get code from server')
	})
}

function scrubberMouseDown(e) {
	//// console.log('scrubber-mouse-down')
	var percent = (e.pageX - $(this).offset().left) / $(this).width()
	var video = $(this.parentNode).find('video')[0]
	$('#'+video.id.split('-')[0]+'-vo').html('<span style="opacity: 0">...</span')
	forceUpdate = true
	updateVideoTime(video, percent)
	$.get('/closest/'+Math.floor(video.currentTime),
		function(result) {
			// console.log('get-closest-voiceover')
			$('#'+video.id.split('-')[0]+'-vo').html(result)
	})
	updateProgressWidth($(this).find('#progress'), percent, video.currentTime, video.duration)
}

function updateProgressWidth($progress, percent, time, duration) {
	function lead(n) {
	    return (n < 10) ? ('0' + n) : n;
	}

	$progress.width((percent * 100) + '%')
	
	// show time elapsed
	var t, limit = (duration < 3600) ? 0.13 : 0.10
	if (duration > 3600)
		t = Math.floor(time/3600) + ':' + lead(Math.floor((time%3600)/60)) + ':' + lead(Math.floor(time%60))
	else // hour not shown
		t = Math.floor((time%3600)/60) + ':' + lead(Math.floor(time%60))
	// var video = $progress.parent().parent().find('video')[0]
	// console.log('loaded:', video.buffered.end(0) / duration * 100)
	if(percent < limit)
		$progress.find('#time').html('<span style="margin-left: 5px; color: black">' + t + '</span>')
	else
		$progress.find('#time').html('<span style="margin-left: 5px; color: teal">' + t + '</span>')
}

function updateVideoTime(video, percent) {
	video.currentTime = percent * video.duration
}
