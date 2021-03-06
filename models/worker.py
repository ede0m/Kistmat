from datetime import datetime, timedelta
from time import sleep
from random import randrange

class Worker:

	def __init__(self, reddit, name, interacted_with=set(), targets={}):
		self.worker_instance = reddit
		self.interacted_with = interacted_with
		self.targets = targets
		self.name = name
		self.random_vote_sleep_max_sec = 0

	def run_worker(self):
		details = ''
		for t in self.targets.values():
			details += self.__vote_flood(t)
		return details

	def update_instance(self, reddit):
		self.worker_instance = reddit

	def set_vote_sleep_max_sec(self, sec):
		self.random_vote_sleep_max_sec = float(sec)

	def __vote_flood(self, target):

		details = ''
		comments_success = True
		submissions_success = True
		# this worker takes control of this target
		target.update(self.worker_instance) # TODO: doesn't seem to update the karma values on redditor
		try:

			if target.vote_comments:
				n_c_voted = self.__try_vote_set(target.comments(), target.vote_direction)
		except Exception as e:
			error = '\nsomething went wrong with comments for '+self.name+' - ' + str(e)
			comments_success = False
			details += error
		
		try:
			if target.vote_submissions:
				n_p_voted = self.__try_vote_set(target.submissions(), target.vote_direction)
		except Exception as e:
			error = '\nsomething went wrong with submissions for '+self.name+' - ' + str(e)
			submissions_success = False
			details += error

		
		dir_str = 'UP' if target.vote_direction == 1 else 'DOWN'
		dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		if comments_success:
			details += '\n'+dt+' - '+self.name+' voted ' +dir_str+' on '+str(n_c_voted)+' comments by ' + target.name +' ['+str(target.comment_karma())+']'
		if submissions_success:
			details += '\n'+dt+' - '+self.name+' voted ' +dir_str+' on '+str(n_p_voted)+' submissions by ' + target.name +' ['+str(target.link_karma())+']'
		
		return details + '\n'
	
	def __try_vote_set(self, p_set, v_direction):
		
		n_voted = 0
		for p in p_set:

			# cannot vote after 6 months (180 days)
			created_date = datetime.utcfromtimestamp(p.created_utc)
			now = datetime.utcnow()
			expired = (now-created_date) > timedelta(180)
			if p.id not in self.interacted_with and not expired:
				
				if self.random_vote_sleep_max_sec > 0:
					sleep(randrange(0, self.random_vote_sleep_max_sec))

				self.__vote(p, v_direction)
				n_voted += 1

		return n_voted

	def __vote(self, post, v_direction):
		
		if v_direction == 1:
			post.upvote()
		else:
			post.downvote()

		self.interacted_with.add(post.id)


