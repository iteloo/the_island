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


# Prevent actual execution of the script
# when in testing mode.
if TEST? and TEST == yes 
	$ ->
		console.log "Initializing testing mode."
		t = new TestSuite()
		t.run()
else # Initialization of everything.
	$ ->
		window.login_controller = new LoginController()

window.connectToGame = ->
 	# First step: connect to the specified WebSocket
 	# server.
 	window.socket = new WebSocket("ws://" + location.host + "/json")
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
 		m = new Message()
 		m.display "Oh No!", "I don't know why, but the socket was closed (!)"

# When everything is loaded and ready to go, this function is called.
window.go = ->
	# We must send the name according to the ancient tradition of the logincontroller
	pycon.transaction 'name_entered', { name: login_controller.input.val() }
	# When the player count changes we need to update the status bar.
	pycon.register_for_event 'update_game_info', (data) ->
		console.log 'Player count changed: ', data
		$('.playercount').html(data.player_count)

	# When the program starts, the server will issue a "stageBegin" to me
	# to indicate the current stage. Here's where I register for that.
	pycon.register_for_event 'stage_begin', (data, responder) ->
		#window.stage = new TradingStage()
		#return false
		if stage? 
			window.stage.end()
		if data.stage_type == 'Job'
			window.stage = new JobStage()
		else if data.stage_type == 'Day'
			window.stage = new DayStage()
		else if data.stage_type == 'Production'
			window.stage = new ProductionStage()
		else if data.stage_type == 'Notification'
			window.stage = new NotificationStage()
		else if data.stage_type == 'Trading'
			window.stage = new TradingStage()
		else
			throw "Illegal stage sent: #{data.stageType}"

		#  Tell the server that we have loaded the stage.
		responder.respond()

	# The 'update_player_info' method updates the inventory and 
	# status of the player.
	pycon.register_for_event 'update_player_info', (data) ->
		# Load up all of the data.
		for name,amount of data.inventory
			if window.stage? and window.stage instanceof TradingStage
				player.products[name].amount = amount - window.stage.products[name].for_trade
			else
				player.products[name].amount = amount

		# Set the condition
		if data.condition?
			player.setHealth(data.condition.health) if data.condition.health?
			player.setFood(data.condition.antihunger) if data.condition.antihunger?

		# Tell the stage to update
		stage.update() if stage?
		window.inventorypanel.needsRefresh()
		window.updateInterface()
		
	# Is it possible
	pycon.register_for_event 'display_event', (data, responder) ->
		data.clickable = no if !data.clickable?
		options = []
		if data.responses?
			options = data.responses

		inputs = []
		if data.inputs?
			inputs = data.inputs

		m = new Message()

		for o in options
			if o.display? && o.display == "background"
				m.close = =>
					responder.respond { response_chosen_id: o.id }
				data.clickable = yes
				break

		m.respond = (response) =>
			responder.respond { response_chosen_id: response, inputs: m.input_states() } 

		m.display data.title, data.text, data.clickable, options, inputs

	pycon.register_for_event 'InventoryCountRequested', (data) ->
		pycon.transaction {action: data.callback, data: player.getInventoryCount.call player }

	pycon.register_for_event 'update_job_selections', (data) ->
		stage.update_job_selections.call(stage,data) if stage.update_job_selections? 

	pycon.register_for_event 'echo', (data, responder) ->
		responder.respond(data)

	pycon.register_for_event 'GivePoints', (data) ->
		player.givePoints data.amount

	# If somebody sends a message to refresh, dutifully refresh.
	pycon.register_for_event 'refresh', (data) ->
		location.reload 0

	# Begin the timer? We just pass this directly into the stage.
	pycon.register_for_event 'TimerBegin', (data) ->
		console.log 'Event handled: ',stage
		stage.timer_begin.call stage, data.duration

	# Report production
	pycon.register_for_event 'RequestProductionReport', (data) ->
		stage.report_production() if stage.report_production?

	# We need to exercise the connection or else it goes stale. So this will keep
	# the connection alive.
	setInterval =>
		pycon.transaction 'echo', { }, =>
			yes
	,20000

	updateStatusBar()
	$('.statusbar').show()

	window.inventorypanel = new InventoryPanel()