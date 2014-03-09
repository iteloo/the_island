import stage
import helpers

class JobStage(stage.Stage):
	stageType = 'Job'

	def __init__(self, game):
		super(JobStage, self).__init__(game)
		self.readyList = []

	@classmethod
	def title(self):
		return "Select your Job"

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
	def afterBegin(self):
		super(JobStage, self).afterBegin()
		amount = dict((j, len(p)) for j,p in self.game.playersWithJob)
		self.sendEventToAllPlayers(player, 'GivePoints', {'amount':amount})

=======
>>>>>>> dbb6788... some fixes to production and cleaned up trading
	def end(self):
		# record production in game
		self.game.playersWithJob = self.playersWithJob()
		super(JobStage, self).end()

=======
>>>>>>> 2efd8db... untested trading, revamp, etc
	#### action handling ####

>>>>>>> c7b69e5... added untested production stage
	def selectJob(self, sender, data):
		try:
			sender.currentJob = data['jobSelected']
		except KeyError:
			return helpers.errorMessageActionDataKeyError(self, 'jobSelected')

<<<<<<< HEAD
<<<<<<< HEAD
		self.jobsSelected[sender] = jobSelected
=======
		# record selection
		self.jobSelectedWithPlayer[sender] = jobSelected

=======
>>>>>>> c7b69e5... added untested production stage
		# notify players
		self.game.sendEventToAllPlayers('JobSelectionUpdated', {'playersWithJob':playerIdsWithJob()})

		return {}
>>>>>>> c82c7ac... still working on jobs

	def ready(self, sender):
		if sender:
			# add player to readyList
			self.readyList.append(sender)
			# if all players are ready, move the to the next stage
			if all([p in self.readyList for p in self.game.players]):
				self.canEnd()

		return {}
<<<<<<< HEAD
=======

	#### convenience ####
	def playerIdsWithJob(self):
<<<<<<< HEAD
		return dict((job, [p.id for p,j in self.jobSelectedWithPlayer.iteritems() if j==job]) for job in self.game.jobs)
<<<<<<< HEAD
>>>>>>> c82c7ac... still working on jobs
=======

	def playersWithJob(self):
		return dict((job, [p for p,j in self.jobSelectedWithPlayer.iteritems() if j==job]) for job in self.game.jobs)
=======
		dict((job, [p.id for p in self.game.playersWithJob(job)]) for job in self.game.job)
>>>>>>> 2efd8db... untested trading, revamp, etc

	#### player handling ####

	def handleAddPlayer(self, newPlayer):
		super(JobStage, self).handleAddPlayer(newPlayer)
		# update new player's data
		self.game.sendEventToPlayer(newPlayer, 'JobSelectionUpdated', {'playersWithJob':self.playerIdsWithJob()})

	def handleRemovePlayer(self, playerRemoved):
		super(JobStage, self).handleRemovePlayer(playerRemoved)
<<<<<<< HEAD
		# remove from data
		self.jobSelectedWithPlayer.pop(playerRemoved, None)
<<<<<<< HEAD
>>>>>>> a69a79e... added handler for player add/remove to job stage
=======
=======
>>>>>>> 2efd8db... untested trading, revamp, etc
		# update everyone else's data
		self.game.sendEventToAllPlayers('JobSelectionUpdated', {'playersWithJob':self.playerIdsWithJob()})

>>>>>>> c7b69e5... added untested production stage
