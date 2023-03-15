# This Python file uses the following encoding: utf-8
import pandas as pd
import yfinance as yf
import datetime as dt
import csv
import sqlite3
import emoji as em
import numpy as np

#ongoing work to streamline all code into one program, to write functions for certain parts/tools etc

con = sqlite3.connect('emote_tweets.db')
cursor = con.cursor()
total_errors = 0

FULL_TICKERS = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'USDT-USD', 'BCH-USD', 'LTC-USD', 'EOS-USD', 
          'BNB-USD', 'BSV-USD', 'XLM-USD', 'TRX-USD', 'ADA-USD', 'XMR-USD', 'LEO-USD', 
          'XTZ-USD', 'LINK-USD', 'ATOM-USD', 'HT-USD', 'NEO-USD', 'MIOTA-USD']

STUDY_TICKERS = ['BTC-USD', 'ETH-USD', 'NEO-USD', 'LTC-USD']

emoji_score_list = pd.read_excel("emoji_scores_2.xlsx")
novak_score_list = pd.read_excel("Emoji_S_D_v1.xlsx")

def get_tickers():
#Gets tickers from the csv file. first 22   
    tickers = []
    with open('../data/symbol_rankings_ordered.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        limit = 0
        for row in csv_reader:
            if limit <=22:
                tickers.append(row[0].upper())
                limit += 1
            else:
                break
    return tickers

#emoji scorer
#gets score (either 1, 0, or -1) from score list (a csv of agreed sentiments by IJ and JB)
#some emojis (very few) throw value error for some reason, try-except handles this and commented print statement can be un-commented to see these problematic emojis
def emoji_scorer(emojis):
    emojis = em.emoji_list(emojis)
    score = 0
    for i in emojis:
        try:
            points = emoji_score_list.query(f"emoji=='{i['emoji']}'")['score'].item()
            score += points
        except ValueError:
            #print(i['emoji'])
            continue

    return score

def individual_scorer(emoji, emojis):
    emojis = em.emoji_list(emojis)
    #print(emojis)
    i_score = 0
    for i in emojis:
        try:
            if emoji in i['emoji']:
                i_score += 1
        except ValueError:
            #print(i['emoji'])
            continue
    return i_score

def novak_score(emojis):
    emojis = em.emoji_list(emojis)
    n_score = 0
    for i in emojis:
        try:
            points = novak_score_list.query(f"emoji=='{i['emoji']}'")['score'].item()
            n_score += points
        except ValueError:
            #print(i['emoji'])
            continue
    return n_score


def mkt_return(tickers):

    returns_df = pd.DataFrame()
    volume_df = pd.DataFrame()
    volatility_df = pd.DataFrame()
    master_df= pd.DataFrame()

    for ticker in tickers:
        df = yf.download(ticker, start='2019-08-31', end='2019-11-27')
        returns_df[f'return-{ticker}'] = (df['Close'] - df['Open'])/ df['Open']
        volume_df[f'volume-{ticker}'] = df['Volume']
        volatility_df[f'volatility-{ticker}'] = (np.log(df["High"]) - np.log(df["Low"]))

    master_df['returns'] = returns_df.mean(axis=1)
    master_df['mean_return'] = returns_df.mean(axis=1)
    master_df['Volume'] = volume_df.mean(axis=1)
    master_df['total_volume'] = volume_df.sum(axis=1)
    master_df['volatility'] = volatility_df.mean(axis=1)
    
    master_df["tomorrow_volume"] = master_df["Volume"].shift(-1)
    master_df["tomorrow_volume_2"] = master_df["Volume"].shift(-2)
    master_df["yesterday_volume"] = master_df["Volume"].shift(1)

    master_df["total_tomorrow_volume"] = master_df["total_volume"].shift(-1)
    master_df["total_tomorrow_volume_2"] = master_df["total_volume"].shift(-2)
    master_df["total_yesterday_volume"] = master_df["total_volume"].shift(1)

    master_df["tomorrow_returns"] = master_df["returns"].shift(-1)
    master_df["tomorrow_returns_2"] = master_df["returns"].shift(-2)
    master_df["yesterday_returns"] = master_df["returns"].shift(1)

    master_df["tomorrow_volatility"] = master_df["volatility"].shift(-1)
    master_df["tomorrow_volatility_2"] = master_df["volatility"].shift(-2)
    master_df["yesterday_volatility"] = master_df["volatility"].shift(1)

    master_df = master_df['2019-09-02':'2019-11-25']



    return master_df


def emoji_aggregator(ticker):
    dataframes = 0
    tweetnos = []
    #Reads the tweets with selected symbol into a dataframe
    sql_query = pd.read_sql(f"SELECT * FROM tweets WHERE symbols IS '{ticker}'", con)
    df = pd.DataFrame(sql_query)

    #Converts time_date column from object datatype to datetime datatype so pandas can perform datetime operations
    df['time_date'] = pd.to_datetime(df['time_date'], infer_datetime_format=True)

    #Removes the time section on the datetime, we just want date
    df['time_date'] = pd.to_datetime(df['time_date']).dt.normalize()

    #Gets unique datetimes from the DataFrame. These values will be used to aggregate emojis by the day they were tweeted
    dates = df.time_date.unique()

    for date in dates:
        df_day = df.loc[(df['time_date'] == f'{date}')]
        agg_emojis = ', '.join(df_day.emoji)
        em_count = em.emoji_count(agg_emojis)
        rows = df_day.shape[0]
        tweetnos.append(rows)
        sentiment = emoji_scorer(agg_emojis)
        novak_sentiment = novak_score(agg_emojis)
        rockets = individual_scorer('🚀', agg_emojis)
        fires = individual_scorer('🔥', agg_emojis)
        ticks = individual_scorer('✅', agg_emojis)
        moneybags = individual_scorer('💰', agg_emojis)
        up_stocks = individual_scorer('📈', agg_emojis)
        skulls = individual_scorer('💀', agg_emojis)
        down_stocks = individual_scorer('📉', agg_emojis)
        alerts = individual_scorer('🚨', agg_emojis)
        down_arrows = individual_scorer('🔻', agg_emojis)

        #Note agg_emojis type is 'str'

        #This creates a dataframe of the date and the emojis used, in order to write it to an excel file
    

        if dataframes == 0:
            df_to_write = pd.DataFrame({'Date': str(date),
                                        'emoji_count' : em_count,
                                        'emoji_score': sentiment,
                                        'novak_score': novak_sentiment,
                                        'number_of_tweets': rows,
                                        'rockets' : rockets,
                                        'fires' : fires,
                                        'ticks' : ticks,
                                        'moneybags': moneybags,
                                        'up_stocks': up_stocks,
                                        'skulls': skulls,
                                        'down_stocks': down_stocks,
                                        'alerts': alerts,
                                        'down_arrows': down_arrows}, 
                                        index=[date])
            dataframes += 1

        else:
            second_df = pd.DataFrame({'Date': str(date),
                                      'emoji_count' : em_count,
                                      'emoji_score': sentiment, 
                                      'novak_score': novak_sentiment,
                                      'number_of_tweets': rows,
                                      'rockets' : rockets,
                                      'fires' : fires,
                                      'ticks' : ticks,
                                      'moneybags': moneybags,
                                      'up_stocks': up_stocks,
                                      'skulls': skulls,
                                      'down_stocks': down_stocks,
                                      'alerts': alerts,
                                      'down_arrows': down_arrows}, 
                                      index=[date])
            
            df_to_write = pd.concat([df_to_write, second_df])
            dataframes += 1

    #some extra steps to get extra datapoints
    av_tweets = df_to_write["number_of_tweets"].mean()
    df_to_write["abnormal_tweets"] = df_to_write["number_of_tweets"] - av_tweets
    av_sentiment = df_to_write['emoji_score'].mean()
    df_to_write["abnormal_emoji_score"] = df_to_write["emoji_score"] - av_sentiment
    df_to_write["w_novak_score"] = df_to_write["novak_score"].clip(df_to_write["novak_score"].quantile(0.05), df_to_write["novak_score"].quantile(0.95))
    df_to_write["cube_r_novak"] = (df_to_write["novak_score"] ** (1/3))
    df_to_write["novak_sentiment_per_emoji"] = (df_to_write["novak_score"] / df_to_write["emoji_count"])
    df_to_write["novak_sentiment_per_tweet"] = (df_to_write["novak_score"] / df_to_write["number_of_tweets"])
    return df_to_write

def file_writer(ticker, price_data, df_to_write, mkt_em):
    df_to_write["abnormal_sentiment_per_emoji"] = df_to_write["novak_sentiment_per_emoji"] - mkt_em["novak_sentiment_per_emoji"]
    df_to_write["abnormal_sentiment_per_tweet"] = df_to_write["novak_sentiment_per_tweet"] - mkt_em["novak_sentiment_per_tweet"]
    #df_to_write["cube_r_ab_sent_per_emoji"] = (df_to_write["abnormal_sentiment_per_emoji"] ** (1/3))
    #df_to_write["cube_r_ab_sent_per_tweet"] = (df_to_write["abnormal_sentiment_per_tweet"] ** (1/3))
    final_df = df_to_write.join(price_data)

    final_df.to_excel(f'../data/{ticker}.xlsx', index=False)

def get_price_data(ticker, df):
    ticker = f'{ticker}-USD'
    price_data = yf.download(ticker, start="2019-08-31", end="2019-11-27")
    price_data["tomorrow_volume"] = price_data["Volume"].shift(-1)
    price_data["tomorrow_volume_2"] = price_data["Volume"].shift(-2)
    price_data["yesterday_volume"] = price_data["Volume"].shift(1)
    price_data["returns"] = (price_data["Close"] - price_data["Open"])/price_data["Open"]
    price_data["percent_returns"] = price_data["returns"]*100
    price_data["tomorrow_returns"] = price_data["returns"].shift(-1)
    price_data["tomorrow_returns_2"] = price_data["returns"].shift(-2)
    price_data["yesterday_returns"] = price_data["returns"].shift(1)
    price_data["abnormal_returns"] = price_data["returns"] - df["mean_return"]
    price_data["tomorrow_abnormal_returns"] = price_data["abnormal_returns"].shift(-1)
    price_data["tomorrow_abnormal_returns_2"] = price_data["abnormal_returns"].shift(-2)
    price_data["yesterday_abnormal_returns"] = price_data["abnormal_returns"].shift(1)
    price_data["volatility"] = (np.log(price_data["High"]) - np.log(price_data["Low"]))
    price_data["tomorrow_volatility"] = price_data["volatility"].shift(-1)
    price_data["tomorrow_volatility_2"] = price_data["volatility"].shift(-2)
    price_data["yesterday_volatility"] = price_data["volatility"].shift(1)
    price_data["log_return"] = ((np.log(price_data["Close"])) / (np.log(price_data["Open"])))
    price_data["tomorrow_log_return"] = price_data["log_return"].shift(-1)
    price_data["tomorrow_log_return_2"] = price_data["log_return"].shift(-2)
    price_data["yesterday_log_return"] = price_data["log_return"].shift(1)
    price_data = price_data['2019-09-02':'2019-11-25']
    return price_data

def total_emoji_score():
    dataframes = 0
    tweetnos = []
    #Reads the tweets with selected symbol into a dataframe
    sql_query = pd.read_sql(f"SELECT * FROM tweets WHERE symbols IN ('BTC', 'ETH', 'LTC', 'NEO')", con)
    df = pd.DataFrame(sql_query)

    #Converts time_date column from object datatype to datetime datatype so pandas can perform datetime operations
    df['time_date'] = pd.to_datetime(df['time_date'], infer_datetime_format=True)

    #Removes the time section on the datetime, we just want date
    df['time_date'] = pd.to_datetime(df['time_date']).dt.normalize()

    #Gets unique datetimes from the DataFrame. These values will be used to aggregate emojis by the day they were tweeted
    dates = df.time_date.unique()

    for date in dates:
        df_day = df.loc[(df['time_date'] == f'{date}')]
        agg_emojis = ', '.join(df_day.emoji)
        em_count = em.emoji_count(agg_emojis)
        rows = df_day.shape[0]
        tweetnos.append(rows)
        sentiment = emoji_scorer(agg_emojis)
        novak_sentiment = novak_score(agg_emojis)
        rockets = individual_scorer('🚀', agg_emojis)
        fires = individual_scorer('🔥', agg_emojis)
        ticks = individual_scorer('✅', agg_emojis)
        moneybags = individual_scorer('💰', agg_emojis)
        up_stocks = individual_scorer('📈', agg_emojis)
        skulls = individual_scorer('💀', agg_emojis)
        down_stocks = individual_scorer('📉', agg_emojis)
        alerts = individual_scorer('🚨', agg_emojis)
        down_arrows = individual_scorer('🔻', agg_emojis)

        #Note agg_emojis type is 'str'

        #This creates a dataframe of the date and the emojis used, in order to write it to an excel file
    

        if dataframes == 0:
            df_to_write = pd.DataFrame({'Date': str(date),
                                        'emoji_count' : em_count,
                                        'emoji_score': sentiment,
                                        'novak_score': novak_sentiment,
                                        'number_of_tweets': rows,
                                        'rockets' : rockets,
                                        'fires' : fires,
                                        'ticks' : ticks,
                                        'moneybags': moneybags,
                                        'up_stocks': up_stocks,
                                        'skulls': skulls,
                                        'down_stocks': down_stocks,
                                        'alerts': alerts,
                                        'down_arrows': down_arrows}, 
                                        index=[date])
            dataframes += 1

        else:
            second_df = pd.DataFrame({'Date': str(date),
                                      'emoji_count' : em_count,
                                      'emoji_score': sentiment, 
                                      'novak_score': novak_sentiment,
                                      'number_of_tweets': rows,
                                      'rockets' : rockets,
                                      'fires' : fires,
                                      'ticks' : ticks,
                                      'moneybags': moneybags,
                                      'up_stocks': up_stocks,
                                      'skulls': skulls,
                                      'down_stocks': down_stocks,
                                      'alerts': alerts,
                                      'down_arrows': down_arrows}, 
                                      index=[date])
            
            df_to_write = pd.concat([df_to_write, second_df])
            dataframes += 1

    #some extra steps to get extra datapoints
    df_to_write["w_novak_score"] = df_to_write["novak_score"].clip(df_to_write["novak_score"].quantile(0.05), df_to_write["novak_score"].quantile(0.95))
    df_to_write["cube_r_novak"] = (df_to_write["novak_score"] ** (1/3))
    df_to_write["novak_sentiment_per_emoji"] = (df_to_write["novak_score"] / df_to_write["emoji_count"])
    df_to_write["novak_sentiment_per_tweet"] = (df_to_write["novak_score"] / df_to_write["number_of_tweets"])
    return df_to_write



#calling individual tickers just now vs calling get_tickers function for debugging reasons
#tickers = get_tickers()

ts = ['ETH', 'BTC', 'LTC', 'NEO']

m_df = mkt_return(FULL_TICKERS)
set_df = mkt_return(STUDY_TICKERS)
mkt_em = total_emoji_score()

mk2_em = mkt_em

for ticker in ts:

    price = get_price_data(ticker, m_df)
    other_data = emoji_aggregator(ticker)
    file_writer(ticker, price, other_data, mkt_em)

file_writer('MKT', set_df, mkt_em, mk2_em)


#TO-DO - add market cap data?
#      - add VIX?