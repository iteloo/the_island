class window.TestSuite
	constructor: ->
		@dom_element = $('.test-output')
		@passed = 0
		@test_count = Object.keys(tests).length
		window.onerror = =>
			@fail()
		@failed = no

	run: ->
		console.log "Starting TestSuite..."
		@passed = 0
		@test_keys = Object.keys(tests)
		@_run_next_test()

	_run_next_test: ->
		name = @test_keys.shift()
		# If we're out of tests, all tests pass.
		if !name?
			console.log "All tests passed."
			@dom_element.after "<h1>All tests passed.</h1>"
			@dom_element.css 'color', 'green'
			return

		test = window.tests[name]
		console.log "Running test '#{name}'..."
		try 
			throw "test '#{name}' returned invalid value" if !test(new TestDelegate @)
		catch err
			@failed = yes
			console.warn "Test '#{name}' failed with error '#{err}'"
			throw "Test suite ended due to failed test."

	pass: ->
		@passed++
		@report_state()
		@_run_next_test()

	fail: ->
		@report_state()
		@dom_element.after "<h1 style='color:red'>Test failed</h1>"

	report_state: ->
		@dom_element.html "#{@passed} / #{@test_count} tests passed."

class window.TestDelegate
	constructor: (@parent) ->
		yes

	pass: ->
		@parent.pass()
		yes

	fail: ->
		@parent.fail()
		no

window.assert = (statement, error) ->
	if !statement
		throw error
	else return true

window.tests = {
	'Connect to the host': (t) ->
		window.socket = new WebSocket("ws://" + location.host + "/json")
		socket.onopen = ->
			socket.close()
			t.pass()
		yes

	# This test will only pass if we connect to the game and receive
	# a "stage begin" command.
	'Start socket, and observe stage_begin': (t) ->
		window.socket = new WebSocket("ws://" + location.host + "/json")
		socket.onopen = ->
			window.pycon = new PyAPI window.socket
			# Only let them pass the test when we receive a "stage begin"
			# message.
			pycon.register_for_event 'stage_begin', (data, responder) ->
				responder.respond()
				# Let the stage set itself up and so forth before we
				# execute the actual pass.
				setTimeout ->
					t.pass()
				,250
			# Initialize the level, do all registrations for
			# different messages, etc.
			window.go()
		yes

	# Update the health bars, inventory, etc.
	'Test: update_player_info': (t) ->
		# The following format comes from the description on 
		# https://github.com/iteloo/the_island/wiki/update_player_info
		m = {
			method: 'update_player_info',
			args: {
				inventory: {
					bandage: Math.round( Math.random() * 100 ),
					food: Math.round( Math.random() * 100 ),
					bullet: Math.round( Math.random() * 100 )
					log: Math.round( Math.random() * 100 )
				},
				condition: {
					health: Math.round( Math.random() * 100 )
					antihunger: Math.round( Math.random() * 100 )
				}
			}
		}
		# Invoke a fake message according to the above format.
		pycon.onmessage {data: JSON.stringify m } 
		# Test that everything loaded.
		assert player.products.bandage.amount == m.args.inventory.bandage, "Failed inventory update"
		assert player.products.food.amount == m.args.inventory.food, "Failed inventory update"
		assert player.products.bullet.amount == m.args.inventory.bullet, "Failed inventory update"
		assert player.products.log.amount == m.args.inventory.log, "Failed inventory update"
		assert player.health == m.args.condition.health, "Failed condition:health update"
		assert player.food == m.args.condition.antihunger, "Failed condition:antihunger update"
		# Well, they must have passed the test.
		t.pass()

}