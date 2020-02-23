
class Target:

	def __init__(self, reddit, name, options):
		self.read_reddit = reddit
		self.redditor = self.read_reddit.redditor(name)
		self.name = self.redditor.name
		self.vote_direction = options['vote_direction']
		self.vote_comments = options['comments']
		self.vote_submissions = options['submissions']
		self.options = options

	def comments(self):
		return self.redditor.comments.new(limit=50) 

	def submissions(self):
		return self.redditor.submissions.new(limit=10)

	def comment_karma(self):
		return self.redditor.comment_karma

	def link_karma(self):
		return self.redditor.link_karma

	def update(self):
		# does this work??
		self.redditor = self.read_reddit.redditor(self.name)


