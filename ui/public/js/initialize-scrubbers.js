function initializeScrubbers() {
	$('.video-container').each(function() {
		var $video = $(this).find('video')
		var $scrubber = $(this).find('#scrubber')
		var $progress = $(this).find('#progress')
		// show time

		$video.bind('timeupdate', videoTimeUpdater)
		$scrubber.bind('mousedown', scrubberMouseDown)
	})
}

function videoTimeUpdater(e) {
	var percent = this.currentTime / this.duration
	updateProgressWidth($(this.parentNode).find('#progress')[0], percent)

	var fnum = Math.round(this.currentTime*10)/10
	var editor_id = $(this.parentNode.parentNode).find('.editor')[0].id
	$.get('extracts/video1-frame'+1+'-segment1.txt',
		function(response) {
			var editor = ace.edit(editor_id)
			editor.session.setValue('refreshed at time '+fnum+'\n---\n'+response)
			// editor.getSession().setMode('ace/mode/'+)
	})
}

function scrubberMouseDown(e) {
	var $this = $(this)
	var x = e.pageX - $this.offset().left
	var percent = x / $this.width()
	updateProgressWidth($(this).find('#progress')[0], percent)
	updateVideoTime($(this.parentNode).find('video')[0], percent)
}

function updateProgressWidth(progress, percent) {
	$(progress).width((percent * 100) + '%')
}

function updateVideoTime(video, percent) {
	video.currentTime = percent * video.duration
}