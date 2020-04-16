from threading import Thread, Timer

class Schedule:

	def __init__(self, name, freq, workers = {}):
		self.__timer = None
		self.__freq = freq * 60
		self.name = name
		self.workers = workers
		self.running = False
		self.log = ''

	def __run_workers(self):
		details = '\n\n- report for schedule: '+self.name+' -\n'
		for w in self.workers.values():
			new_details = w.run_worker()
			details += new_details
			self.log += new_details
		print(details)

	def __run_schedule(self):
		try:
			self.__run_workers()
		except Exception as e:
			self.running = False
			raise e

		self.__timer = Timer(self.__freq, self.__run_schedule)
		self.__timer.start()

	def get_freq(self):
		return self.__freq / 60

	def update_freq(self, freq):
		self.__freq = freq * 60

	def add_worker(self, w):
		self.workers[w.name] = w

	def remove_worker(self, w):
		del self.workers[w.name]

	def start_schedule(self):
		if self.running:
			print('- schedule: ' + self.name + ' already running -')
		elif len(self.workers.keys()) == 0:
			print('- scheudle has no workers. i.e. \'[scheduleName] register bot [botName]\' -')
		else:
			print('\n- starting schedule: ' + self.name+' -\n')
			self.running = True
			self.__timer = Timer(self.__freq, self.__run_schedule)
			self.__timer.start()

	def stop_schedule(self):
		if self.running or self.__timer:
			print('- schedule: '+self.name +' stopped -')
			self.__timer.cancel()
			self.running = False
