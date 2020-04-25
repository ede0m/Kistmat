import praw
import sys
import json
import os
from modules.proxy_studio import *
from modules.investigator import *
from models.target import Target
from models.worker import Worker
from models.schedule import Schedule
from requests import Session

###################################

def create_reddit_worker(bot_name, proxy_url):
	if proxy_url:
		s = Session()
		proxies =  { 'https': proxy_url}
		s.proxies.update(proxies)
		bot = praw.Reddit(bot_name, requestor_kwargs={'session': s})
		print(bot._core._requestor._http.proxies.get('https'))
	else:
		bot = praw.Reddit(bot_name)
	return bot

def update_worker_proxy(bot_name):
	choice = input('\n1. manual entry\n2. random assignment\n3. clear proxy\n4. exit\n\nchoose a number: ')
	if choice == '1':
		print('\nplease enter https proxy in this form: https://72.35.40.34:8080')
		proxy_url = input('\nproxy url: ')
		valid = validate_proxy_url(proxy_url)
		if valid:
			test = input('would you like to test your proxy? (y/n): ')
			if test == 'y' or test == 'Y':
				try_proxy(proxy_url)
			finalize = input('finalize proxy update? (y/n): ')
			if finalize == 'y' or finalize == 'Y':
				workers[bot_name].update_instance(create_reddit_worker(bot_name, proxy_url))
	elif choice == '2':
		get_usable_https_proxies()
	elif choice == '3':
		workers[bot_name].update_instance(create_reddit_worker(bot_name, None))

	print('\n')


def save_worker_data():
	save_workers = {}
	for name, w in workers.items():
		save_worker = {}
		save_worker['interacted_with'] = list(w.interacted_with)
		save_worker['targets'] = list(name for name in w.targets.keys())
		save_worker['proxy'] = w.worker_instance._core._requestor._http.proxies.get('https')
		save_worker['random_vote_sleep_max_sec'] = w.random_vote_sleep_max_sec
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
		targets[target] = Target(target, options)

	session_fn = 'session.json'
	load_data = {}
	if os.path.isfile(session_fn):
		with open(session_fn) as handle:
			data = json.loads(handle.read())
			workers = load_worker_data(data['workers'], targets)
			schedules = load_schedule_data(data['schedules'], workers)

	# init workers
	for bot_name in bots:
		if workers.get(bot_name) == None:
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
		worker_proxy = w.get('proxy')
		workers_interacted = set(w['interacted_with'])
		workers_targets = {}
		for t in w.get('targets'):
			if targets.get(t):
				workers_targets[t] = targets.get(t)
		bot = create_reddit_worker(name, worker_proxy)
		load_workers[name] = Worker(bot, name, workers_interacted, workers_targets)

		if w.get('random_vote_sleep_max_sec'):
			load_workers[name].set_vote_sleep_max_sec(w['random_vote_sleep_max_sec'])

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

def print_investigations(investigations):
	for k, v in investigations.items():
		details = '\t\t\t'+v.name+'\tprogress: '+str(v.progress)+'%'
		print(details)

def print_targets(targets):
	for k, v in targets.items():
		details = '\t\t\t'+v.name
		print(details)

def print_workers(workers):
	for k, v in workers.items():
		proxy = v.worker_instance._core._requestor._http.proxies.get('https')
		if proxy == None:
			proxy = '\t\t\t'

		details = '\t\t\t'+v.name+'\t'+ str(proxy) + '\trand_vote_sleep: '+str(v.random_vote_sleep_max_sec)
		print(details)

def print_schedules(schedules):
	for name, s in schedules.items():
		print('\t\t\t'+name+'\t'+'freq: '+str(s.get_freq())+'m\trunning: '+str(s.running))

def print_schedule_log(schedule):
	print(schedules.get(schedule).log)

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
	print('\n\nartificial karma 0.2\n--------------------')
	print('\nUSAGE:\n \nlist loaded targets: \t\t\'list targets\''+
		'\nlist loaded bots: \t\t\'list bots\''+
		'\nlist schedules: \t\t\'list schedules\''+
		'\n\ncreate a schedule: \t\t\'schedule create\''+
		'\nremove a schedule: \t\t\'schedule remove [scheduleName]\''+
		'\n\nadd bot to schedule: \t\t\'[scheduleName] register bot [botName]\''+
		'\nremove bot from schedule: \t\'[scheduleName] remove bot [botName]\''+
		'\nupdate schedule freq: \t\t\'[scheduleName] update freq [minutes]\''+
		'\nlist schedule\'s bots: \t\t\'[scheduleName] list bots\''+
		'\nprint schedule\'s log: \t\t\'[scheduleName] print log\''+
		'\n\nregister target to bot: \t\'[botName] register target [targetName]\'' +
		'\nremove target from bot: \t\'[botName] remove target [targetName]\'' +
		'\nlist bot\'s targets: \t\t\'[botName] list targets\''+
		'\nupdate a bot\'s proxy: \t\t\'[botName] update proxy\''+
		'\nbot\'s vote sleep offset max: \t\'[botName] set sleep [sec]\''+
		'\n\nrun all bots: \t\t\t\'run\''+
		'\nrun a schedule: \t\t\'run [scheduleName]\''+
		'\nrun a bot: \t\t\t\'run [botName]\''+
		'\nstop a schedule: \t\t\'stop [scheduleName]\''+
		'\nrun an investigation: \t\t\'run investigation\''+
		'\n\nusage: \t\t\t\t\'help\'')
	print('---------------------\n')

def run_cli():
	
	while (True):
		try:
			cmds = input('> ').split(' ')
			
			if cmds[0] == 'list':
				if cmds[1] == 'targets':
					print_targets(targets)
				elif cmds[1] == 'bots':
					print_workers(workers)
				elif cmds[1] == 'schedules':
					print_schedules(schedules)
				elif cmds[1] == 'investigations':
					print_investigations(active_investigations)
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
					
				elif len(cmds) > 3 and cmds[1] == 'set' and cmds[2] == 'sleep' and cmds[3].isdigit():
					workers[cmds[0]].set_vote_sleep_max_sec(cmds[3])

				elif len(cmds) > 2 and cmds[1] == 'list':
					if cmds[2] == 'targets':
						print_targets(workers[cmds[0]].targets)
					else:
						print('unknown command: \''+cmds[0]+' '+cmds[1]+' '+cmds[2]+'\'')
				
				elif len(cmds) > 2 and cmds[1] == 'update' and cmds[2] == 'proxy':
					update_worker_proxy(cmds[0])

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
					if len(cmds) > 2 and cmds[2] == 'bots':
						for b in schedules[cmds[0]].workers.keys(): print('\t\t\t'+b)
					else:
						print('unknown command: \''+cmds[0]+' '+cmds[1]+'\'')

				elif cmds[1] == 'print':
					print_schedule_log(cmds[0])

				else:
					print('unknown command: \''+cmds[1]+' '+cmds[2]+'\'')

			elif cmds[0] == 'run':
				if len(cmds) > 1:
					if schedules.get(cmds[1]) is not None:
						schedules[cmds[1]].start_schedule()

					elif workers.get(cmds[1]) is not None:
						print('\n- running '+cmds[1]+' -\n')
						print(workers[cmds[1]].run_worker())
					
					elif cmds[1] == 'investigation':
						investigation = TargetInvestigation(read_reddit)
						active_investigations[investigation.name] = investigation
					
					else:
						print('run target: ' + cmds[1] + ' not found')
				else:
					for w in workers.values():
						for t in w.targets.values():
							w.vote_flood(t)

			elif cmds[0] == 'help':
				print_usage()

			elif cmds[0].strip() != '':
				print('unknown command: \''+' '.join(cmds)+'\'')
			
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
session = start_session(['bot1', 'bot2', 'bot3', 'bot4', 'bot5', 'bot6', 'bot7', 'bot8'], target_users)
schedules = session['schedules']
workers = session['workers']
targets = session['targets']
active_investigations = {}

# run app
print_usage()
run_cli()



