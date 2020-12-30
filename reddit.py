import requests
from auth import user_agent, client_id, client_secret, username, password
import time, string, sys
import collections, json
from sentiment import Sentiment
from collections import defaultdict
from pandas_datareader.data import DataReader
import datetime
from datetime import date, timedelta, timezone
#pip install with --user to avoid error

LOOKBACK_TIME_SECONDS = 24*60*60
# year, month, day, hour, minute, second, milisecond // utc is 5 hours head of EST, start collecting at 4:00 EST
START_DATE_UTC = int(datetime.datetime(2020, 12, 29, 21, 0, 0, 0).replace(tzinfo=timezone.utc).timestamp())
NUM_DAYS_AGO = 0

start_time = time.time()

stock_list = requests.get("https://dumbstockapi.com/stock?exchanges=NYSE,NASDAQ,AMEX").json()
#get rid of annoying tickers
stock_list = [x for x in stock_list if len(x['ticker']) != 1]

#subreddits = ['investing', 'wallstreetbets', 'stocks']
subreddits = ['wallstreetbets', 'investing', 'stocks']

#get reddit comment data
comments = []
for sub in subreddits:
    print(f"getting from r/{sub}")
    last_utc = START_DATE_UTC
    # incrementally get API data due to rate limit
    while(START_DATE_UTC - last_utc < LOOKBACK_TIME_SECONDS):
        while(True):
            try:
                response = requests.get(f"https://api.pushshift.io/reddit/comment/search/?subreddit={sub}&size=100&before={last_utc}").json()
                comments.append(response)
                break
            except:
                print(f"error, retrying https://api.pushshift.io/reddit/comment/search/?subreddit={sub}&size=100&before={last_utc}")
        
        last_utc = comments[-1]['data'][-1]['created_utc']
        print("cycling...", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_utc)))
        print(round(LOOKBACK_TIME_SECONDS - START_DATE_UTC + last_utc, 2))
stock_dict = defaultdict(int)
sentiment = Sentiment()
sentiment.train()

print(f"parsing {len(comments)*100} comments...")
for data in comments:
    arr = data['data']
    for chunk in arr:
        # format commets into set
        text = chunk['body']
        text_no_punct = text.translate(str.maketrans('', '', string.punctuation))
        text_arr = text_no_punct.split(" ")
        text_set = set()
        for word in text_arr:
            if(word.isupper() and word!="I"):
                #if $ symbol is used in comment
                if(word[0] == '$'):
                    text_set.add(word[1:])
                else:
                    text_set.add(word)
        if(not text_set or chunk["score"]<=0):
            continue
        for item in stock_list:
            #check if ticker is present in comment
            if(item["ticker"] in text_set):
                pos_neg = sentiment.test(text)
                # set maximum weight for score
                score = chunk["score"] if chunk["score"] < 5 else 5
                if(stock_dict[item["ticker"]]==0):
                    # format: Ticker symbol, total positive, total negative, total number
                    stock_dict[item["ticker"]] = [pos_neg[0]*score, pos_neg[1]*score, score]
                else:
                    stock_dict[item["ticker"]] = [stock_dict[item["ticker"]][0]+pos_neg[0]*score, 
                                                stock_dict[item["ticker"]][1]+pos_neg[1]*score, 
                                                stock_dict[item["ticker"]][2]+score]

print("finalizing data...")                                                
output = []
date = date.today() - timedelta(days=NUM_DAYS_AGO)
for key, val in stock_dict.items():
    #limit min number of ppl per stock
    if(val[2] > 3):
        #if symbol isn't registered in yahoo finance, skip
        try:
            data = round(DataReader(key, 'yahoo', date)['Adj Close'][0], 2)
            output.append([key, int((val[0]/val[2])*100)/100, int((val[1]/val[2])*100)/100, data, val[2]]) 
        except:
            continue
output = sorted(output, key=lambda x: x[4], reverse=True)

output_file = open('reddit_data.txt', 'a')
formatted_date = date.strftime("%m/%d/%y")
print(formatted_date, sep="\n", file=output_file)
print(*output, sep="\n", file=output_file)
print(f"Total time elapsed: {round(time.time() - start_time, 2)} seconds")