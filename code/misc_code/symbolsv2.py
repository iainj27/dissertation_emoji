import jsonlines
import csv

symbol_dictionary = {}
tweetcount = 0
symbolcount = 0

#open the jsonl file and look at it line by line
#try accessing full_text first, then if that fails, text, then if that fails just continue
with jsonlines.open("../../data_original/full.jsonl") as reader:
    for item in reader:
        symbs = []
        try:
            symbs = item["extended_tweet"]["entities"]["symbols"]
        except KeyError:
            try:
                symbs = item["entities"]["symbols"]
            except KeyError:
                continue
        tweetcount += 1
        for s in symbs:
            symbol = s["text"].lower()
            symbolcount += 1
            if symbol not in symbol_dictionary:
                symbol_dictionary[symbol] = 1
            else:
                symbol_dictionary[symbol] += 1

with open('../old_data/symbol_rankings_all.csv', 'w', newline='') as symbol_csv:
    headers = ['symbol', 'Times Used']
    w = csv.writer(symbol_csv)
    w.writerows(symbol_dictionary.items())

print(f"Tweet count: {tweetcount} - 146133 or 5 expected \n")
print(f"Symbol count: {symbolcount} - ? or 19 expected \n")