import praw
import requests
from auth import user_agent, client_id, client_secret, username, password
import time

reddit = praw.Reddit(user_agent=user_agent,
                     client_id=client_id, client_secret=client_secret,
                     username=username, password=password)

subreddit = reddit.subreddit('wallstreetbets')

stock_list = requests.get("https://dumbstockapi.com/stock?exchanges=NYSE,NASDAQ,AMEX").json()
t0 = time.time()
tsla = ""
count = 0
for item in stock_list:
    count+=1
    if(item["ticker"]=="TSLA"):
        tsla = item
t1 = time.time()
print(count)
print(t1-t0)
#for comment in subreddit.stream.comments():
 #   print(comment.body)