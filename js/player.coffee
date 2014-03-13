# The Player class is just a data interface for storing information about
# the current player, e.g. production capabilities, total gold, etc.

class window.Player
	constructor: ->
		# Initialize the production facilities
		@products = []
		@health = 100
		@food 	= 100
		@productionfacilities = []
		for p in [ 'bandage', 'food', 'bullet', 'log' ]
			@products[p] = new Product(p)

		@products['bandage'].color 		= '#DD514C'
		@products['food'].color 		= '#5EB95E'
		@products['bullet'].color 		= '#777'
		@products['log'].color 			= '#FAD232'

		yes

	getInventoryCount: ->
		inventory = {}
		for name,p of @products
			inventory[name] = p.amount
		return inventory

	update: ->
		@setHealth @health
		@setFood @food

	setHealth: (amount) ->
		if (amount) < 100
			@health = amount
		else 
			@health = 100
		health_points = Math.ceil(@health / 34.0)
		health_string = Array(health_points+1).join("&#9829;") + Array(4-health_points).join("&#9825;")
		$('.statusbar .health').html health_string

	setFood: (amount) ->
		if amount < 100
			@food = amount
		else 
			@food = 100
		food_points = Math.ceil(@food / 33.0)
		food_string = Array(food_points+1).join("<span class='food'>&nbsp;&nbsp;&nbsp;</span>") + Array(3-food_points+1).join("<span class='anti food'>&nbsp;&nbsp;&nbsp;</span>")
		$('.statusbar .hunger').html food_string

class window.Product
	constructor: (@name) ->
		@amount = 0
		@color = "green" 
		yes

	activate: ->
		# Tell the server that we activated the item.
		pycon.transaction 'item_activated', { item_name: @name }

class window.Bandage extends Product

class window.Food extends Product

class window.Job
	constructor: (@title, @color) ->
		yes

window.jobs = {}

jobs['hospital'] 	= new Job 'Hospital', '#DD514C'
jobs['production'] 	= new Job 'Production', '#FAD232'
jobs['farm']		= new Job 'Farm', '#5EB95E'
jobs['watchtower'] 	= new Job 'Watchtower', '#777'

window.player = new Player()