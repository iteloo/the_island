# This function makes a nice-looking message pop up
# NO LONGER IN USE!

class window.Message
	constructor: ->
		@dom_selector = '.message'
		@timeout = 5
		@onclose = =>
			yes

	# An example of the options argument is something like: [ {text: "button text", callback: function() {} }, ... ]
	display: (title,text,clickable=true,options=[],duration=null) ->
		me = @

		$('.overlay').show()

		text = '' if !text? 
		title = '' if !title?
		
		$(@dom_selector).children('.title').html title
		$(@dom_selector).children('.text').html text
		$(@dom_selector).show()

		@dom_element = $(@dom_selector)

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
			$(@dom_selector).tap =>
				@close()
				@hide()

		# If necessary, use a timeout.
		if duration?
			setTimeout =>
				window.message.hide()
			, duration*1000


	respond: (response) ->
		yes

	# This is called when the message is clicked away. It is only possible
	# when the message is clickable.
	close: ->
		yes

	hide: ->
		@onclose()
		$(@dom_selector).unbind()
		$(@dom_selector).hide()
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


window.message = new Message()