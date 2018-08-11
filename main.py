import os
import argparse

import pandas as pd 

from elo_calculator import EloCalculator
from tabbie_scraper import TabbieScraper
from tabbycat_scraper import TabbyCatScraper


def main(tab_urls, master_elo_df, init_elo_value, k, div):

	tcat_scraper = TabbyCatScraper()
	tabbie_scraper = TabbieScraper()
	elo_calculator = EloCalculator(k=k, divisor=div)
	num_rounds = 5

	for url in tab_urls:

		if 'tabbie' in url:
			scraper = tabbie_scraper
		else:
			scraper = tcat_scraper
		
		# getting data on tournament
		print('\nscraping data for {}'.format(url))
		scraper.create_results_csv(tab_link=url)
		scraper.create_speakers_csv()

		# get initial (or initalise) elo for all speakers in competition
		team_speakers_df = pd.read_csv('./output_data/speakers/{}.csv'.format(scraper.tournamnet_name))
		if master_elo_df is not None:
			elo_df = pd.merge(team_speakers_df, master_elo_df[['speaker_name', 'speaker_elo']], on='speaker_name', how='left')
			elo_df['speaker_elo'].fillna(init_elo_value, inplace=True)
		else:
			elo_df = team_speakers_df.copy()
			elo_df['speaker_elo'] = init_elo_value
			master_elo_df = elo_df[['speaker_name', 'speaker_elo']]

		team_elo_df = elo_df.groupby(['team_name'])['speaker_elo'].mean().reset_index()
		
		results_filepath = './output_data/results/{}.csv'.format(scraper.tournamnet_name)

		# calculate elo
		print('calculating elo...')
		elo_calculator.calculate_elo(num_rounds=num_rounds, elo_df=team_elo_df, results_filepath=results_filepath)
		elo_calculator.elo_df.to_csv(path_or_buf='./output_data/elo/{}.csv'.format(scraper.tournamnet_name))

		elo_df = pd.merge(elo_df, elo_calculator.elo_df[['team_name', 'total_elo_change']], on='team_name', how='left')
		elo_df['new_elo'] = elo_df['speaker_elo'] + elo_df['total_elo_change']

		# add results to master elo document
		master_elo_df = pd.merge(master_elo_df, elo_df[['speaker_name', 'new_elo']], on='speaker_name', how='outer')
		master_elo_df['new_elo'].fillna(master_elo_df['speaker_elo'], inplace=True)
		master_elo_df['speaker_elo'] = master_elo_df['new_elo']
		master_elo_df.rename(columns={'new_elo':'{}_elo'.format(scraper.tournamnet_name)}, inplace=True)

	# clean up and save results
	master_elo_df = master_elo_df[master_elo_df.speaker_name != 'speaker 1']
	master_elo_df = master_elo_df[master_elo_df.speaker_name != 'speaker 2']
	master_elo_df = master_elo_df.sort_values(by='speaker_elo', ascending=False)
	master_elo_df.to_csv(path_or_buf='./output_data/elo/master_elo.csv')


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Web Scraper and Elo Calculator')
	parser.add_argument('--init-elo', type=int, default=1500, metavar='N',
						help='Elo score given to new speakers')
	parser.add_argument('--elo-k', type=int, default=32, metavar='N',
						help='k factor, see paper for more details (default 32)')
	parser.add_argument('--elo-divisor', type=int, default=32, metavar='N',
						help='divisor for elo, see paper for more details (default 400)')
	args = parser.parse_args()

	if not os.path.exists('./output_data'):
		os.mkdir('./output_data')
	if not os.path.exists('./output_data/results'):
		os.mkdir('./output_data/results')
	if not os.path.exists('./output_data/elo'):
		os.mkdir('./output_data/elo')
	if not os.path.exists('./output_data/speakers'):
		os.mkdir('./output_data/speakers')

	if os.path.exists('./input_data/master_elo.csv'):
		master_elo_df = pd.read_csv('./data/elo/master_elo.csv')
	else:
		master_elo_df = None

	if os.path.exists('./input_data/tab_urls.txt'):
		with open('./input_data/tab_urls.txt', 'r') as f:
			tab_urls = [line.strip() for line in f]

	init_elo_value = args.init_elo
	k = args.elo_k
	div = args.elo_divisor

	main(tab_urls, master_elo_df, init_elo_value, k, div)




