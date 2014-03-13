# This class handles communication with the Python
# WebSocket server that is running on the local
# machine, and interfaces communication between the two.

# You shouldn't start the PyAPI without first having a valid, connected
# socket going. So check that first, then make a PyAPI around it.
class @PyAPI
	constructor: (@socket = null) ->
		# In case the socket is null, we'll use the
		# globally-accessible socket.
		@socket = window.socket if !@socket?
		@response_handlers = []
		@event_responders = []

		# Connect this PyAPI class to the onmessage
		# event for the socket.
		me = @
		@socket.onmessage = (message) ->
			me.onmessage.call me, message

		# Verify the server version using this method.
		@transaction 'server_info', {} , (data) ->
			console.log "Attempted version validation. Received response:"
			console.log data
			throw "VERSION_ERROR: Invalid reported server version #{data.version}. Expecting #{window.config.server_version}" if data.version != window.config.server_version
	
 	# This function is called whenever a message is received
 	# by the socket. It checks if the message matches the transaction
 	# pattern, and if so, handles it appropriately.
	onmessage: (message) ->
		#window.message = JSON.parse message 
		#if !(typeof yourVariable === 'object')
		# If the mssage has a transaction ID, and there is a callback
		message = JSON.parse message.data
		if !message.method?
			throw "Received illegal message '#{JSON.stringify message}' without method header."
		else if message.method == "handle_callback"
			if !@response_handlers[ message.args.callback_id ]?
				throw "Received illegal callback ID in a handle_callback response."
			# Call the response function.
			console.log 'Received callback with arguments: ', message.args
			@response_handlers[ message.args.callback_id ].call @, message.args.callback_args
		else
			# This must be a method call.
			console.log 'Received method call: ', message.method
			console.log 'Method call data: ', message.args
			@trigger_event message.method, message.args

	# This function generates a transaction ID, based upon the current time.
	generate_transaction_id: (message) ->
		# For now, we just use a random number. But this introduces
		# random behavior - it might be better to use a hashing algorithm
		# in the future. Returns a string.
		return "T" + Math.random()

	# Register for an event using this function, to hear when the computer
	# tells you something global. But you can't respond to it.
	register_for_event: (eventName, response) ->
		if !@event_responders[eventName]?
			@event_responders[eventName] = []
		@event_responders[eventName].push response 

	# When an event comes in, this function executes all of the listeners.
	trigger_event: (eventName, data) ->
		if @event_responders[eventName]?
			for e in @event_responders[eventName]
				# If we are supposed to return their call, this method will do that.
				if data.callback_id? 
					response = e.call(window, data, new PyAPIResponder(data.callback_id,@))
				else 
					e.call(window,data, new PyAPIDummyResponder())

	# This function executes a transaction by transmitting a message, then waiting for 
	# a response, then executing the responder function on the response.
	transaction: (method_name, args, responder=null) ->
		# First, generate a transaction ID that we can use later when 
		# we receive a response from the system. 

		# Follow the specifications for the transmission (https://github.com/iteloo/the_island/wiki/Server-client-interface)
		transmission = {
			method: method_name
			args: args
		}

		# If we care about a reponse, we must include a responder function. 
		# Then we'll generate a transaction ID to listen for a response on.
		if responder?
			transaction_id = @generate_transaction_id(message)
			# Add the "callback_id" parameter to the message
			transmission.args.callback_id = transaction_id
			# Register the responder in the responders database
			@response_handlers[ transaction_id ] = (response) ->
				responder.call( @, response )

		# Send out the actual data, and wait for the response! (actually this is 
	 	# asynchronous so we don't wait)
		@socket.send( JSON.stringify transmission )
		console.log 'Transaction sent: ', JSON.stringify(transmission)

	# This function closes and opens the socket connection, which 
	# "re-jiggles" the connection and starts things over. 
	reconnectWithSocket: (new_socket) ->
		@socket.close()
		@socket = new_socket

# This is the responder object. Event handlers will receive an instance
# of this object, which they can use to make a repsonse. It is intended
# to be used with asynchronous responses.
class @PyAPIResponder
	constructor: (@callback_id, @parent) ->
		yes

	respond: (response) ->
		@parent.transaction 'handle_callback', {
				callback_id: @callback_id
				callback_args: response
		}
		yes

class @PyAPIDummyResponder extends PyAPIResponder
	respond: ->
		yes