import urllib.request

def verify_float(str):
	''' Checks if argument is a float '''
	try:
		float(str)
		return True
	except ValueError:
		return False
		
def calc_win_rate(my_rating, opponent_rating):
	''' Given two ratings, returns the expected score of the first team '''
	return 4*1/(1+10**(-(my_rating-opponent_rating)/400))
		
def update(rating, first_team, second_team, winner, winner_score):
	''' Updates the ratings of both teams, given the necessary data:
	rating: the dictionary of team ratings
	first_team: the name of the first team
	second_team: the name of the second team
	winner: the city of the winning team, or "Tie" in the case of a 2-2 match
	winner_score: the score of the winner, or "2" in the case of a tie '''
	
	# Ensure the first team is the winner for convienence; swap otherwise
	if second_team[0:len(winner)] == winner:
		first_team,second_team = second_team,first_team
	
	#Get expected scores
	exp_score_winner = calc_win_rate(rating[first_team], rating[second_team])
	exp_score_loser = calc_win_rate(rating[second_team], rating[first_team])
	
	#Update ratings, use K=14
	rating[first_team] = rating[first_team] + 14 * (float(winner_score) - exp_score_winner)
	rating[second_team] = rating[second_team] + 14 * ((4-float(winner_score)) - exp_score_loser)
	
	return rating

#Get data from schedule page
url = 'http://uschessleague.com/schedule-2015.php'
response = urllib.request.urlopen(url)
html_str = str(response.read())
sz = len(html_str)

rating = dict()

#	Format of substring representing a match:
#	<tr><td>1. Philadelphia Inventors vs New England Nor'easters</td><td>New England 3-1 </td></tr>
#   ^          ^                      ^                         ^        ^            ^
#   i          i+11                   i+j                       i+j+k    i+j+k+9      i+j+k+l
#
#	First team's name: begins at i+11 (inclusive), ends at i+j-1 (exclusive)
#	Second team's name: begins at i+j+3 (inclusive), ends at i+j+k (exclusive)
#	Winner: begins at i+j+k+9 (inclusive), end at i+j+k+l-2 (exclusive) OR i+j+k+l-4 (exclusive), depending on integer score or not
#	Winner's score: begins at i+j+k+l-1 (inclusive) OR i+j+k+l-3 (inclusive), depending on integer score or not

for rep in range(10000):
	#Run season 10000 times to find equilibrium state
	for i in range(sz-8):
		if(html_str[i:i+8] == '<tr><td>'):
		#Found index of a match!
			for j in range(40):
				if(html_str[i+j:i+j+2] == 'vs'):
					#End-ish of first team's name
					break
			
			#Found first team's name:
			first_team = html_str[i+11:i+j-1]
			
			#Might have an extra space :(
			if(first_team[0] == ' '):
				first_team = first_team[1:]
			
			#Find end of second team's name
			for k in range(40):
				if(html_str[i+j+k] == '<'):
					break
					
			#Found second team's name:
			second_team = html_str[i+j+3:i+j+k]
			
			#If first instance of team, add them to the rating dictionary
			if first_team not in rating:
				rating[first_team] = 2400.0
			if second_team not in rating:
				rating[second_team] = 2400.0
			
			#Find winner and their score
			for l in range(40):
				if(html_str[i+j+k+l] == '-'):
					break
			
			if html_str[i+j+k+l-1] == '5':
				#Winner had half-point score (2.5 or 3.5)
				winner = html_str[i+j+k+9:i+j+k+l-4]
				winner_score = html_str[i+j+k+l-3:i+j+k+l]
			else:
				#Winner had integer score
				winner = html_str[i+j+k+9:i+j+k+l-2]
				winner_score = html_str[i+j+k+l-1]
			
			#print(first_team, second_team, winner, winner_score)
			
			if not verify_float(winner_score):
				#Match hasn't been played yet :(
				break
			
			#Update rating
			rating = update(rating, first_team, second_team, winner, winner_score)
		
#Print ratings truncated at two decimal places
for key in sorted(rating.keys()):
	print(key,int(100*rating[key])/100.0)
