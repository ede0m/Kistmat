import praw
import json
from threading import Thread

# read only bot
read_reddit = praw.Reddit('reader_bot')

def investigator_prompt():

	choice = input('\noptions:\n 1. active subreddit targets\n\nselect: ')
	
	# active subreddit users
	if choice == '1':
		subreddit = input('enter subreddit name: \t')
		n_user_limit = input('limit returned users: \t')
		if not n_user_limit.isdigit():
			print('error: returned users must be a number')
		n_post_limit = input('limit posts to analyze: ')
		if not n_post_limit.isdigit():
			print('error: posts limit must be a number')

		t = Thread(target=active_subreddit_users, args=(subreddit, float(n_user_limit), float(n_post_limit)))
		t.start()
	
	else:
		print('error: option not supported')


def active_subreddit_users(subreddit_name, n_user_limit, n_post_limit):
	
	karma_map = {}

	try:
		subreddit_submissions = read_reddit.subreddit(subreddit_name).top('hour', limit=n_post_limit)
		for submission in subreddit_submissions:

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
				karma_map[submission.author.name]['n_interactions'] += 1

			# https://stackoverflow.com/questions/36366388/get-all-comments-from-a-specific-reddit-thread-in-python
			# WARNING potentially long running
			submission.comments.replace_more(limit=None)
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
					karma_map[comment.author.name]['karma'] += comment.score
					karma_map[comment.author.name]['interactions'] += comment.score

		# sort dict by active desc
		sorted_active_users = sorted(karma_map.items(), key=lambda t : t[1]['karma'], reverse=True)
		for k,v in sorted_active_users:
			print(k+': \n'+json.dumps(v, indent=4)+'\n\n')


	except Exception as e:
		print('active_subreddit_users: something went wrong. ' + str(e) + '\n')



