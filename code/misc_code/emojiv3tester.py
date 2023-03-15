import jsonlines
import emoji
import csv

emoji_dictionary = {}
tweetcount = 0
emotecount = 0


#open the jsonl file and look at it line by line
#try accessing full_text first, then if that fails, text, then if that fails just continue
with jsonlines.open("5lines.jsonl") as reader:
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
        if tweetcount >= 1:
            break


with open('../data/test_nonsig.csv', 'w', newline='', encoding='utf-8') as emoji_csv:
    headers = ['Emoji', 'Times Used']
    w = csv.writer(emoji_csv)
    w.writerows(emoji_dictionary.items())


print(f"Tweet count: {tweetcount} \n")
print(f"Emoji count: {emotecount} \n")