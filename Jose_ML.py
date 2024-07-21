import pandas as pd
import requests
# importing beautifulsoup to parse through HTML
from bs4 import BeautifulSoup
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score

matches = pd.read_csv("/Users/keshav/Documents/Projects/Jose_Buildspace/all_plmatches_23to20.csv", index_col= 0)
matches.dtypes

# converting columns to datatypes that are usable in the Random Forest Classifier model
matches["Date"] = pd.to_datetime(matches['Date'])                       
matches["coded_venue"] = matches["Venue"].astype("category").cat.codes        
matches["coded_opponent"] = matches["Opponent"].astype("category").cat.codes
matches["coded_time"] = matches["Time"].str.replace(":.+","", regex = True).astype(int)
matches["coded_day"] = matches["Date"].dt.dayofweek

point_mapping = {"W" : 3, "D" : 1, "L" : 1}                                   # converting result into points scored per match
matches["target"] = matches["Result"].map(point_mapping)

# implementing the Random Forest Classifier Model
rf = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=1)
training_set = matches[matches["Date"] < '2023-08-11']
test_set = matches[matches["Date"] >= '2023-08-11']
base_predictors = ["coded_venue", "coded_opponent", "coded_time", "coded_day"]
rf.fit(training_set[base_predictors], training_set["target"])
predictions = rf.predict(test_set[base_predictors])
acc_score = accuracy_score(test_set["target"], predictions)
prec_score = precision_score(test_set["target"], predictions, average='weighted')


combined = pd.DataFrame(dict(actual=test_set["target"], preds = predictions))
pd.crosstab(index=combined["actual"], columns=combined["preds"])

team_matches = matches.groupby('Team')
per_team_matches = team_matches.get_group("Chelsea")


# calculating rolling averages of key_predictors to take team 'form' into account
def rolling_averages(per_team_matches, keys, key_predictors):
    per_team_matches = per_team_matches.sort_values("Date")
    rolling_team_stats = per_team_matches[keys].rolling(3, closed='left').mean()
    per_team_matches[key_predictors] = rolling_team_stats
    per_team_matches = per_team_matches.dropna(subset = key_predictors)
    return per_team_matches

per_team_matches.columns
keys = ["xG", "xGA","Poss","SCA", "GCA", "PassLive", "PassLive.1", "Sh", "SoT", "Dist", "FK", "PK", "np:G-xG"]
key_predictors =  [f"rolling_{key}" for key in keys]

rolling_averages(per_team_matches, keys, key_predictors)
rolling_matches = matches.groupby("Team").apply(lambda x: rolling_averages(x, keys, key_predictors))
rolling_matches.droplevel("Team")
rolling_matches.index = range(rolling_matches.shape[0])

training_set = rolling_matches[rolling_matches["Date"] < '2023-12-11']
test_set = rolling_matches[rolling_matches["Date"] >= '2023-12-11']

def create_predictions(training_set, test_set, predictors):
    rf.fit(training_set[predictors], training_set["target"])
    predictions = rf.predict(test_set[predictors])
    final_df = pd.DataFrame(dict(actual = test_set["target"], predictions=predictions), index=test_set.index)
    acc_score = accuracy_score(test_set["target"], predictions)
    prec_score = precision_score(test_set["target"], predictions, average='weighted')
    return final_df, acc_score, prec_score

final_df, accuracy, prec_score = create_predictions(training_set, test_set, base_predictors+key_predictors)
final_df = final_df.merge(rolling_matches[["Date", "Team", "Opponent", "Result"]], left_index= True, right_index= True)
final_df
accuracy
prec_score
final_df["Team"].value_counts()
final_df["Opponent"].value_counts()

class MissingVals(dict):
    __missing__ = lambda self, key:key

name_mapping = {
    "BrightonandHoveAlbion" : "Brighton",
    "ManchesterUnited" : "Manchester Utd",
    "TottenhamHotspur" : "Tottenham",
    "NewcastleUnited" : "Newscastle Utd",
    "WestHamUnited" : "West Ham",
    "WolverhamptonWanderers" : "Wolves",
    "NottinghamForest" : "Nott'ham Forest"
}

mapping = MissingVals(**name_mapping)
final_df["correct_team_name"] = final_df["Team"].map(mapping)
merged_final_df = final_df.merge(final_df, left_on=["Date", "correct_team_name"], right_on=["Date", "Opponent"])
merged_final_df[(merged_final_df["predictions_x"] == 3) & merged_final_df["predictions_y"] == 0]["actual_x"].value_counts()
final_df["Date"].value_counts()
merged_final_df["Date"].value_counts()

# getting fixtures for next season
fbref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
fbref_page = requests.get(fbref_url)
fbref_page_soup = BeautifulSoup(fbref_page.content, 'html.parser')

next_season_url = fbref_page_soup.select("a.next")[0].get("href")
next_season_url = f"https://fbref.com{next_season_url}"
next_season_page = requests.get(next_season_url)
next_season_soup = BeautifulSoup(next_season_page.content, 'html.parser')
next_sf_atag = next_season_soup.find("a", text = "Scores & Fixtures").get("href")
next_sf_url = f"https://fbref.com{next_sf_atag}"
next_sf_page = requests.get(next_sf_url)
next_sf_table = pd.read_html(next_sf_page.text, match= "Scores & Fixtures")[0]
next_sf_table = next_sf_table.rename(columns={"Wk":"Round"})
matches["Round"] = matches["Round"].str.split(' ').str[1].astype(float)             # making the round column common for both datasets


# matching next_sf_table's format to matches
next_sf_table["Team"] = next_sf_table["Home"]
next_sf_table["coded_venue"] = 1
next_sf_table["Opponent"] = next_sf_table["Away"]
next_sf_table2 = next_sf_table.copy()
next_sf_table2["Opponent"] = next_sf_table["Home"]
next_sf_table2["Team"] = next_sf_table2["Away"]
next_sf_table2["coded_venue"] = 0

combined_table = pd.concat([next_sf_table, next_sf_table2], ignore_index= True)
combined_table = combined_table.rename(columns={"Score": "Result"})
common_columns = [col_name for col_name in combined_table.columns if (col_name in matches.columns)]
combined_table = combined_table.drop(columns=["Home","Away","xG","Attendance","Venue", "Referee","Match Report","Notes","xG.1"])
combined_table = combined_table.dropna(subset=["Round"])                           # dropping line breaks from the table
matches
next_sf_training_set = matches[["Team","Opponent","Date","Round","coded_day","coded_opponent","coded_time","coded_venue","Result","target"]]


# converting columns to datatypes that are usable in the Random Forest Classifier model
combined_table["Date"] = pd.to_datetime(combined_table["Date"])
combined_table["target"] = combined_table["Result"].fillna(0)                       
combined_table["coded_opponent"] = combined_table["Opponent"].astype("category").cat.codes
combined_table["coded_time"] = combined_table["Time"].str.replace(":.+","", regex = True).astype(int)
combined_table["coded_day"] = combined_table["Date"].dt.dayofweek
opponent_mapping = dict(zip(matches["Opponent"],matches["coded_opponent"]))                 # creating the same encoding pairs as the one in the training set
combined_table["coded_opponent"] = combined_table["Opponent"].map(opponent_mapping)
combined_table = combined_table.drop(columns=["Day","Time"])

next_season_predictions = create_predictions(next_sf_training_set, combined_table, base_predictors)        # cannot use key predictors because they do not exist yet
next_season_predictions
combined_table["Predictions"] = next_season_predictions[0]["predictions"]
combined_table
combined_gameweek = combined_table.merge(combined_table, left_on=["Date", "Team"], right_on=["Date", "Opponent"])

combined_gameweek.loc[combined_gameweek["Predictions_y"] == 3, "Predictions_x"] = 0
combined_gameweek.loc[combined_gameweek["Predictions_x"] == 3, "Predictions_y"] = 0
predicted_standings = combined_gameweek[["Team_x","Predictions_x"]]
predicted_standings = predicted_standings.groupby("Team_x").sum().sort_values("Predictions_x", ascending=False)

combined_gameweek = combined_gameweek.iloc[:380]



# creating a more presentable dataframe
final_predictions = combined_gameweek[["Round_x", "Date", "Team_x", "Opponent_x", "Predictions_x"]]
final_predictions = final_predictions.rename(columns = {"Round_x": "Matchweek", "Team_x":"Home Team", "Opponent_x":"Away Team", "Predictions_x":"Winner"})
final_predictions.loc[final_predictions["Winner"] == 3, "Winner"] = final_predictions.loc[(final_predictions["Winner"] == 3), "Home Team"]
final_predictions.loc[final_predictions["Winner"] == 1, "Winner"] = "Draw"
final_predictions.loc[final_predictions["Winner"] == 0, "Winner"] = final_predictions.loc[(final_predictions["Winner"] == 0), "Away Team"]
final_predictions.to_csv("2024-25_predictions.csv")