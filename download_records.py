import re,urllib,time
from optparse import OptionParser, Option, OptionValueError
import json
import os


parser = OptionParser()
parser.add_option("-u", action="store", type="str", dest="url")
parser.add_option("-s", action="store", type="str", dest="speakername")
(options, args) = parser.parse_args()

def get_page_items(page_source,url):
	
	items_list = []

	results_block = re.search("<ol class=\"results_list\".*?</ol>",page_source,re.S).group(0)

	results_list = re.findall("(?<=<li>).*?(?=</li>)",results_block,re.S)

	for i in results_list:
		h2 = re.sub("\'","",re.search("<h2>.*</h2>",i,re.S).group(0))
		title = re.search("(?<=\">).*?(?=</a>)",h2,re.S).group(0)
		url = re.search("(?<=<a href=\").*?(?=\")",h2,re.S).group(0)
		
		id_pt1 = re.sub("/","-",re.search("[0-9]{4}/[0-9]{2}/[0-9]{2}",url).group(0))
		id_pt2 = re.search("(?<=/article/).*?(?=/$)",url).group(0)
		id = "%s-%s" %(id_pt1,id_pt2)
		this_item = {"title":title,"url":url,"date":id_pt1,"id":id}
		items_list.append(this_item)

	return items_list
'''	except:
		print "Error getting page items.\nURL=%s" %url'''


def timeout(s):
	 
	 print "Pausing %s seconds" %str(s)
	 start = time.time()
	 
	 elapsed = 0
	 
	 while elapsed < s:
	 	elapsed = (time.time() - start)
	 print "resuming"



def pull_transcripts(filename):
	d = open(filename,'r')
	t = d.read()
	
	j = json.loads(t)
	keys = j.keys()
	
	if not os.path.exists('transcripts'):
		os.makedirs('transcripts')
	
	
	count = 1
	
	for k in keys:
		
		name = k
		item = j[k]
		
		try:
			q = open('transcripts/%s.txt' %name,'r')
			print "File already logged: %s" %name
			count += 1
		except:
			try:
				url = item['url']		
				url = 'https://www.congress.gov' + url
				page = urllib.urlopen(url)
				html = page.read()
				transcript_text = re.search("(?<=<div class=\"txt-box\">).*?(?=</div>)",html,re.S).group(0)
		
				transcript_text = re.sub('\s+_+\s+</pre>','',transcript_text,re.S)
				transcript_text = re.sub('\s*<pre class="styled">\s+','',transcript_text,re.S)
		
				e = open('transcripts/%s.txt' %name,'w')
				e.write(transcript_text)
				e.close()
				print "%s of %s" %(str(count),str(len(keys)))
		
				count += 1
				timeout(5)
			except:
				print "error downloading item: %s" %item




if __name__ == '__main__':

	start_url = options.url
	
	try:
		re.search("&page=[0-9]+",start_url).group(0)
		clean_start_url = re.sub("&page=[0-9]+","&page=1",start_url)
	except:
		clean_start_url = start_url + "&page=1"
	
	try:
		re.search("&pageSize=[0-9]+",start_url).group(0)
		clean_start_url = re.sub("&pageSize=[0-9]+","&pageSize=250",clean_start_url)
	except:
		clean_start_url = clean_start_url + "&pageSize=250"
	
	transcripts_list = {}
	
	p = 1
	
	url = clean_start_url
	
	print "Indexing congressional records"
	
	while True:
		
		page_source = urllib.urlopen(url).read()
		
		results_position_block = re.search("(?<=span class=\"results-number\">).*?</span>",page_source,re.S).group(0)		
		results_position_block = re.sub(",","",results_position_block)
		a,b = re.search("[0-9]+-[0-9]+",results_position_block).group(0).split('-')
		total = re.search("(?<=of )[0-9]+",results_position_block).group(0)
		
		
		this_page_transcripts_list = get_page_items(page_source,url)
		
		for i in this_page_transcripts_list:
			transcripts_list[i['id']] = i
		
		if b!=total:
			p+=1
			url = re.sub("&page=[0-9]+","&page=%s" %str(p),url)
			print url
		else:
			break
		
		print "Indexed %s items (of %s)" %(str(len(transcripts_list)),str(total))
		
		timeout(30)
	
	s = re.sub("\'","\"",str(transcripts_list))
	
	print "transcripts indexed at cr_pages.json"
	
	d = open("cr_pages.json",'w')
	d.write(s)
	d.close()
	
	print "Downloading transcrips"
	
	
	
	pull_transcripts("cr_pages.json")
	
	
	print "Transcripts downloaded"