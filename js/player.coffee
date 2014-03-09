# The Player class is just a data interface for storing information about
# the current player, e.g. production capabilities, total gold, etc.

class window.Player
	constructor: ->
		# Initialize the production facilities
		@products = []
		@productionfacilities = []
		for p in [ 'bandage', 'food', 'bullet', 'point' ]
			@products[p] = new Product(p)

		@products['bandage'].color 		= '#DD514C'
		@products['food'].color 		= '#5EB95E'
		@products['bullet'].color 		= '#777'
		@products['point'].color 		= '#FAD232'

		@cards = []

		yes

	points: ->
		return @products['point'].amount

	getInventoryCount: ->
		inventory = {}
		for name,p of @products
			inventory[name] = p.amount
		return inventory

	givePoints: (amount) ->
		@products['point'].amount += amount
		point_string = Array(@products['point'].amount+1).join("&#9673;")
		$('.statusbar .points').html point_string


class window.Product
	constructor: (@name) ->
		@amount = 0
		@color = "green" 
		yes

class window.Job
	constructor: (@title, @color) ->
		yes

window.jobs = {}

jobs['hospital'] 	= new Job 'Hospital', '#DD514C'
jobs['production'] 	= new Job 'Production', '#FAD232'
jobs['farm']		= new Job 'Farm', '#5EB95E'
jobs['watchtower'] 	= new Job 'Watchtower', '#777'

window.player = new Player()