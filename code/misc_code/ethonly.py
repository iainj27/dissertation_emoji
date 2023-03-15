import sqlite3
import numpy as np
import pandas as pd

con = sqlite3.connect('emote_tweets.db')

cursor = con.cursor()

sql_query = pd.read_sql('SELECT * FROM eth', con)

df = pd.DataFrame(sql_query)

#print(df)

#print(df.dtypes)

df['time_date'] = pd.to_datetime(df['time_date'], infer_datetime_format=True)

#print(df)
#print(df.dtypes)

df['time_date'] = pd.to_datetime(df['time_date']).dt.normalize()

print(df)

df_day = df[(df['time_date'].dt.strftime('%Y-%m-%d')=="2019-09-02")]

#print(df_day)

#rint(df_day.dtypes)
#print(df.dtypes)

agg_emojis = ', '.join(df_day.emoji)

print(agg_emojis)


#This code can aggregate emojis from a single day for the ETH only table.
#Aim now is to try and get a sample regression done for ETH, or at least to get a data object that has columns for [day] and [emoji_used]
#Then can start computing a score somehow.
#Also need price data