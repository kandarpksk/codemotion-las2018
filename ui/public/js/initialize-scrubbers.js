function initializeScrubbers() {
	$('.video-container').each(function() {
		var $video = $(this).find('video')
		var $scrubber = $(this).find('#scrubber')
		var $progress = $(this).find('#progress')
		
		$video.bind('timeupdate', videoTimeUpdater)
		$scrubber.bind('mousedown', scrubberMouseDown)
	})

	function videoTimeUpdater(e) {
		var percent = this.currentTime / this.duration
		updateProgressWidth($(this.parentNode).find('#progress')[0], percent)
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
}