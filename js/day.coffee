class window.DayStage extends Stage
	constructor: ->
		@dom_element = $("<div class='wait'><h3>Waiting for everyone else...</h3></div>")
		$(".interface").append @dom_element

	end: ->
		@dom_element.remove()