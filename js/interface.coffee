# Handle the interface size
window.handleResize = ->
	# Update the status bar font size so that it doesn't get too big
	$('.statusbar').css('font-size', (0.9 * $('.statusbar').height()) + 'px' )
	#$('.card').css('font-size',$('.card').width())
	# Scroll the window to the top (solves some problems when rotating phones)
	$(window).scrollTop(0);

$(window).bind 'resize', window.handleResize

$ ->
	window.handleResize()
	$('.interface > div').each ->
		$(@).hide()
	

	# Check for CDN failure and refresh if yes
	if !$.ui? or !$.mobile?
		location.reload true

window.updateStatusBar = ->
	window.updateInterface()

window.updateInterface = ->
	if this.stage? 
		this.stage.update()

window.updateCountdown = ->
	# Write in the time.
	$('.countdown').html stage.time	