# This function makes a nice-looking message pop up
# NO LONGER IN USE!

class window.Message
	constructor: ->
		# Create the element
		@dom_element = $("<div class='message' data-role='page'><h3 class='title'></h3><p class='text'></p><div class='message-inputs'></div><div class='message-buttons'></div></div>")		
		@timeout = 5
		@onclose = =>
			yes

	# An example of the options argument is something like: [ {text: "button text", callback: function() {} }, ... ]
	display: (title,text,clickable=true,options=[],inputs=[],duration=null) ->
		me = @

		$(".interface").append @dom_element
		$('.overlay').show()

		text = '' if !text? 
		title = '' if !title?
		
		@dom_element.children('.title').html title
		@dom_element.children('.text').html text
		@dom_element.show()

			# Now let's handle the inputs. Each input is like, a text box or whatever.
		@inputs = {}
		if inputs? && inputs.length > 0
			for i in inputs
				if i.id? && i.type == "textbox"
					@inputs[i.id] = $("<input type=text class='message-input message-input-textbox' />")

		# Throw all supported inputs into the loop.
		@dom_element.children('.message-inputs').html ""
		for k,i of @inputs
			@dom_element.children('.message-inputs').append i

		# Now consider whether we need buttons.
		@buttons = []
		# Clear out the list of buttons
		@dom_element.children('.message-buttons').html ''
		if options? && options.length > 0
			for o in options
				if !o.display? || o.display == "button"
					@buttons.push new MessageButton(@, o.text, o.id)
		
		# Now set up click events.
		if clickable
			@dom_element.tap =>
				@close()
				@hide()
				@destroy

		# If necessary, use a timeout.
		if duration?
			setTimeout =>
				window.message.hide()
			, duration*1000

		# Make the inventory screen disappear if it's open
		window.inventorypanel.close()


	# This function returns the state of all existing inputs.
	input_states: ->
		state = {}
		for k,i of @inputs
			state[k] = i.val()
		return state

	respond: (response) ->
		yes

	# This is called when the message is clicked away. It is only possible
	# when the message is clickable.
	close: ->
		yes

	destroy: ->
		@dom_element.remove()

	hide: ->
		@onclose()
		@dom_element.unbind()
		@dom_element.hide()
		$('.overlay').hide()

# The message buttons are created whenever a message has button options.
class @MessageButton
	constructor: (@parent, @text, @id) ->
		@dom_element = $("<div class='message-button'>#{@text}</div>")
		
		#@dom_element.click =>
		#	@click()
		@dom_element.tap =>
			@click()

		@parent.dom_element.children(".message-buttons").append @dom_element

	click: ->
		@parent.respond @id
		@parent.hide()