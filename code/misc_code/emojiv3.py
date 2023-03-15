import jsonlines
import emoji
import csv
import pandas as pd

emoji_dictionary = {}
tweetcount = 0
emotecount = 0


#open the jsonl file and look at it line by line
#try accessing full_text first, then if that fails, text, then if that fails just continue
with jsonlines.open("../data/em_only_v2.jsonl") as reader:
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
            em_list = emoji.emoji_list(words)
            for em in em_list:
                emote = em["emoji"]
                if emote not in emoji_dictionary:
                    emoji_dictionary[emote] = 1
                else:
                    emoji_dictionary[emote] += 1


#with open('../data/emoji_rankings_nonsig.csv', 'w', newline='', encoding='utf-8') as emoji_csv:
   # headers = ['Emoji', 'Times Used']
   # w = csv.writer(emoji_csv)
  #  w.writerows(emoji_dictionary.items())

df = pd.DataFrame.from_dict(emoji_dictionary, orient='index')
df.to_excel('../data/all_emojis.xlsx')


print(f"Tweet count: {tweetcount} - 146133 expected \n")
print(f"Emoji count: {emotecount} - 451675 expected \n")