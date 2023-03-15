import jsonlines
import csv

#counter for checking how many tweets we looked at and wrote to csv
tweetcount = 0

#Allow us to specify which file to open, and what file to output to. Note output file will be overwritten.
#If return key is pressed, default filenames are used
filename = input('Enter file path: ')
if len(filename) <= 1:
    filename = "5lines.jsonl"

outfile = input('Enter output CSV name: ')
if len(outfile) <= 1:
    outfile = "tester.csv"

#open the jsonl file and the csv file
with jsonlines.open(f"{filename}") as reader, open(outfile, 'w', newline='', encoding='utf-8') as output_file:

#try accessing full_text first, then if that fails, text, then if that fails just continue
#assign tweet text to variable - words
    for item in reader:
        symbs = []
        #try:
        if item["truncated"] == True:
            words = item["extended_tweet"]["full_text"]
            for symbol in item["extended_tweet"]["entities"]["symbols"]:
                symbs.append(symbol["text"])
        else:
            words = item["text"]
            for symbol in item["entities"]["symbols"]:
                symbs.append(symbol["text"])
        
        #if tweet has NO text fields whatsoever, can presume we have hit some non-tweet information in the larger jsonl files
        #except KeyError:
            #continue

        print(symbs)
        print('-------')
        tweetcount += 1
        
        
        
print(tweetcount)

#with open('../data/emoji_rankings_nonsig.csv', 'w', newline='', encoding='utf-8') as emoji_csv:
    #headers = ['Emoji', 'Times Used']
    #w = csv.writer(emoji_csv)
    #w.writerows(emoji_dictionary.items())


#print(f"Tweet count: {tweetcount} - 139518 expected \n")
#print(f"Emoji count: {emotecount} - 380324 expected \n")