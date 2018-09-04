class window.JobStage extends Stage
	constructor: ->
		me=@

		@jobs = {}

		$('.ready').show()

		$('.ready').tap =>
			@ready()

		# Show the interface
		$('.jobstage-interface').show()

		# Register the jobs: one for each production
		$('.jobstage-interface .box').each ->
			jobcode = $(@).attr 'data-job-type'
			me.jobs[jobcode] = new JobView( $(@) )

		$('.jobstage-interface .box').fitText 1, { maxFontSize: '40px'}
			
		yes

	ready: ->
		# We can only be ready if a selection has been made.
		if @getSelectedJob()
			# Show the ready as GREEN instead of GRAY
			$('.ready').addClass('active')
			pycon.transaction 'ready'

	getSelectedJob: ->
		for name,job of @jobs
			return job if job.selected
		return no

	end: ->
		$('.jobstage-interface').hide()
		$('.ready').hide().unbind().removeClass('active')
		# Destroy all of the jobviews
		j.end.call j for name,job in @jobs
		$('.ready').hide().unbind()

	update_job_selections: (data) ->
		for job,players of data.job_selections
			console.log '==> ', job, ' with players ', players
			@jobs[job].number_players = players.length
			@jobs[job].needsRefresh.call @jobs[job]

class window.JobView 
	constructor: (@dom_object) ->
		me=@

		@job = window.jobs[@dom_object.attr('data-job-type')]
		@job_code = @dom_object.attr('data-job-type')

		@dom_object.css 'background-color', @job.color 
		@selected = no
		@number_players = 0

		@dom_object.tap ->
			me.tap.call me

		@needsRefresh()

	select: ->
		job.unselect.call(job) for q,job of window.stage.jobs
		@selected = yes
		pycon.transaction 'job_selected', { job: @job_code }
		@needsRefresh()

	unselect: ->
		@selected = no
		@needsRefresh()

	tap: ->
		if @selected
			#@unselect()
		else
			@select()

	needsRefresh : ->

		@dom_object.html ''
		@dom_object.append $("<h3>#{@job.title}</h3>")
		player_string = Array(@number_players+1).join("&#9679;")
		@dom_object.append $("<p>#{player_string}</p>")

		if !@selected
			@dom_object.css('opacity','0.5')
		else
			@dom_object.css('opacity','1')

	end: ->
		@dom_object.unbind()