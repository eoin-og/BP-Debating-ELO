import pandas as pd 

class EloCalculator():

	def __init__(self, k=32, divisor=400):

		self.k = k
		self.divisor = divisor
		self.calc_elo_score = lambda t1, t2: (10**((t1 - t2)/self.divisor)) / (1 + 10**((t1 - t2)/self.divisor))

	
	def calculate_elo(self, num_rounds=None, results_filepath=None, elo_df=None):

		self.results_df = pd.read_csv(results_filepath)
		self.elo_df = elo_df.copy()
		self.elo_df.rename(columns={'speaker_elo':'r0_elo'}, inplace=True)

		for i in range(1, num_rounds + 1):
			self.calc_one_round(round_number=i)

		self.elo_df['total_elo_change'] = self.elo_df['r{}_elo'.format(num_rounds)] - self.elo_df['r0_elo']

	
	def calc_one_round(self, round_number=None):

		round_elo_col_name = 'r{}_elo'.format(round_number - 1)
		elo_round_df = self.elo_df[['team_name', round_elo_col_name]]
		round_df = self.results_df[self.results_df['round_number'] == round_number]

		# add team elo
		round_df = pd.merge(round_df, elo_round_df, on='team_name')
		round_df.rename(columns={round_elo_col_name:'team_elo'}, inplace=True)


		for opp in ['opp_1_', 'opp_2_', 'opp_3_']:

			# change team position to won/loss bool
			round_df[opp + 'result'] = round_df['team_result'] < round_df[opp + 'result']

			# add opponent elo
			round_df = pd.merge(round_df, elo_round_df, left_on=opp + 'name', right_on='team_name')
			round_df.drop('team_name_y', axis=1, inplace=True)
			round_df.rename(columns={round_elo_col_name:opp + 'elo', 'team_name_x':'team_name'}, inplace=True)

			round_df[opp + 'elo_change'] = round_df.apply(lambda x: self.k*(
																	x[opp + 'result'] - 
																	self.calc_elo_score(x['team_elo'], x[opp + 'elo'])),
																	axis=1)

		round_df['team_elo_change'] = round_df[['opp_1_elo_change', 'opp_2_elo_change', 'opp_3_elo_change']].sum(axis=1)

		self.elo_df = pd.merge(self.elo_df, round_df[['team_name', 'team_elo_change']], on='team_name')
		self.elo_df.rename(columns={'team_elo_change':'r{}_elo_change'.format(round_number)}, inplace=True)
		self.elo_df['r{}_elo'.format(round_number)] = self.elo_df[round_elo_col_name] + self.elo_df['r{}_elo_change'.format(round_number)]
