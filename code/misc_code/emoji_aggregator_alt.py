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
path = f'../data/agg_em_{symbol}.xlsx'
exists = 0

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
    
    #THIS WOULD BE THE PLACE TO IMPLEMENT A SCORING FUNCTION?
    #Note agg_emojis type is 'str'

    #This creates a dataframe of the date and the emojis used, in order to write it to an excel file
    df_to_write = pd.DataFrame({'date': str(date), 'emojis used': agg_emojis}, index=[0])

    #If we're on the first writing operation, file does not yet exist, so exists = 0
    if exists == 0:
        exists += 1
        df_to_write.to_excel(path, index=False)

    else:
        with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='overlay') as writer:
            df_to_write.to_excel(writer, index=False)

print('Done!')
