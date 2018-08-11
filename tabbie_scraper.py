import time
from collections import defaultdict
import re
import os

import pandas as pd
from robobrowser import RoboBrowser 


class TabbieScraper():

	def __init__(self):

		self.br = RoboBrowser(parser='html.parser')
		self.logged_in = False
		self.base_url = "https://www.tabbie.org"
		self.sleep_time_secs = 2


	def create_results_csv(self, tab_link=None):

		if not self.logged_in:
			self.login()

		regex_str = 'https://www.tabbie.org/([a-zA-Z-]+)'
		
		self.tournamnet_name = re.match(regex_str, tab_link).group(1)
		if not os.path.exists('./output_data/results/{}.csv'.format(self.tournamnet_name)):
			self.team_tab_url = "https://www.tabbie.org/{}/stats/team-tab".format(self.tournamnet_name)
			self.get_team_performance_links()
			results_df = self.create_results_df()
			results_df.to_csv(path_or_buf='./output_data/results/{}.csv'.format(self.tournamnet_name))
		else:
			print('Already have results for this competition!')


	def create_speakers_csv(self):

		if os.path.exists('./output_data/speakers/{}.csv'.format(self.tournamnet_name)):
			return

		self.br.open('https://www.tabbie.org/{}/stats/speaker-tab/'.format(self.tournamnet_name))
		team_speakers_dict = defaultdict(list)
		for team in self.br.parsed.find_all('table')[0].find_all('tr')[1:]:
		    team_row_cells = team.find_all('td')
		    speaker_name = team_row_cells[1].text.lower()
		    team_name = team_row_cells[2].text
		    team_speakers_dict['team_name'].append(team_name)
		    team_speakers_dict['speaker_name'].append(speaker_name)

		team_speakers_df = pd.DataFrame(team_speakers_dict)
		team_speakers_df.to_csv(path_or_buf='./output_data/speakers/{}.csv'.format(self.tournamnet_name))

	
	def create_team_results_dict(self, team_url, team_name):
		self.br.open(team_url)
		divs = self.br.parsed.find_all('div')[1].find_all('div')[3]
		divs = divs.find_all('div')[2].find_all('div', recursive=False)

		team_results = [team_name]

		for div in divs[1:]:
			round_name = div.find_all('div', {'class': 'panel-heading'})[0].getText()

			team_name_elements = div.find_all('tr')[1].find_all('td')
			team_names = [td.getText() for td in team_name_elements]

			team_place_elements = div.find_all('tr')[2].find_all('td')
			team_places = [td.getText()[1] for td in team_place_elements]

			round_name_place = {name:place for name, place in zip(team_names, team_places)}
			round_name_place['round_number'] = int(round_name[-1])

			team_results.append(round_name_place)

		return team_results

	
	def login(self):

		with open('./input_data/tabbie_login.txt', 'r') as f:
			uname_pass = [line.strip() for line in f] 

		self.br.open(self.base_url + "/site/login")

		form = self.br.get_form()
		form['LoginForm[email]'] = uname_pass[0]
		form['LoginForm[password]'] = uname_pass[1]
		self.br.submit_form(form)

	
	def get_team_performance_links(self):

		# get list of links for individual team performances
		self.br.open(self.team_tab_url)
		links = self.br.find_all('a', href=True)
		self.team_links = [(link['href'], link.getText()) for link in links
							if self.tournamnet_name in link['href'] and 'team/' in link['href']]


	def create_results_df(self):

		# make list of team performances
		print('Downloading data for {}'.format(self.tournamnet_name))
		print('\nThere are {} teams so this might stake about {} seconds...'.format(len(self.team_links), len(self.team_links)*3))
		total_team_results = []
		for team_link, team_name in self.team_links:
			team_url = self.base_url + team_link[2:-2]
			team_results = self.create_team_results_dict(team_url, team_name)
			total_team_results.append(team_results)
			time.sleep(self.sleep_time_secs) # don't spam!!

		# turn into dataframe
		df_dict = defaultdict(list)
		for team_results in total_team_results:
			team_name = team_results[0]

			for team_result in team_results[1:]:
				i = 1
				for name, pos in team_result.items():

					if name == team_name:
						df_dict['team_name'].append(name)
						df_dict['team_result'].append(pos)
						continue

					if name == 'round_number':
						df_dict[name].append(pos)
						continue

					df_dict['opp_{}_name'.format(i)].append(name)
					df_dict['opp_{}_result'.format(i)].append(pos)
					i += 1

		return pd.DataFrame(df_dict)