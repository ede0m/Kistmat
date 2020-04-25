import json
from threading import Thread
from datetime import datetime

class TargetInvestigation:

	def __init__(self, read_reddit):
		self.read_reddit = read_reddit
		self.progress = 0
		self.name = ''
		self.timestamp_start = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
		self.__run_target_investigation()

	def __run_target_investigation(self):

		choice = input('\noptions:\n1. active subreddit targets\n\nselect: ')
		
		# active subreddit users prompt
		if choice == '1':
			subreddit = input('enter subreddit name: \t')
			n_user_limit = input('limit returned users: \t')
			if not n_user_limit.isdigit():
				print('error: returned users must be a number')
			n_post_limit = input('limit posts to analyze: ')
			if not n_post_limit.isdigit():
				print('error: posts limit must be a number')
			time_filter = input('enter post time filter: ')
			if time_filter not in ['all', 'day', 'hour', 'month', 'week', 'year']:
				print('error: invalid time filter. Must be one of the following: (all, day, hour, month, week, year)')
			more_comments_replace_limit = input('more-comments replace limit: ')
			if not more_comments_replace_limit.isdigit():
				print('error: more-comments replace limit must be a number')

			self.name = 'active_'+subreddit+'_top_'+time_filter+'_'+self.timestamp_start

			print('\n')
			t = Thread(target=self.__active_subreddit_users, args=(subreddit, float(n_user_limit), float(n_post_limit), time_filter, float(more_comments_replace_limit)))
			t.start()
		else:
			print('error: option not supported')


	def __active_subreddit_users(self, subreddit_name, n_user_limit, n_post_limit, time_filter, more_comments_replace_limit):
		
		karma_map = {}
		posts_processed = 0
		try:
			subreddit_submissions = self.read_reddit.subreddit(subreddit_name).top(time_filter, limit=n_post_limit)
			for submission in subreddit_submissions:
				posts_processed += 1
				# author can be deleted
				if not submission.author:
						continue

				if not karma_map.get(submission.author):
					karma_map[submission.author.name] = {
						'karma' : submission.score,
						'interactions' : 1
					}
				else:
					karma_map[submission.author.name]['karma'] += submission.score
					karma_map[submission.author.name]['interactions'] += 1

				# https://stackoverflow.com/questions/36366388/get-all-comments-from-a-specific-reddit-thread-in-python
				# WARNING potentially long running
				submission.comments.replace_more(limit=more_comments_replace_limit) # "limit=None" will replace all moreComments with its comments (LONG RUNNING)
				for comment in submission.comments.list():
					# author can be deleted
					if not comment.author:
						continue

					if not karma_map.get(comment.author):
						karma_map[comment.author.name] = {
							'karma' : comment.score,
							'interactions' : 1
						}
					else:
						print('HERE ADDING')
						karma_map[comment.author.name]['karma'] += comment.score
						karma_map[comment.author.name]['interactions'] += 1
				
				self.progress = posts_processed / n_post_limit * 100

			# sort dict by active desc and format for persistence
			sorted_active_users = sorted(karma_map.items(), key=lambda t : t[1]['karma'], reverse=True)
			sorted_filtered_active_users = {}
			n_users = 0
			for k,v in sorted_active_users:
				if v['interactions'] == 1 and v['karma'] == 1:
					continue
				sorted_filtered_active_users[k] = v
				n_users += 1
				if n_users >= n_user_limit:
					break
			report = {
				'timestamp' : self.timestamp_start,
				'subreddit' : subreddit_name,
				'n_posts_analyzed' : n_post_limit,
				'top_time_filter' : time_filter,
				'active_users' : sorted_filtered_active_users
			}
			self.__write_investigation_report(report, self.name)

		except Exception as e:
			print('active_subreddit_users: something went wrong. ' + str(e) + '\n')


	def __write_investigation_report(self, report, filename):
		with open('investigations/'+filename, 'w', encoding='utf-8') as f:
			json.dump(report, f, ensure_ascii=False, indent=4)
			print('\ninvestigation for active: ' + self.name + ' finished successfully\n')




