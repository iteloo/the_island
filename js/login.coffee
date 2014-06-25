class @LoginController
	constructor: ->
		@background = $("<div class='overlay login-background'><h3>Who are you?</h3><input value=name type=text /><br /><br /><div class='message-button'>OK</div></div>").show()

		@button = @background.children('.message-button')
		@input 	= @background.children('input')

		# Try to decode the cookie value.
		cookie = {}
		try 
			cookie = JSON.parse document.cookie
		catch err
			yes

		# Set the username, if we remember it.
		if cookie.username?
			@input.val cookie.username

		@button.tap =>
			@finish()

		$(".interface").append @background

	finish: ->
		# Destroy any evidence of the cookie
		document.cookie = name + '=; expires=Thu, 01-Jan-70 00:00:01 GMT;';
		# and then re-bake it.
		document.cookie = JSON.stringify { username: @input.val() }
		@background.remove()
		window.connectToGame()