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
		name = @test_keys.pop()
		# If we're out of tests, all tests pass.
		if !name?
			console.log "All tests passed."
			@dom_element.after "<h1>All tests passed.</h1>"
			@dom_element.css 'color', 'green'
			return

		test = window.tests[name]
		console.log "Running test '#{name}'..."
		try 
			throw "failure" if !test(new TestDelegate @)
		catch err
			@failed = yes
			console.warn "Test '#{name}' failed with error #{err}"
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
	'Start socket, and start game': (t) ->
		window.socket = new WebSocket("ws://" + location.host + "/json")
		socket.onopen = ->
			window.pycon = new PyAPI window.socket
			pycon.register_for_event 'stage_begin', (data, responder) ->
				responder.respond()
				t.pass()
}