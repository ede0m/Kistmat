import praw
import sys
import json
import os
from models.target import Target
from models.worker import Worker
from models.schedule import Schedule
from requests import Session

###################################

def create_reddit_worker(bot_name, proxy_url):
	if proxy_url:
		s = Session()
		proxies = {
			'http': proxy_url,
			'https': proxy_url 
		}
		s.proxies.update(proxies)
		print(s.proxies)
		bot = praw.Reddit(bot_name, requestor_kwargs={'session': s})
	else:
		bot = praw.Reddit(bot_name)
	return bot

def save_worker_data():
	save_workers = {}
	for name, w in workers.items():
		save_worker = {}
		save_worker['interacted_with'] = list(w.interacted_with)
		save_worker['targets'] = list(name for name in w.targets.keys())
		save_workers[name] = save_worker
	return save_workers

def save_schedule_data():
	save_schedules = {}
	print('\n')
	for name, s in schedules.items():
		save_schedule = {}
		save_schedule['freq'] = s.get_freq()
		save_schedule['workers'] = list(name for name in s.workers.keys())
		save_schedule['name'] = name
		s.stop_schedule()
		save_schedules[name] = save_schedule
	return save_schedules

def save_session():
	session = {}
	session['workers'] = save_worker_data()
	session['schedules'] = save_schedule_data()
	with open('session.json', 'w', encoding='utf-8') as f:
		json.dump(session, f, ensure_ascii=False, indent=4)

def start_session(bots, target_users):

	start_session = {}
	targets = {}
	workers = {}
	schedules  = {}

	# init targets
	for target, options in target_users.items():
		targets[target] = Target(read_reddit, target, options)

	session_fn = 'session.json'
	load_data = {}
	if os.path.isfile(session_fn):
		with open(session_fn) as handle:
			data = json.loads(handle.read())
			workers = load_worker_data(data['workers'], targets)
			schedules = load_schedule_data(data['schedules'], workers)
	else:
		# init workers
		for bot_name in bots:
			bot = create_reddit_worker(bot_name, None)
			w = Worker(bot, bot_name)
			workers[bot_name] = w

	start_session['targets'] = targets
	start_session['workers'] = workers
	start_session['schedules'] = schedules
	return start_session


def load_worker_data(workers_data, targets):
	load_workers = {}
	for name, w in workers_data.items():
		workers_targets = {}
		workers_interacted = set(w['interacted_with'])
		for t in w.get('targets'):
			if targets.get(t):
				workers_targets[t] = targets.get(t)
		bot = create_reddit_worker(name, None)
		load_workers[name] = Worker(bot, name, workers_interacted, workers_targets)
	return load_workers

def load_schedule_data(schedules_data, workers):
	load_schedules = {}
	for name, s in schedules_data.items():
		schedules_bots = {}
		for bot_name in s['workers']:
			if workers.get(bot_name):
				schedules_bots[bot_name] = workers.get(bot_name)
		load_schedules[name] = Schedule(name, s['freq'], schedules_bots)
	return load_schedules	


def print_entities(entity_list):
	for k, v in entity_list.items():
		details = '\t\t\t'+v.name
		print(details)

def print_schedules(schedules):
	for name, s in schedules.items():
		print('\t\t\t'+name+'\t'+'freq: '+str(s.get_freq())+'m\trunning: '+str(s.running))

def create_schedule_prompt():
	n_schedules = len(schedules.keys())
	
	s_name = input('\nschedule name: ')
	name = s_name if (s_name.strip() != '') else 'schedule'+str(n_schedules+1)
	
	period = input('runs every X minutes: ')
	freq = int(period) if period.isdigit() else 20
	
	s = Schedule(name, freq)
	schedules[name] = s
	print('\ncreated schedule: '+s.name+'\n')

def print_usage():
	print('\n\nartificial karma 0.1\n--------------------')
	print('\nUSAGE:\n \nlist loaded targets: \t\t\'list targets\''+
		'\nlist loaded bots: \t\t\'list bots\''+
		'\nlist schedules: \t\t\'list schedules\''+
		'\n\ncreate a schedule: \t\t\'schedule create\''+
		'\nremove a schedule: \t\t\'schedule remove [scheduleName]\''+
		'\n\nadd bot to schedule: \t\t\'[scheduleName] register bot [botName]\''+
		'\nremove bot from schedule: \t\'[scheduleName] remove bot [botName]\''+
		'\nupdate schedule freq: \t\t\'[scheduleName] update freq [minutes]\''+
		'\nlist schedule\'s bots: \t\t\'[scheduleName] list bots\''+
		'\n\nregister target to bot: \t\'[botName] register target [targetName]\'' +
		'\nremove target from bot: \t\'[botName] remove target [targetName]\'' +
		'\nlist bot\'s targets: \t\t\'[botName] list targets\''+
		'\n\nrun all bots: \t\t\t\'run\''+
		'\nrun a schedule: \t\t\'run [scheduleName]\''+
		'\nrun a bot: \t\t\t\'run [botName]\''+
		'\nstop a schedule: \t\t\'stop [scheduleName]\''+
		'\n\nusage: \t\t\t\t\'help\'')
	print('---------------------\n')

def run_cli():
	
	while (True):
		try:
			cmds = input('> ').split(' ')
			
			if cmds[0] == 'list':
				if cmds[1] == 'targets':
					print_entities(targets)
				elif cmds[1] == 'bots':
					print_entities(workers)
				elif cmds[1] == 'schedules':
					print_schedules(schedules)
				else:
					print('unknown command: \''+cmds[1]+'\'')
			
			elif workers.get(cmds[0]) is not None:
				bot_name = cmds[0]
				
				if cmds[1] == 'register' and cmds[2] == 'target':
					if targets.get(cmds[3]) is not None:
						workers[bot_name].targets[cmds[3]] = targets[cmds[3]]
					else:
						print('target: ' + cmds[3] + ' not found')
				
				elif cmds[1] == 'remove' and cmds[2] == 'target':
					if targets.get(cmds[3]) is not None:
						del workers[bot_name].targets[cmds[3]]
					else:
						print('target: ' + cmds[3] + ' not found')
						
				elif cmds[1] == 'list':
					if cmds[2] == 'targets':
						print_entities(workers[cmds[0]].targets)
					else:
						print('unknown command: \''+cmds[0]+' '+cmds[1]+' '+cmds[2]+'\'')
				else:
					print('unknown command: \''+cmds[1]+' '+cmds[2]+'\'')

			elif cmds[0] == 'schedule':
				if cmds[1] == 'create':
					create_schedule_prompt()
				
				elif cmds[1] == 'remove':
					if schedules.get(cmds[2]) is not None:
						print('\n')
						schedules[cmds[2]].stop_schedule()
						del schedules[cmds[2]]
					else:
						print('schedule not found: ' + cmds[2])
				else:
					print('unknown command: \''+cmds[1]+' '+cmds[2]+'\'')

			elif schedules.get(cmds[0]) is not None:
				
				if cmds[1] == 'remove' and cmds[2] == 'bot':
					if workers.get(cmds[3]) is not None:
						schedules[cmds[0]].remove_worker(workers[cmds[3]])
					else:
						print('worker: '+cmds[3]+' not found')
				
				elif cmds[1] == 'register' and cmds[2] == 'bot':
					if workers.get(cmds[3]) is not None:
						schedules[cmds[0]].add_worker(workers[cmds[3]])
					else:
						print('worker: ' + cmds[3] + ' not found')

				elif cmds[1] == 'update' and cmds[2] == 'freq':
					freq = cmds[3]
					if freq.isdigit():
						freq = int(freq)
						schedules[cmds[0]].update_freq(freq)
					else:
						print(freq + ' is not an integer')
				
				elif cmds[1] == 'list':
					if cmds[2] == 'bots':
						for b in schedules[cmds[0]].workers.keys(): print('\t\t\t'+b)
					else:
						print('unknown command: \''+cmds[0]+' '+cmds[1]+' '+cmds[2]+'\'')
				else:
					print('unknown command: \''+cmds[1]+' '+cmds[2]+'\'')

			elif cmds[0] == 'run':
				if len(cmds) > 1:
					if schedules.get(cmds[1]) is not None:
						schedules[cmds[1]].start_schedule()

					elif workers.get(cmds[1]) is not None:
						print('\n- running '+cmds[1]+' -\n')
						print(workers[cmds[1]].run_worker())
					
					else:
						print('run target: ' + cmds[1] + ' not found')
				else:
					for w in workers.values():
						for t in w.targets.values():
							w.vote_flood(t)

			elif cmds[0] == 'help':
				print_usage()

			elif cmds[0].strip() != '':
				print('unknown command: \''+cmds[0]+'\'')
			
		except KeyboardInterrupt:
			save_session()
			print('\nsaving and exiting ...\n--------------------\n')
			sys.exit(0)

def print_targets_error():
	sample_target = {
		"someredditusername" : {
			"vote_direction" : 1,
			"comments" : True,
			"submissions" : True
		}
	}
	print("\nmissing target.json")
	print("place targets.json in run directory.")
	print('\nsample:\n')
	print(json.dumps(sample_target, indent=4, sort_keys=True) + "\n")
	sys.exit(0)

############################

# open targets config
target_users = {}
try:
	with open('targets.json') as handle:
		target_users = json.loads(handle.read())
		if len(target_users.keys()) == 0:
			print_targets_error()
except FileNotFoundError as not_found:
	print_targets_error()

# read only bot
read_reddit = praw.Reddit('reader_bot')

# try load 
session = start_session(['bot1', 'bot2'], target_users)
schedules = session['schedules']
workers = session['workers']
targets = session['targets']

# run app
print_usage()
run_cli()



