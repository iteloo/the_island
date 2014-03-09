# Configuration parameters:
# they are now pulled from a configuration.json file.
# -------------------------------------- #

window.config = $.ajax({
    type: "GET",
    url: "/configuration.json",
    async: false
}).responseText

try 
	window.config = JSON.parse window.config
catch error
	throw "Configuration loaded from 'configuration.json' is invalid."

# -------------------------------------- #`

$ ->
 	# First step: connect to the specified WebSocket
 	# server.

 	window.socket = new WebSocket( window.config.websocket_url )
 	# Get ready for when the socket opens
 	window.jevent 'SocketOpened', ->
		console.log 'The socket was opened.'

 	# This function is called only when the socket is opened. 
 	socket.onopen = ->
 		console.log "Socket connection opened successfully."
 		window.pycon = new PyAPI window.socket

 		window.go()
 		
 	# Since the socket should never close, this is always unexpected.
 	socket.onclose = ->
 		console.log "Socket connection was closed, unexpectedly."
 		window.message.display "Oh No!", "I don't know why, but the socket was closed (!)"

# When everything is loaded and ready to go, this function is called.
window.go = ->
	# When the player count changes we need to update the status bar.
	pycon.register_for_event 'playerCountChanged', (data) ->
		console.log 'Player count changed: ', data
		$('.playercount').html data.count 

	# When the program starts, the server will issue a "stageBegin" to me
	# to indicate the current stage. Here's where I register for that.
	pycon.register_for_event 'stageBegin', (data) ->
		#window.stage = new TradingStage()
		#return false
		if stage? 
			window.stage.end()
		if data.stageType == 'Job'
			window.stage = new JobStage()
		else if data.stageType == 'Production'
			window.stage = new ProductionStage()
		else if data.stageType == 'Notification'
			window.stage = new NotificationStage()
		else if data.stageType == 'Trading'
			window.stage = new TradingStage()
		else
			throw "Illegal stage sent: #{data.stageType}"

	# When a trade is found to be completed with somebody, then we
	# need to inform the current stage so that it can do what it likes
	# with that information.
	pycon.register_for_event 'TradeCompleted', (data) ->
		if stage?
			window.stage.trade_complete.call stage,data
		else 
			console.log 'Received illegal trade...?'

	# Is it possible
	pycon.register_for_event 'DisplayMessage', (data) ->
		data.clickable = yes if !data.clickable?
		message.display.call message,data.title, data.text, data.clickable

	pycon.register_for_event 'InventoryCountRequested', (data) ->
		pycon.transaction {action: data.callback, data: player.getInventoryCount.call player }

	pycon.register_for_event 'JobSelectionUpdated', (data) ->
		stage.job_selection_updated.call(stage,data) if stage.job_selection_updated?

	pycon.register_for_event 'GivePoints', (data) ->
		player.givePoints data.amount

	# Begin the timer? We just pass this directly into the stage.
	pycon.register_for_event 'TimerBegin', (data) ->
		console.log 'Event handled: ',stage
		stage.timer_begin.call stage, data.duration

	# Report production
	pycon.register_for_event 'RequestProductionReport', (data) ->
		stage.report_production() if stage.report_production?

	updateStatusBar()