import praw
import requests
from auth import user_agent, client_id, client_secret, username, password
import time, string
import collections, json
from sentiment import Sentiment
from collections import defaultdict
#pip install with --user to avoid error

LOOKBACK_TIME_SECONDS = 2*60*60

reddit = praw.Reddit(user_agent=user_agent,
                     client_id=client_id, client_secret=client_secret,
                     username=username, password=password)

stock_list = requests.get("https://dumbstockapi.com/stock?exchanges=NYSE,NASDAQ,AMEX").json()
#get rid of annoying ticker
stock_list = [x for x in stock_list if len(x['ticker']) != 1]

#subreddits = ['investing', 'wallstreetbets', 'stocks']
subreddits = ['stocks', 'investing', 'wallstreetbets']

#get reddit comment data
comments = []
for sub in subreddits:
    print(f"getting from r/{sub}")
    comments.append(requests.get(f"https://api.pushshift.io/reddit/comment/search/?subreddit={sub}&size=100").json())
    last_utc = comments[-1]['data'][-1]['created_utc']
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_utc)))
    # incrementally get API data due to rate limit
    while(time.time() - LOOKBACK_TIME_SECONDS < last_utc):
        temp = requests.get(f"https://api.pushshift.io/reddit/comment/search/?subreddit={sub}&size=100&before={last_utc}").json()
        if(temp["data"]):
            comments.append(temp)
            last_utc = comments[-1]['data'][-1]['created_utc']
            print("cycling...", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_utc)))
            print(last_utc - time.time() + LOOKBACK_TIME_SECONDS)
        else:
            print(f"finished getting from r/{sub}")
            break
stock_dict = defaultdict(int)
temp = Sentiment()
temp.train()

for data in comments:
    arr = data['data']
    for chunk in arr:
        # format commets into set
        text = chunk['body'].lower()
        text_no_punct = text.translate(str.maketrans('', '', string.punctuation))
        text_arr = text_no_punct.split(" ")
        for i in range(len(text_arr)):
            if(not text_arr[i].isupper()):
                text_arr[i] = text_arr[i].lower()
        text_set = set(text_arr)
        for item in stock_list:
            #check if ticker is present in comment
            if(item["ticker"] in text_set):
                pos_neg = temp.test(text)
                if(stock_dict[item["ticker"]]==0):
                    # format: Ticker symbol, total positive, total negative, total number
                    stock_dict[item["ticker"]] = [pos_neg[0], pos_neg[1], 1]
                else:
                    stock_dict[item["ticker"]] = [stock_dict[item["ticker"]][0]+pos_neg[0], 
                                                stock_dict[item["ticker"]][1]+pos_neg[1], 
                                                stock_dict[item["ticker"]][2]+1]
                                                

for key, val in stock_dict.items():
    val[0] = int((val[0]/val[2])*100)/100
    val[1] = int((val[1]/val[2])*100)/100

print(stock_dict)