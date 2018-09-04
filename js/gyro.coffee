
$ ->	
	window.acc = {x:0, y:0, z:0}
	window.avg_acc = false
	moving_average_samples = 50
	window.censor_gyroscope = false 

	window.ondevicemotion = (e) ->

		x = e.accelerationIncludingGravity.x
		y = e.accelerationIncludingGravity.y
		z = e.accelerationIncludingGravity.z

		change = Math.abs(acc.x-x) + Math.abs(acc.y-y) + Math.abs(acc.z-z)

		window.acc = {x:x, y:y, z:z}

		if change > 20 and !window.censor_gyroscope
			window.censor_gyroscope = true
			
			window.stage.bump.call window.stage
			
			setTimeout( ->
				window.censor_gyroscope = false
			,500) 
