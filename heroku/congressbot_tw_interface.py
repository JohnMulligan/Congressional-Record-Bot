from __future__ import division
import twitter
import json
from OAuthSettings import settings
import time
import re,json
import string
from nltk.stem import WordNetLemmatizer
from collections import Counter
import numpy as np
import operator
from nltk.util import ngrams
from collections import Counter
from nltk import word_tokenize

consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token_key = settings['access_token_key']
access_token_secret = settings['access_token_secret']


def minimize_string(raw_text):
	
	#lower
	query_string = raw_text.lower()
	
	
	#remove usernames
	query_string = re.sub("@[a-z|_]+","",query_string)
	
	
	#get rid of punctuation
	punct = string.punctuation
	for p in punct:
		query_string = query_string.replace(p,' ')
	
	#remove urls
	query_string = re.sub("http.*? ","",query_string)
	
	
	#remove duplicate spaces
	query_string = query_string.replace('  ',' ')
	
	
	words_list = query_string.split(" ")
	words_list = [w for w in words_list if w != " "]
	
	
	sws = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now']
	
	johns_stopwords = ['sanders','senator','policy','position','opinion','feel','think','should']
	
	sws += johns_stopwords
	
	words_list = [w for w in words_list if w not in sws]
	
	
	#lemmatize
	wordnet_lemmatizer = WordNetLemmatizer()
	
	
	processed_list = [wordnet_lemmatizer.lemmatize(w,pos='v') for w in words_list]
	
	
	minimized_sentence = str()
	
	
	for w in processed_list:
		minimized_sentence += " %s" %w
	
	processed_list = [i for i in processed_list if i != '']
	
	tallied_query_dict = Counter(processed_list)
	
	
	
	#add in bigrams & trigrams
	sentence_token = word_tokenize(minimized_sentence)
	sentence_bigrams = ["%s %s" %(n[0],n[1]) for n in ngrams(sentence_token,2)]
	sentence_trigrams = ["%s %s %s" %(n[0],n[1],n[2]) for n in ngrams(sentence_token,3)]	
	
	
	if sentence_bigrams != []:
			for b in sentence_bigrams:
				tallied_query_dict[b] = 25
				'''for w in b.split(' '):
					try:
						minimized_scored_text[w] -= 1
					except:
						pass'''
				try:
					tallied_query_dict[b] = 25
				except:
					tallied_query_dict[b] += 25
	if sentence_trigrams != []:
			for t in sentence_trigrams:
				tallied_query_dict[t] = 50
				'''for w in b.split(' '):
					try:
						minimized_scored_text[w] -= 1
					except:
						pass'''
				try:
					tallied_query_dict[t] = 50
				except:
					tallied_query_dict[t] += 50
	
	
	return tallied_query_dict


def score_items(documents_json,corpus_json,scored_input_list,json_key_1='',json_key_2=''):
	
	total_wordcount = corpus_json['total_wordcount']
	corpus_words = corpus_json['words']
	'''average_score = sum(corpus_words.values())/(len(corpus_words.keys()))'''

	keys = documents_json.keys()
	output_scores = {}
	for k in keys:
		
		if json_key_1 != '':
			index_json_scored_list = documents_json[k][json_key_1][json_key_2]
		else:
			index_json_scored_list = documents_json[k]
			
		'''print index_json_scored_list.keys()
		print scored_input_list.keys()'''
		
		this_item_scores =[]
		'''print scored_input_list
		print index_json_scored_list'''
		for si in scored_input_list.keys():
			if si in index_json_scored_list.keys():
				this_score_idx = total_wordcount/(corpus_words[si])
				this_score = (scored_input_list[si]**2)*(index_json_scored_list[si]**2)*(this_score_idx**2)
				this_item_scores.append(this_score)
			else:
				this_item_scores.append(0)
						

		this_item_score = np.average(this_item_scores)
		
		if this_item_score > 0:
			output_scores[k] = this_item_score
	
	scores_no_keys = [output_scores[k] for k in output_scores.keys()]
	'''print max(scores_no_keys)'''
	return output_scores





def choose_item(score_dict):

	
	arr = score_dict.keys()
	weights = [score_dict[key] for key in arr]
	
	processed_weights = [w/len(arr) for w in weights]
	
	probs = np.array(processed_weights)
	probs /= probs.sum()
	

	choice = np.random.choice(arr, 1, replace=False, p=probs)
	return choice



	
def choose_sentences(chosen_article_full_sentences,choice_index,n=3):
	
	full_sent = chosen_article_full_sentences
	
	if n==3:
		if choice_index == 0:
			output = "%s %s %s" %(full_sent[0],full_sent[1],full_sent[2])
		elif choice_index == len(full_sent)-1:
			output = "%s %s %s" %(full_sent[-3],full_sent[-2],full_sent[-1])
		else:
			output = "%s %s %s" %(full_sent[choice_index-1],full_sent[choice_index],full_sent[choice_index+1])
	if n==2:
		if choice_index == 0:
			output = "%s %s" %(full_sent[0],full_sent[1])
		elif choice_index == len(full_sent)-1:
			output = "%s %s" %(full_sent[-2],full_sent[-1])
		else:
			output = "%s %s" %(full_sent[choice_index-1],full_sent[choice_index])
	if n==1:
		output = full_sent[choice_index]
	
	return output


def twitterize(final_sentences,replytouser,document_json,url_length,max_length=10):


	output_tweets = []
	
	tweet_count = 1
	
	if len(final_sentences) + len(replytouser) + 4 < 140 and replytouser != '':
		output_tweets.append("@%s %s" %(replytouser,final_sentences))
	else:
		
		char_idx = 0
		text_block = final_sentences
	
	
		while tweet_count <= max_length:
			tweetstring = str()
			if tweet_count ==1 and replytouser != '':
				tweetstring = "@%s " %replytouser
		
			try:
				remaining_chars = 134 - len(tweetstring)
				text_block[remaining_chars]
			except:
				tweetstring = "%s (%s/%s)" %(text_block,str(tweet_count),str(tweet_count+1))
				output_tweets.append(tweetstring)
				break
		
			#find first available space
			space_lookup = remaining_chars-1
			space_idx = -1
		
			while space_idx == -1:
				space_idx = text_block.rfind(" ",space_lookup,remaining_chars)
				space_lookup -=1
		
			tweetstring += "%s (%s/NNN)" %(text_block[0:space_idx],str(tweet_count))
		
			text_block = text_block[space_idx+1:]

			output_tweets.append(tweetstring)
		
			tweet_count += 1
	
	print output_tweets
	
	if tweet_count ==1:
		output_tweets = [re.sub('\([0-9]+/NNN\)','',t) for t in output_tweets]
	else:
		output_tweets = [re.sub('(?<=/)NNN',str(tweet_count+1),t) for t in output_tweets]
	
	url = "http://www.congress.gov%s" %document_json['metadata']['url']
	date = document_json['metadata']['date']
	title = document_json['metadata']['title'].title()
	
	look_backwards_idx=len(title)-1
	source_info_tweet = "Source: %s -- %s\n%s (%s/%s)" %(title,date,url,str(tweet_count+1),str(tweet_count+1))
	while len(title) + len(date) + url_length + 15 > 140:
	
		last_space_idx = title.rfind(" ",look_backwards_idx)
		if last_space_idx == -1:
			look_backwards_idx -=2
		else:
			title = "%s..." %title[:last_space_idx]
			look_backwards_idx = len(title)-1
		source_info_tweet = "Source: %s -- %s\n%s (%s/%s)" %(title,date,url,str(tweet_count+1),str(tweet_count+1))
	
	output_tweets.append(source_info_tweet)
	
	return output_tweets
	
















def speaker_main(query_string,user_id,n=3,url_length=22):
	
	
	#minimize and score text
	tallied_query_list = minimize_string(query_string)
	
	
	
	
	
	#get article scores
	e = open('final.json')
	t = e.read()
	j = json.loads(t)
	e.close()
	
	
	documents_json = j['documents']
	corpus_json = j['corpus']
	
	
	art_scores = score_items(documents_json,corpus_json,tallied_query_list,"document_text","minimized_tallied_text")
	
	
	chosen_article = str(choose_item(art_scores)[0])
	#score sentences
	sentence_scores = score_items(documents_json[chosen_article]['indexed_sentences']['minimized_tallied_sentences'],corpus_json,tallied_query_list)
	#choose output sentences
	
	
	chosen_sentence_idx = int(choose_item(sentence_scores)[0])
	#turn this on to check that the correct sentence is actually being selected. if not, something is screwed up in the app that produced the json output
	'''print j['documents'][chosen_article]['indexed_sentences']['full_sentences'][chosen_sentence_idx]
	print j['documents'][chosen_article]['indexed_sentences']['minimized_tallied_sentences'][str(chosen_sentence_idx)]'''
	
	

	final_sentences = choose_sentences(documents_json[chosen_article]['indexed_sentences']['full_sentences'],chosen_sentence_idx,n)
	
	tweets = twitterize(final_sentences,user_id,documents_json[chosen_article],url_length)

	return tweets









def speaker_tweets_independently():

	twitter_api = get_twitter_api()
	
	timeline_tweets = twitter_api.GetHomeTimeline(count=50)
	
	tweets_texts = [i.text.encode('ascii',errors='ignore') for i in timeline_tweets]
	timeline_text = str()
	for i in tweets_texts:
		timeline_text += i.encode('ascii',errors='ignore') + "."
	
	response_tweets = speaker_main(str(timeline_text),'',n=1)
	
	attempts = 1
	
	while attempts <4:
		response_tweets = speaker_main(str(timeline_text),'',n=2)		
		d = open('response_log.json', 'r')
		t = d.read()
		d.close()
		j = json.loads(t)
		
		
		logged_texts = [j[k] for k in j]
		
		duplicate=0
		for ts in tweets_texts:
			if ts in logged_texts:
				duplicate = 1
				attempts += 1
				if attempts >= 4:
					response_tweets=[]
		if duplicate == 0:
			break
	
	return response_tweets










def log_responses(response):
    d = open('response_log.json', 'r')
    t = d.read()
    d.close()
    j = json.loads(t)
    j[response.id] = response.text
    e = open('response_log.json', 'w')
    out = json.dumps(j)
    e.write(out)
    e.close()

def post_tweets(s,start_id=''):
	twitter_api = get_twitter_api()
	id = start_id
	for tweet in s:
		while True:
			try:
				if id != '':
					response = twitter_api.PostUpdate(status=tweet,in_reply_to_status_id=id)
				else:
					response = twitter_api.PostUpdate(status=tweet)
				log_responses(response)
				id = response.id
				break
			except twitter.TwitterError as inst:
				e = inst
				message = s.message[0]['message']
				##tweet the whole thing out.
				if message =='Rate limit exceeded.':
					timeout(300,"rate limit exceeded")
				
				elif message == 'Status is a duplicate.':
					##if i get duplicates on the final, sourcing tweets (it's already happened), then i should just change something minor (here, removing the last word) and then circle back and try again
					if s.index(tweet) == len(s)-1:
						tweet = re.sub(' [^ ]+\n(?=https://)','\n',tweet)
					##if i get duplicates on non-final tweets, then just exit.
					else:
						print "Duplicate tweet: %s" %tweet
						return response
				else:
					return response
	
	return response
    

def get_twitter_api():
	
	twitter_api = twitter.Api(consumer_key = consumer_key, consumer_secret = consumer_secret, access_token_key = access_token_key, access_token_secret = access_token_secret)
	
	return twitter_api


def timeout(s,message=""):
	 
	 print "%s Pausing %s seconds" %(message,str(s))
	 start = time.time()
	 
	 elapsed = 0
	 
	 while elapsed < s:
	 	elapsed = (time.time() - start)
	 print "resuming"

def get_new_mentions(min_id):
	
	
	'''d = open('logged_mentions.json','r')
	t = d.read()
	d.close()
	j = json.loads(t)
	
	newest_known_mention = max([int(i) for i in j.keys()])
		
	logged_mentions = j.keys()'''
	
	twitter_api = get_twitter_api()
	
	mentions = twitter_api.GetMentions(since_id=min_id)
	
	new_mentions = [{"user":i.user.screen_name,"status_id":i.id,"text":i.text} for i in mentions if int(i.id)>(min_id)]	
	
	'''for new_mention in new_mentions:
		j[new_mention['status_id']] = new_mention['user']'''
	
	print new_mentions
	
	'''output_json = json.dumps(j)
	d = open('logged_mentions.json','w')
	d.write(output_json)'''
	
	
	return new_mentions



if __name__ == "__main__":
	cycles_without_tweets = 0
	trigger = 120
	
	last_tweet_id = 0
	
	while last_tweet_id == 0:
		twitter_api = get_twitter_api()
		timeline = twitter_api.GetHomeTimeline()
		ids = [int(i.id) for i in timeline]	
		last_tweet_id = max(ids)
		print last_tweet_id
	
	while True:
		
		response = {}
		
		tweeted_this_cycle = 0
		try:
			print "checking"
			new_mentions = get_new_mentions(last_tweet_id)
			if len(new_mentions) > 0:
				tweeted_this_cycle = 1
				print "found %s new interactions" %str(len(new_mentions))
				for new_mention in new_mentions:
					
					try:
						print new_mention
						response_tweets = speaker_main(new_mention['text'],new_mention['user'])
						print "response tweets = %s" %str(response_tweets)
					except:
						print "bernie had nothing to say"
						response = post_tweets(["@%s I've got nothing on that. Maybe rephrase?" %new_mention['user']],new_mention['status_id'])
					try:
						response = post_tweets(response_tweets,new_mention['status_id'])
						print "replied to %s with %s new tweets" %(new_mention['user'],str(len(response_tweets)))
					except:
						last_tweet_id = new_mention['status_id']


			if tweeted_this_cycle == 0:
				cycles_without_tweets += 1
			else:
				cycles_without_tweets = 0
				
			if cycles_without_tweets >= trigger:
				print "bernie has gone %s cycles without a query. now tweeting unprompted." %str(trigger)
				cycles_without_tweets = 0
				unprompted_tweets = speaker_tweets_independently()
				
				if unprompted_tweets!=[]:
					response = post_tweets(unprompted_tweets)
				else:
					print "bernie had nothing new to say"
			timeout(60)
		except:
			timeout(300,"error getting mentions")
			cycles_without_tweets += 1
		
		try:
			last_tweet_id = int(response.id)
			print "Last tweet id = %s" %str(last_tweet_id)
		except:
			pass
		