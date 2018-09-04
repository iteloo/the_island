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
			@toggle()

		# Create a sortable with the trading objects. This sortable is not actually sortable
		# (because when sorting completes, see the "stop" event, the thing is cancelled) but
		# when the sorting is over, if the player has moved the placeholder around the screen
		# then we consider that to be an action of either trading or selling.
		$('.inventory').sortable { 
				# The helper is a pop-up that appears while you are dragging the product around
				# the screen. It is created when sorting starts and destroyed when sorting ends.
				helper: (e, ui) ->
					type = ui.attr('data-production-type')
					if player.products[type].amount <= 0
						return $('<div></div>')
					else
						# Although the helper has class 'square', the size is forced by sortable to
						# match the size of the thing being sorted, which is in this case the trading product.
						return $("<div class='square placeholder'></div>").css('background-color', player.products[ui.attr('data-production-type')].color)
				,

				# This is called when sorting starts (i.e. somebody drags a trading product). 
				start: (e, ui) ->
					# It is necessary to show the trading product tile immediately because otherwise
					# it disappears, as per the default functionality of sortable.
					ui.item.show()
				,
				# This is called when sorting causes a re-ordering.
				change: ->
					# We don't want people to actually be able to sort the trading products, so I am 
					# just causing an instant refresh of the positions to keep them frozen.
					$(@).sortable "refreshPositions" 
				,
				# The placeholder is what sits in for the trading product (by default) when it is 
				# being moved around. But here, I am just filling it in as an un-used class.
				placeholder: 'test',
				# When sorting is finished (i.e. the user releases the tap, etc.) this is called.
				stop: (e,ui) ->
					# Where is the position of the thing? Look at the ending position and use that as a key
					offset = ui.originalPosition.top - ui.position.top
					#console.log 'moved to position: ', offset
					# Find out which item we are actually moving
					if stage instanceof TradingStage
						item = stage.products[ ui.item.attr('data-production-type') ]
						# Moving down corresponds to a "trade"
						if offset > 50
							item.trade.call item
						# It is very important that we cancel the sort in order to prevent things
						# from getting re-ordered.
						$(@).sortable 'cancel'
		}

		@quit_button = $("<div class='message-button quit-button'>Leave game</div>")
		# If someone clicks on the quit button, we need to double-check them
		# before they quit and all that
		@quit_button.click (e) =>
			e.preventDefault()
			console.log "quit button tapped!"
			m = new Message()
			m.respond = (response) =>
				if response == yes
					pycon.transaction 'quit'
			m.display("Sure to quit?", "", no, [{text: "leave game", id: yes}, {text: "don't quit", id: no}])
			yes
		$('.inventory').append @quit_button


		$('.inventory span.inventorycount').each ->
			$(@).html "<span class='block'>&#9632;</span> x <span class='count'>0</span>"
			type = $(@).attr('data-production-type')
			color = player.products[type].color
			$(@).children('.block').css('color',color)
			$(@).hide()

		$('.inventory span.inventorycount').taphold ->
			type = $(@).attr('data-production-type')
			pycon.transaction 'item_activated', { item_name: type }
			console.log "I tried to use a #{type}"

		@close()

		@needsRefresh()

	open: ->
		@dom_element.show()

	close: ->
		@dom_element.hide()

	toggle: ->
		@dom_element.toggle()

	needsRefresh: ->
		if window.player?
			for n,p of window.player.products
				p.needsRefresh()
		yes