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

class @InventoryPanel
	constructor: () ->
		@dom_element =  $('.inventory');
		@button_element =  $('.inventory-button')
		# Set up the clicking.
		@button_element.click =>
			@dom_element.toggle()

		@needsRefresh()

	needsRefresh: ->
		if window.player?
			for n,p of window.player.products
				p.needsRefresh()
		yes