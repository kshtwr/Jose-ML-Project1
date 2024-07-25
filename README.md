# Jose-ML-Project1
José, is a chat-bot that refers to 2 csv files with data of the past 3 Premier League seasons, and predictions for the next season, to provide you detailed insight into your favorite footballing team. Oh, and he does so in the same way as his famous name-sake and legendary football manager, José Mourinho.

To use the site, visit this [link](https://jose-ml-project1.streamlit.app/)

## Jose_WebScraping.py
This Python script scrapes Premier League match data (from FBref.com) for the seasons from 2023 to 2021. It collects data on scores, fixtures, goal and shot creation, and shooting statistics for each team in the league. The script uses requests to fetch web data, BeautifulSoup to parse HTML, and pandas to handle dataframes. The data is stored in a CSV file for further analysis.

### Prerequisites
- Python 3.x
- `requests` library
- `pandas` library
- `beautifulsoup4` library

### Script Flow
- Import Libraries
- Implement Rate Limiter Function (FBRef has a 10 requests/min rate limit)
- Define Seasons and Base URLs
- The Main loop iterates over and merges each season: extracts squad links from standings page, fetches match logs, goal and shot creation and shooting data for each squad
- Clean Data, append each team's data to a list, combine them into a single dataframe, save the dataframe to a CSV File titled `all_plmatches_23to20.csv`

## all_plmatches_23to20.csv file
This CSV file contains data for each fixture for each Premier League squad over the past 3 seasons (2020-23). The column headings included 'Date', 'Time', 'Round', 'Day', 'Venue', 'Result', 'GF', 'GA', 'Opponent', 'xG', 'xGA', 'Poss', 'Attendance', 'Captain', 'Formation', 'Referee', 'Match Report', 'Notes', 'SCA', 'GCA', 'PassLive', 'PassLive.1', 'Sh', 'SoT', 'Dist', 'FK', 'PK', 'np:G-xG','Season', 'Team'. 

This csv file is then read into Jose_ML.py to create the training set for future predictions. Testing this dataset with the key parameters (illustrated in Jose_Ml.py) on a distinct subset of the data, yielded a 65.8% precision score, and 66.5% accuracy.

## Jose_ML.py
This Python script predicts the outcomes of Premier League matches for the 2024-25 season using a Random Forest Classifier. It processes historical match data, trains a model, and makes predictions for future fixtures.

### Prerequisites
- Python 3.x
- `pandas` library
- `requests` library
- `beautifulsoup4` library
- `scikit-learn` library

### Script Flow
- Import Libraries
- Load and Prepare Data:
  - Read historical match data.
  - Convert columns to appropriate data types for the model.
- Train Random Forest Model:
  - Define and train the model using the historical data up to a specified date.
- Rolling Averages:
  - Calculate rolling averages of key predictors to account for team form.
- Create Predictions:
  - Predict outcomes for test set and calculate accuracy and precision.
- Mapping and Merging:
  - Map team names and merge data for final prediction table.
- Get Future Fixtures:
  - Scrape the fixtures for the upcoming season and format data to match historical data.
- Predict Future Fixtures:
  - Predict outcomes for future fixtures using the trained model.
- Generate Final Predictions:
  - Format the predictions into a presentable dataframe and save to CSV titled - 2024-25_Predictions.csv

## 2024-25_Predictions.csv file
This CSV file contains predictions (Winner/Draw) for each fixture for each Premier League squad for the next season (2024-25). The column headings include 'Matchweek', 'Date', 'Home Team', 'Away Team', 'Winner'. 

**Note**: The data is slightly skewed in favour of teams that have not featured in the league for the past 3 seasons (for e.g. Ipswich Town). Moreover, there is a definite inclination towards draws over definitive wins/losses. Lastly, the predictions were made on previously established base predictors - Opponent, Venue, Day & Time.
  
