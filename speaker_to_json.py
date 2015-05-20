import re,json
import string
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter


def make_doc_json(text,index_json):
	
	wordnet_lemmatizer=WordNetLemmatizer()
	
	####the text processing is broken. I'm changing the order now.
	
	text = " %s " %text

	
	#remove spurious periods
	#in order to avoid spurious sentence breaks as a result of Mr. Mrs. middle initials etc. etc., strip those periods out before splitting the sentences.
	text = re.sub('Mr\.','Mr',text)
	text = re.sub('Mrs\.','Mr',text)
	text = re.sub('Ms\.','Ms',text)
	text = re.sub('Ph\.D\.','PhD',text)
	text = re.sub('B\.A\.','BA',text)
	text = re.sub('M\.A\.','MA',text)
	text = re.sub('B\.S\.','BS',text)
	text = re.sub('Mrs\.','Mrs',text)
	text = re.sub('Ret\.','Ret',text)
	text = re.sub('etc\.','Ret',text)
	text = re.sub('(p\.m\.|P\.M\.)','pm',text)
	text = re.sub('v\.','v',text)
	text = re.sub('U\.S\.','US',text)
	text = re.sub(' U\. S\. ',' US ',text)
	#tags that oftentimes attend the discussion of specific pieces of legislation
	text = re.sub('U\.S\.C\.','USC',text)
	text = re.sub(' SEC\.','',text)
	text = re.sub(' seq\.',' seq',text)
	text = re.sub(' [0-9]+[A-Z]+\.','',text)
	#bill titles are in caps and followed by periods
	text = re.sub('(?<=[A-Z]{3})\.','',text)
	#decimals in figures
	text = re.sub('(?<=[0-9])\.[0-9]+','',text)
	text = re.sub('(?<=[0-9])\.','',text)
	text = re.sub('\s+',' ',text)
	text = re.sub('(?<=[A-Z])\.','',text)
	
	#get sentences
	sentences_list = text.split('.')
	sentences_list = [sent for sent in sentences_list if sent not in ['.','',' ','  ']]
	final_sentences_list = [re.sub("^\s*","","%s." %sent) for sent in sentences_list]
	

	minimized_scored_sentences = {}
	minimized_sentences = {}
	
	s_counter = 0
	for s in sentences_list:
		
		sent = s.lower()		
		
		#remove possessive s's, remove "t" contractions
		sent = re.sub("\'s "," ",sent)
		sent = re.sub(" [a-z]+\'t"," ",sent)
		#remove bad characters
		badchars = string.punctuation
		for b in badchars:
			sent = sent.replace(b," ")
		sent = sent.replace("  "," ")
		

		
		##remove stopwords
		sw = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now']
		
		additional_stopwords = ['senator','speaker','position','opinion','opinions','thought','thoughts','feel','feelings','great','worse','best','have','get']
		
		sw += additional_stopwords
		
		#build the fully minimized words list
		mw = sent.split(" ")
		try:
				mw.remove("")
		except:
			pass
		mw = [wordnet_lemmatizer.lemmatize(i,pos='v') for i in mw if i not in sw]
		
		
		#now reconstitute into a minimized sentence
		ms = str()
		for w in mw:
			ms += ' %s' %w
		#and remove the leading space
		ms = ms[1:]
		
		##The transcripts are pretty standardized, so the regex scrubbers up top do a solid job -- but if it's breaking, unquote the below to start testing where.
		'''if mw in [[],['']]:
			#print surrounding sentences
			sentence_idx = sentences_list.index(s)
			checker = sentence_idx - 1
			while checker <= sentence_idx +1:
				print sentences_list[checker]
				checker += 1
			#print the offending sentence
			print "------------%s-------------" %s
			#print the output
			print "------------%s-------------" %mw
			print index_json["id"]'''

		
		minimized_sentences[s_counter] = ms
		minimized_scored_sentences[s_counter] = dict(Counter(mw))
		s_counter += 1
	
	
	minimized_text = str()
	for msk in minimized_sentences.keys():
		minimized_text += ' %s' %minimized_sentences[msk]
	

	#pull bigrams and trigrams that appear more than once in the minimized text, and add them into the minimized scored sentences list	
	
	minimized_text_list = minimized_text.split(' ')
	try:
		minimized_text_list.remove('')
	except:
		pass
	minimized_scored_text = dict(Counter(minimized_text_list))
	
	
	for msk in minimized_sentences.keys():
		sentence = minimized_sentences[msk]
		sentence_token = word_tokenize(sentence)
		sentence_bigrams = ["%s %s" %(n[0],n[1]) for n in ngrams(sentence_token,2)]
		sentence_trigrams = ["%s %s %s" %(n[0],n[1],n[2]) for n in ngrams(sentence_token,3)]
		
		good_bigrams = [re.findall(sb,minimized_text) for sb in sentence_bigrams]
		good_bigrams = [g[0] for g in good_bigrams if len(g)>1]
		good_trigrams = [re.findall(sb,minimized_text) for sb in sentence_trigrams]
		good_trigrams = [g[0] for g in good_trigrams if len(g)>1]
		
		
		
		if good_bigrams != []:
			for b in good_bigrams:
				minimized_scored_sentences[msk][b] = 25
				'''for w in b.split(' '):
					try:
						minimized_scored_text[w] -= 1
					except:
						pass'''
				try:
					minimized_scored_text[b] = 25
				except:
					minimized_scored_text[b] += 25
		if good_trigrams != []:
			for t in good_trigrams:
				minimized_scored_sentences[msk][t] = 50
				'''for w in b.split(' '):
					try:
						minimized_scored_text[w] -= 1
					except:
						pass'''
				try:
					minimized_scored_text[t] = 50
				except:
					minimized_scored_text[t] += 50
		
	
	
	##get metadata from the json
	ij = index_json

	
	document_json = {"document_text":{"minimized_tallied_text":""},"indexed_sentences":{"full_sentences":[],"minimized_tallied_sentences":[]}}
	
	
	'''document_json["document_text"]["full_text"] = text'''
	document_json["indexed_sentences"]["full_sentences"] = final_sentences_list
	document_json["document_text"]["minimized_tallied_text"] = minimized_scored_text
	document_json["indexed_sentences"]["minimized_tallied_sentences"] = minimized_scored_sentences
	
	#add metadata (note on "original id") -- can be used to see if the original file has been split because of multiple topics being addressed
	document_json["metadata"] = {"original_id":ij["id"],"date":ij["date"],"title":ij["title"],"url":ij["url"]}
		
	return document_json

def get_corpus_stats(docs_json):
	
	total_wordcount = 0
	corpus_count = {}
	
	for doc_id in docs_json.keys():
		doc_word_scores = docs_json[doc_id]["document_text"]['minimized_tallied_text']
		for word in doc_word_scores.keys():
			if word != '':
				word_score = doc_word_scores[word]
				try:
					corpus_count[word] += word_score
				except:
					corpus_count[word] = word_score
				total_wordcount += word_score
	
	return {"words":corpus_count,"total_wordcount":total_wordcount}






def main(filename):
	
	d = open(filename,'r')
	t = d.read()
	j = json.loads(t)
	
	keys = j.keys()
	
	output_json = {'corpus':{},'documents':{}}
	
	doc_count = 0
	failed_count = 0
	progress_b = 0
	
	for k in keys:
		
		id = j[k]['id']
		
		
		open_fail=0
		try:
			f = open('speaker/%s.txt' %id,'r')
			text = f.read()
			f.close()
		except:
			'''print "File not found %s" %id'''
			failed_count += 1
			open_fail=1

		if open_fail == 0:
			##remove linebreaks
			text = re.sub("\s*\n\s*"," ",text)
			##remove ellipses
			text = text.replace(". . .","")
	
			##Oftentimes in a given piece, a speaker will deal with multiple topics. When those topics are sufficiently unrelated, just add "<break>" between them. the id will have alpha designators appended (a,b,c,&c.)
			text_list = text.split("<break>")
			doc_split_count = 0
	
			for i in text_list:
		
				if len(text_list)>1:
					this_id = "%s-%s" %(id,string.uppercase[doc_split_count])
					doc_split_count += 1
				else:
					this_id = id

		
				document = make_doc_json(i,j[k])
				output_json['documents'][id] = document
			
			doc_count += 1
			if doc_count - progress_b == 25:
				progress_b = doc_count
				print "processed %s" %(str(doc_count))
								
				
			
		
			
			

	
	corpus_stats = get_corpus_stats(output_json['documents'])
	
	output_json['corpus'] = corpus_stats
	
	print "Processed %s (with %s failures) out of %s" %(str(doc_count),str(failed_count),str(len(keys)))
	
	
	final = json.dumps(output_json)
	
	out = open('heroku/final.json','w')
	out.write(final)
	out.close()