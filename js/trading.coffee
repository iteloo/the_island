# This class handles the setup and so forth of the 
# trading stage.

class window.TradingStage extends Stage
	constructor: ->
		console.log "testing testing"
		me = @
		@type = 'TradingStage'
		@timers = []

		$('.tradingstage-interface').show()
		player.update()

		$('.ready').show()

		$('.ready').tap =>
			@ready()

		$('.health').show()
		$('.hunger').show()
		# Register all of the trading products boxes. They are instances
		# of the class TradingProduct, which handles the visual behavior
		# of the trading boxes. They are connected to the player's set of
		# products.
		@products = {}
		$('.tradingstage-interface .trading span.tradecount').each ->
			type = $(@).attr('data-production-type')
			$(@).children('.block').css('background-color',player.products[type].color)
			me.products[type] = new TradingProduct( $(@), player.products[type] )
			me.products[type].product.needsRefresh()
			me.refreshTradingPlatform()
			window.inventorypanel.needsRefresh()

		setTimeout( =>
			for p in @products
				p.product.needsRefresh()
			window.inventorypanel.needsRefresh()
			@refreshTradingPlatform() 
		,300)

		# Set up the trading window to show all of the appropriate things:
		$('.tradingstage-interface .trading span.tradecount').each ->
			$(@).html "<span class='block'>&#9632;</span> x <span class='count'>0</span>"
			type = $(@).attr('data-production-type')
			color = player.products[type].color
			$(@).children('.block').css('color',color)
			$(@).hide()

		# Allow for clearing of the trading panel
		$('.trading').on "taphold", =>
			@clearTrades()

		$('.countdown').show()

		super

	ready: ->
		# Show the ready as GREEN instead of GRAY
		$('.ready').addClass('active')
		pycon.transaction 'ready'

	end: ->
		$('.countdown').hide()
		$('.ready').hide().unbind().removeClass('active')
		$('.tradingstage-interface').hide()
		$('.trading').unbind()
		$('.health').hide()
		$('.hunger').hide()
		$('.tradingstage-interface .inventory').sortable('destroy')
		if $('.placeholder').length > 0
			$('.placeholder').remove()
		@clearTrades()

		clearInterval interval for interval in @timers

		super

	# The bump function is called when the accelerometer detects a big
	# change of acceleration. 
	bump: ->
		# Assemble a list of items for the trade and ship them off
		items = {}
		for name,p of @products
			if p.for_trade > 0
				items[name] = p.for_trade

		pycon.transaction 'trade_proposed', { items:items }, (r) =>
			for name, p of @products
				p.for_trade = 0

			for name, amount of r.items
				@products[name].for_trade = amount

			window.inventorypanel.needsRefresh()
			@refreshTradingPlatform()

	# When somebody clears out the trading panel (for some reason) then
	# I'll refund whatever is in that panel to their list of things.
	clearTrades: ->
		for name,p of @products
			if p.for_trade > 0
				p.product.amount += p.for_trade
				p.for_trade = 0
				p.needsRefresh.call p

		@refreshTradingPlatform()
		window.inventorypanel.needsRefresh()

	# When a trade is finished (as judged by the server), it sends a message back
	# to pycon, which then calls this function. 
	trade_complete: (data) ->
		# Clear out what is in the trading panel right now.
		for name,p of @products
			p.for_trade = 0

		# Let the cards have a hay-day
		card.on_trade_end.call(card, data.items) for card in player.cards

		# Enter in the new data which was received during the trade.
		for name,amount of data.items
			if @products[name]?
				@products[name].for_trade = amount
				@products[name].needsRefresh.call @products[name]

		# Refresh everything in the trading panel.
		@refreshTradingPlatform()

	price_updated: ->
		for name,p of @products
			p.needsRefresh.call p

	products_updated: ->
		@price_updated()

	update: ->
		@price_updated()
		@refreshTradingPlatform()
		window.inventorypanel.needsRefresh()

	# This is called whenever there is some stale data relating to the trading
	# panel. This function will update the trading panel to have the new data.
	refreshTradingPlatform: ->
		for name,p of @products
			if p.for_trade > 0
				# Only show things that have non-zero values.
				$(".tradingstage-interface .tradecount[data-production-type='#{name}']").show().children('.count').html p.for_trade
			else 
				# Hide trading products that are zero.
				$(".tradingstage-interface .tradecount[data-production-type='#{name}']").hide()

	yield_production: ->
		for name,p of @products
			facility = player.productionfacilities[name]
			facility.run_factory.call facility
			p.needsRefresh.call p

		card.on_production.call card for card in player.cards

	timer_begin: (countdown) ->
			me = @
			# Record the time in the countdown.
			@time = countdown 
			count_down = ->
				# Count down.
				stage.time -= 1 if stage.time > 0
				# Draw to the screen.
				updateCountdown()
			
			# Wait one second before starting so that everything lines up.
			@timers.push setInterval count_down,1000
			updateCountdown()

class window.TradingProduct
	constructor: (@dom_element, @product) ->
		@needsRefresh()
		@for_trade = 0
		yes

	trade: ->
		if @product.amount > 0
			@for_trade += 1
			@product.amount -= 1
			@needsRefresh()
			window.inventorypanel.needsRefresh()
			stage.refreshTradingPlatform.call stage
			return yes
		else 
			return no

	sell: ->
		yes

	needsRefresh: ->
		yes