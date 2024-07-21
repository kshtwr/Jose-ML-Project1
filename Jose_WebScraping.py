#importing requests to get web-data
import requests
import pandas as pd
import time

# importing beautifulsoup to parse through HTML
from bs4 import BeautifulSoup

# rate limiter
def rate_check(n_requests):
    
    n_requests+=1
    if n_requests % 10 == 0:                         #respecting rate limits
        time.sleep(65)
    
    return n_requests



years = list(range(2023,2020, -1))
fbref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
all_matches = []
num_requests = 0

for year in years:                              # iterating through past seasons
    standings_data = requests.get(fbref_url)    # getting data from the standings page
    num_requests = rate_check(num_requests)
    standings_soup = BeautifulSoup(standings_data.content, 'html.parser')
    
    # selecting relevant squad urls from the table
    table_html = standings_soup.select('table.stats_table')[0]
    a_tags = table_html.find_all('a')
    squad_links = [a.get("href") for a in a_tags]
    squad_links = [l for l in squad_links if '/squads/' in l]
    squad_links = [f"https://fbref.com{l}" for l in squad_links]

    prev_season = standings_soup.select("a.prev")[0].get("href")
    fbref_url = f"https://fbref.com{prev_season}"
    
    # iterating over all premier league teams per season
    for squad in squad_links:
        # getting team name for a column
        team_name = squad.split("/")[-1].replace("-Stats", "").replace("-", "")


        squad_data = requests.get(squad)
        num_requests = rate_check(num_requests)
        
        squad_soup = BeautifulSoup(squad_data.content, 'html.parser')
        a_tags = squad_soup.find_all('a', text = 'Premier League')                    # getting premier league specific links
        a_tags = [a.get("href") for a in a_tags if a.get("href")]
        pl_scores_fixtures_link = [l for l in a_tags if '/matchlogs/' in l][0]         
        pl_scores_fixtures_link = f"https://fbref.com{pl_scores_fixtures_link}"      # getting to the scores & fixtures table
        

        # creating a dataframe out of the scores and fixtures table
        squad_sf_data = requests.get(pl_scores_fixtures_link)
        num_requests = rate_check(num_requests)
        squad_sf_data
        team_matches_sf = pd.read_html(squad_sf_data.text, match= "Scores & Fixtures")
        team_matches_sf
        # getting more in-depth data on goal and shot creation (key predictors)
        squad_sf_soup  = BeautifulSoup(squad_sf_data.text)
        goal_shot_page = squad_sf_soup.find('a', text = "Goal and Shot Creation")
        goal_shot_page = f"https://fbref.com{goal_shot_page.get("href")}"
        
        # creating and cleaning up the squad's premier league Goal and Shot Creation Data
        goal_shot_data = requests.get(goal_shot_page)
        num_requests = rate_check(num_requests)
        goal_shot_data
        team_goal_shot_data = pd.read_html(goal_shot_data.text, match = "Goal and Shot Creation")[0]
        team_goal_shot_data.columns = team_goal_shot_data.columns.droplevel()
        team_goal_shot_data = team_goal_shot_data[team_goal_shot_data['Comp'] == 'Premier League']

        # getting more in-depth data on shooting statistics (key predictors)
        shooting_page = squad_sf_soup.find('a', text = "Shooting")
        shooting_page = f"https://fbref.com{shooting_page.get("href")}"
        shooting_data = requests.get(shooting_page)
        num_requests = rate_check(num_requests)
        team_shooting_data = pd.read_html(shooting_data.text, match = "Shooting")[0]
        team_shooting_data.columns = team_shooting_data.columns.droplevel()
        team_shooting_data = team_shooting_data[team_shooting_data['Comp'] == 'Premier League']

        # merging scores & fixtures, Goal and Shot Creation, Shooting dataframes together
        try:
            team_data = team_matches_sf[0].merge(team_goal_shot_data[["Round", "SCA", "GCA", "PassLive"]], on = "Round")   
            team_data = team_data.merge(team_shooting_data[["Round", "Sh", "SoT", "Dist", "FK", "PK","np:G-xG"]], on = "Round")
        except:
            continue    
        
        print(num_requests)
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)


all_matches_df = pd.concat(all_matches)
all_matches_df.to_csv("all_plmatches_23to20.csv")
all_matches_df.columns