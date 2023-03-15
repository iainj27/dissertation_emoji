import jsonlines
import emoji

emotecount = 0
tweetcount = 0
tweets_with_emoji = 0
emoji_dictionary = {}

with jsonlines.open("../../data/full.jsonl") as reader:
    for item in reader:
        try:
            words = item["extended_tweet"]["full_text"]
        except KeyError:
            try:
                words = item["text"]
            except KeyError:
                continue
        tweetcount += 1
        count = emoji.emoji_count(words)
        if count > 0:
            emotecount += count
            tweets_with_emoji += 1
            em_list = emoji.emoji_list(words)
            

        

print(f'\n total emotes = {emotecount}')
print(f'\n total tweets = {tweetcount}')
print(f'\n total tweets with emojis = {tweets_with_emoji}')
print(f'\n proportion of tweets with emoji = {(tweets_with_emoji/tweetcount)*100} %')
print(f'\n average emojis per tweet_with_emoji = {emotecount/tweets_with_emoji}')
print('\n done')

