class window.ProductionStage extends Stage
	constructor: ->
		me=@

		@jobs = {}

		$('.ready').show()

		$('.ready').tap ->
			me.ready.call me

		# Show the interface
		$('.productionstage-interface').show()

		# Register the jobs: one for each production
		$('.productionstage-interface .box').each ->
			jobcode = $(@).attr 'data-job-type'
			me.jobs[jobcode] = new ProductionView( $(@) )

		$('.productionstage-interface .box').fitText 1, { maxFontSize: '40px'}
			
		yes

	ready: ->
		# We can only be ready if all points have been spent.
		if player.points() == 0
			# Show the ready as GREEN instead of GRAY
			$('.ready').addClass('active')

			@report_production()

			pycon.transaction { 'action': 'ready' }, ->
				yes

	end: ->
		# Destroy all of the jobviews
		j.end.call j for name,job in @jobs
		$('.ready').hide().unbind().removeClass('active')
		$('.productionstage-interface').hide()

	report_production: ->
		production = {}
		production[name] = job.number_points for name,job of @jobs
		pycon.transaction { action: 'updatePoints', data: { production:production }}

	job_selection_updated: (data) ->
		for job,players of data.playersWithJob
			console.log '==> ', job, ' with players ', players
			@jobs[job].number_players = players.length
			@jobs[job].needsRefresh.call @jobs[job]

class window.ProductionView 
	constructor: (@dom_object) ->
		me=@

		@job = window.jobs[@dom_object.attr('data-job-type')]
		@job_code = @dom_object.attr('data-job-type')

		@dom_object.css 'background-color', @job.color 
		
		@number_points = 0

		@dom_object.tap ->
			me.tap.call me

		@dom_object.taphold ->
			me.tapHold.call me

		@needsRefresh()

	tap: ->
		if player.points() > 0
			@number_points += 1
			player.givePoints -1
			@needsRefresh()

	tapHold: ->
		player.givePoints @number_points
		@number_points = 0
		@needsRefresh()

	needsRefresh : ->
		@dom_object.html ''
		@dom_object.append $("<h3>#{@job.title}</h3>")
		point_string = Array(@number_points+1).join("&#9673;")
		@dom_object.append $("<p>#{point_string}</p>")

	end: ->
		@dom_object.unbind()