# -*- coding: utf-8 -*-

#    MIT License
#    
#    Copyright (c) 2018 Alexander Heilig, Dominik Sauter, Tabea Kiupel
#    
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#    
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.


#!bin/bash
twitter_imported = True
try:
    import json
except:
    import simplejson as json
try:
    from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
except ImportError:
    twitter_imported = False
    print('Error: No twitter module imported!')
#import csv
import unicodecsv as csv
import os

ACCESS_TOKEN = '935953290650640385-JzronD80EUdqZPtWzkMu9X36hAAkN5Z'
ACCESS_SECRET = 'lCVz26Fy3kiQY6r2EKTi82O0oJUnwOLqYxt146ihDTOD7'
CONSUMER_KEY = 'HoStbDyDPk818EkjmZnOxjZQF'
CONSUMER_SECRET = 'vFIiTUwR09hyeegT7utpGBFp0nECWFFNq24hyiViAbXTfBLXjI'


class TweetRetriever(object):
    """Class providing functionality for fetching tweet data from twitter.
    """
    
    def __init__(self):
        if (twitter_imported):
            self.oAuth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
            #Init connection to twitter streaming api
            self.twitter_stream = TwitterStream(auth=self.oAuth)
            self.twitter = Twitter(auth=self.oAuth)
        self.tweets = []

    def __tweet_not_deleted(self, tweet):
        """
        check if 'full_text' is a key of tweet
        only usable in tweet_mode 'extended'
        
        Args:
            tweet: twitter tweet dict
        """
        if 'full_text' in tweet:
            return True
        return False

    def retrieve_single_tweet(self, id):
        """
        Retrieves a single tweet, identified by its id from twitter
        
        Args:
            id: tweet id

        Returns:
            tweet: twitter tweet dict
        """
        print("looking up: %s"%id)
        tweet = self.twitter.statuses.show(tweet_mode='extended',id=id)
        return tweet

    def retrieve_list_of_tweets(self, ids):
        """
        Given a list of ids, retrieves the list of tweets from twitter
        
        Args:
            ids: list of tweet ids

        Returns:
            short_tweets: dict of id: text for each tweet
        """
        tweets = self.twitter.statuses.lookup(tweet_mode='extended',_id=ids)
        tweet_gen = [tweet for tweet in tweets if self.__tweet_not_deleted(tweet)]
        tweet_texts = [tweet["full_text"] for tweet in tweet_gen]
        tweet_ids = [tweet["id"] for tweet in tweet_gen]
        short_tweets = {}
        for tweet_text, tweet_id in zip(tweet_texts, tweet_ids):
            short_tweets[str(tweet_id)] = tweet_text
        return short_tweets

    def retrieve_sample_tweets(self, amount):
        """
        samples the amount latest tweets from twitter
        
        Args:
            amount: amount of tweets to retrieve from twitter

        Returns:
            iterator over tweets
        """
        iterator = self.twitter_stream.statuses.sample(tweet_mode='extended')
        return self.__retrieve_from_iterator(iterator, amount)

    def retrieve_specified_track_and_language(self, amount, track, languages=None):
        """
        samples the amount latest tweets from twitter given a keyword(track) and specified languages
        this lookup does not work with languages only, so track cannot be empty
        
        Args:
            amount: amount of tweets to retrieve
            track: keyword to seach for in tweets, i.e "Google", Google,Yahoo" for "Google" or "Yahoo", Google Twitter" for "Google" and "Twitter"
            languages: comma-separated list of BCP 47 language identifiers

        Returns:
            iterator over tweets
        """
        iterator = self.twitter_stream.statuses.filter(tweet_mode='extended',track=track, language=languages)
        return self.__retrieve_from_iterator(iterator, amount)

    def __retrieve_from_iterator(self, iterator, amount):
        """
        Args:
            iterator: iterate over desired tweets
            amount: amount of tweets to fetch

        Returns:
            short_tweets: dict containing id:text for each tweet
        """
        short_tweets = {}
        i = 0
        for tweet in iterator:
            #print(tweet.keys())
            if 'full_text' in tweet:
                short_tweets[str(tweet['id'])] = tweet['full_text']
                i += 1
            elif 'text' in tweet:
                short_tweets[str(tweet['id'])] = tweet['text']
                i += 1
            if i >= amount:
                break
        return short_tweets

    def __read_language_id_csv(self, csv_file):
        """
        reads list of tweet ids and their language saved in csv
        
        Args:
            csv_file: contains semicolon separated list of 'language, id'

        Returns:
            tweet_id_to_language: dict containing id: language
        """
        tweet_id_to_language = {}
        with open(csv_file, 'rb') as file:
            reader =  csv.reader(file, delimiter=';', encoding='utf-8')
            for row in reader:
                tweet_id_to_language[str(row[1])] = row[0]
        return tweet_id_to_language

    def read_tweets_from_file(self, csv_file):
        """
        Given a list of ids, retrieves all tweets
        
        Args:
            csv_file: contains language, id in each row

        Returns:
            tweets: dict containing id, text, language
        """
        tweet_id_to_language = self.__read_language_id_csv(csv_file)
        tweet_ids = list(tweet_id_to_language.keys())
#        tweet_lang = list(tweet_id_to_language.values())
        short_tweets = {}
        tweets = []
        for i in range(0,len(tweet_ids),80):
            short_tweets.update(self.retrieve_list_of_tweets(','.join(tweet_ids[i:i+80])))

            if(i%500==0):
                print("retrieved %d tweets"%len(short_tweets))
        for id, text in short_tweets.items():
            lang = tweet_id_to_language.get(id, None)
            if(lang is not None):
                tweets.append({'id':id,'text':text,'language':lang})
            else:
                print("language is none")
        return tweets

    # !!! UNUSED !!!
    def filter_by_language(self, tweets, lang):
        lang_tweets = []
        for tweet in tweets:
            print(tweet['language'])
            if(tweet['language'] == lang):
                lang_tweets.append(tweet)
        return lang_tweets

    def write_to_csv(self, file, tweets):
        """
        writes tweets retrieved from twitter via __read_tweets_from_file() to file
        
        Args:
            file: output file
            tweets: tweets to write to file
        """
        with open(file,'ab') as file:
            writer = csv.writer(file, delimiter=';')
            for tweet in tweets:
                to_write = [tweet['id'],tweet['text'],tweet['language']]
                print(to_write)
                writer.writerow(to_write)

def main():
    
    #cur_dir = os.path.dirname(os.path.abspath(__file__))
    #tweet_file = cur_dir+"\\..\\..\\data\\tweet_retriever_data\\recall_tweets.csv"
    #output_file = cur_dir + "\\..\\..\\data\\tweet_retriever_data\\downloaded\\recall_oriented_dl2.csv"
    tr = TweetRetriever()
    tweets = tr.retrieve_sample_tweets(4)
    print(tweets)
    #tweets = tr.read_tweets_from_file(tweet_file)
    #print(len(tweets))
    #tr.write_to_csv(output_file, tweets)

    #tweet_new = tr.retrieve_single_tweet("935995896637964290")
    #print(json.dumps(tweet_new))


if __name__ == '__main__':
    main()
    