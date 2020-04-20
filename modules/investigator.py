import praw
import json
from tqdm import tqdm

# read only bot
read_reddit = praw.Reddit('reader_bot')


def popular_subreddit_users(subreddit_name, n_users):
	
	karma_map = {}

	try:
		subreddit_submissions = read_reddit.subreddit(subreddit_name).top('hour', limit=10)
		for submission in tqdm(subreddit_submissions):

			if not karma_map.get(submission.author):
				karma_map[submission.author.name] = submission.score
			else:
				karma_map[submission.author.name] += submission.score

			# https://stackoverflow.com/questions/36366388/get-all-comments-from-a-specific-reddit-thread-in-python
			# WARNING potentially long running
			submission.comments.replace_more(limit=None)
			for comment in submission.comments:
				if not karma_map.get(comment.author):
					karma_map[comment.author.name] = comment.score
				else:
					karma_map[comment.author.name] += comment.score

		print(json.dumps(karma_map, indent=4))


	except Exception as e:
		print('popular_subreddit_users: something went wrong. ' + str(e))

	#retreive posts from top k hours. 
	#create k:user v:karma (from comments and posts) map across all posts.
	#return the top 

