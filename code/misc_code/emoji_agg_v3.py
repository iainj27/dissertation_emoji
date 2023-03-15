import pandas as pd
import sqlite3
import openpyxl

#Setting up connection to database of emoji-containing tweets
con = sqlite3.connect('emote_tweets.db')
cursor = con.cursor()

#Grab symbol that user wants to aggregate emojis for
symbol = input('''Enter Symbol to select from tweets.
Example: if you enter 'ETH', program will select tweets that *ONLY* contain $ETH cashtag, and no others.
Tweets with "$ETH $BTC $XRP" for example, will be ignored. --  ''')

#Sets up path for writing results into excel file
#exists variable represents whether file exists or not, make sure to delete excel file if it exists
path = f'../data/agg_em_tweets{symbol}.xlsx'
exists = 0
dataframes = 0

#Reads the tweets with selected symbol into a dataframe
sql_query = pd.read_sql(f"SELECT * FROM tweets WHERE symbols IS '{symbol}'", con)
df = pd.DataFrame(sql_query)

#Converts time_date column from object datatype to datetime datatype so pandas can perform datetime operations
df['time_date'] = pd.to_datetime(df['time_date'], infer_datetime_format=True)

#Removes the time section on the datetime, we just want date
df['time_date'] = pd.to_datetime(df['time_date']).dt.normalize()

#Gets unique datetimes from the DataFrame. These values will be used to aggregate emojis by the day they were tweeted
dates = df.time_date.unique()

#Dates take format of: '2019-11-05 00:00:00+00:00' for example
#Loop through all dates and uses them to create a new dataframe
#This dataframe represents a single day
#Then joins all emojis used on that day into a single object
for date in dates:
    df_day = df.loc[(df['time_date'] == f'{date}')]
    agg_emojis = ', '.join(df_day.emoji)
    rows = df_day.shape[0]

    
    #THIS WOULD BE THE PLACE TO IMPLEMENT A SCORING FUNCTION?
    #Note agg_emojis type is 'str'

    #This creates a dataframe of the date and the emojis used, in order to write it to an excel file
    

    if dataframes == 0:
        df_to_write = pd.DataFrame({'date': str(date), 'emojis used': agg_emojis, 'number of tweets': rows}, index=[0])
        dataframes += 1

    else:
        second_df = pd.DataFrame({'date': str(date), 'emojis used': agg_emojis, 'number of tweets': rows}, index=[0])
        df_to_write = pd.concat([df_to_write, second_df])
        dataframes += 1


print(f'Shape of eventual dataframe: {df_to_write.shape}  - Note, compare with number of rows expected')

df_to_write.to_excel(path, index=False)

print(f'Done! {dataframes} rows written')