# -*- coding:utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import os
import sys
import urllib
import configparser

save_path = os.path.abspath('./')

image_number = 0
count = 90
max_id = ''
check_url = []
twit_search_name = ''

# Twitterの設定を行います
def create_oath_session(consumer_key, consumer_secret, accsss_token, access_token_secret):
    oath = OAuth1Session(consumer_key, consumer_secret, accsss_token, access_token_secret)
    return oath

# TwitterからTwitteを取得します
def fav_tweets_get():
    url = "https://api.twitter.com/1.1/search/tweets.json"
    inifile = configparser.ConfigParser()
    inifile.read('./oath_key_dict.txt', 'UTF-8')
    twit_search_name = inifile.get('name', 'twit_search_name')
    params = {
        'q': twit_search_name + ' exclude:retweets',
        "count" : count,
        'max_id':max_id
    }
    oath = create_oath_session(inifile.get('settings', 'consumer_key'),
        inifile.get('settings', 'consumer_secret'),
        inifile.get('settings', 'accsss_token'),
        inifile.get('settings', 'access_token_secret'))
    response = oath.get(url, params = params)

    if response.status_code != 200:
        print("Error code : {0}".format(response.status_code))
        exit()
    tweets = json.loads(response.text)
    return tweets

# 画像を保存します
def image_saver(tweets):
    global image_number
    global max_id
    for tweet in tweets['statuses']:
        try:
            if  max_id == '' or int(max_id) >= tweet['id']:
                max_id = str(tweet['id'] - 1)
            image_list = tweet["extended_entities"]["media"]
            for image_dict in image_list:
                if (len(check_url) == 10):
                    break
                elif image_dict['type'] == 'photo':
                    url = image_dict["media_url"]
                    if url in check_url:
                        continue
                    with open(save_path + "/" + str(image_number) + "_" + os.path.basename(url), 'wb') as f:
                        img = urllib.request.urlopen(url, timeout=5).read()
                        f.write(img)
                    check_url.append(url)
                    image_number += 1
        except KeyError:
            # 画像でない場合は次のツイットへ
            continue
        except:
            # 想定外のエラーなので終了
            print("Unexpected error:", sys.exc_info()[0])
            exit()

if __name__ == "__main__":
    while (True):
        tweets = fav_tweets_get()
        image_saver(tweets)
        if (len(check_url) == 10):
            break