import json
import re
from collections import defaultdict
import os

import pandas as pd 
from robobrowser import RoboBrowser 


class TabbyCatScraper():

	def __init__(self):

		self.br = RoboBrowser(parser='html.parser')

	
	def create_results_csv(self, tab_link=None, check_existing=False):

		regex_str = 'https://([a-zA-Z-]+)'
		
		self.tournamnet_name = re.match(regex_str, tab_link).group(1)
		if not os.path.exists('./output_data/results/{}.csv'.format(self.tournamnet_name)):
			self.create_results_dict(tab_link)
			results_df = self.create_results_df()
			results_df.to_csv(path_or_buf='./output_data/results/{}.csv'.format(self.tournamnet_name))
		else:
			print('Already have results for this competition!')

	
	def create_speakers_csv(self):

		if os.path.exists('./output_data/speakers/{}.csv'.format(self.tournamnet_name)):
			return

		script_data_text = self.br.parsed.find_all('script')[0].string
		script_data_text = script_data_text[script_data_text.find('vueData = ')+10:-3]
		script_data_text = '{"tableData"' + script_data_text[18:] # makes json valid
		script_data_json = json.loads(script_data_text)

		team_name_dict = defaultdict(list)
		for team_data in script_data_json['tableData'][0]['data']:
			td = team_data[1]['popover']
			tn = team_data[1]['text']
			sn = td['content'][0]['text'].lower()
			
			spkr_1, spkr_2 = sn.split(', ')
			
			team_name_dict['team_name'].append(tn)
			team_name_dict['speaker_name'].append(spkr_1)
			
			team_name_dict['team_name'].append(tn)
			team_name_dict['speaker_name'].append(spkr_2)
			
		team_speakers_df = pd.DataFrame(team_name_dict)
		team_speakers_df.to_csv(path_or_buf='./output_data/speakers/{}.csv'.format(self.tournamnet_name))

	def create_results_dict(self, tab_link):

		self.br.open(tab_link)
		script_data_text = self.br.parsed.find_all('script')[0].string
		script_data_text = script_data_text[script_data_text.find('vueData = ')+10:-3]
		script_data_text = '{"tableData"' + script_data_text[18:] # makes json valid
		script_data_json = json.loads(script_data_text)

		self.total_team_results = []
		for team_record in script_data_json['tableData'][0]['data']:
			team_name = team_record[1]['text']
			round_num = 1
			
			team_results = [team_name]
			for round_record in team_record[2:7]:
				try:
					teams = round_record['popover']['content'][0]['text'].split('<br />')[1:]
				except KeyError:
					continue
				
				teams = [team[8:-14] if '<strong>' in team else team[:-5] for team in teams]
				places = {team:0 for team in teams}
				places[team_name] = int(round_record['text'][0])
				places['round_number'] = round_num
				round_num += 1
				team_results.append(places)
			
			self.total_team_results.append(team_results)


	def create_results_df(self):

		df_dict = defaultdict(list)
		for team_results in self.total_team_results:
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
			

		df = pd.DataFrame(df_dict)

		for i in range(1, 4):

			df = pd.merge(df, df[['team_name', 'team_result', 'round_number']], 
							left_on=['opp_{}_name'.format(i), 'round_number'], 
							right_on=['team_name', 'round_number'])

			df['opp_{}_result'.format(i)] = df['team_result_y']
			df.drop(['team_result_y', 'team_name_y'], axis=1, inplace=True)
			df.rename(columns={'team_name_x':'team_name', 'team_result_x':'team_result'}, inplace=True)

		return df
