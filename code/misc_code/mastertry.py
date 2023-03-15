import jsonlines
import sqlite3
import emoji

#set up counter variables for debugging, knowing how many lines have been read/written
tweetsread = 0
tweetsfound = 0

commits = 0
#Defines what cashtag to search for. If enter key pressed/no input then default set to ETH
#symbol = input("Enter symbol to search for... ")
#if len(symbol) <= 1:
    #symbol = "ETH"

#Connect to sqlite database
con = sqlite3.connect('emote_tweets.db')
cursor = con.cursor()

#Create SQL table
cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (time_date TEXT, tweet_text TEXT, emoji TEXT, symbols TEXT)''')

with jsonlines.open("../data/em_only_v2.jsonl") as reader:
    for item in reader:
        tweetsread += 1
        symbs = []
        emojis = []
        if item["truncated"] == True:
            words = item["extended_tweet"]["full_text"]
            for symbol in item["extended_tweet"]["entities"]["symbols"]:
                symbs.append(symbol["text"])
        else:
            words = item["text"]
            for symbol in item["entities"]["symbols"]:
                symbs.append(symbol["text"])
        
        date = item["created_at"]
        emojidict = emoji.emoji_list(words)
        for i in emojidict:
            emojis.append(i['emoji'])

        symbs = [sym.upper() for sym in symbs]

        cursor.execute("INSERT INTO tweets VALUES (?,?,?,?)", (date, str(words), ', '.join(emojis), ', '.join(symbs)))

        commits += 1
        if commits >= 500:
            con.commit()
            commits = 0

con.commit()
con.close()

print(f"Done! --- {tweetsread} tweets read")
