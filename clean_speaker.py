import re,json



def formatting (text):


	#depaginate
	
	text = re.sub("\s*\[.*?\]\s+"," ",text)

	#emove_links
	
	text = re.sub("<a href=.*?>","",text)
	text = re.sub("</a>","",text)


	#remove_timestamps
	
	text = re.sub("\s+\{time}\s+[0-9]+\s+"," ",text)
	
	#remove_notes
	
	text = re.sub("\s+=+\s+NOTE.*?END NOTE\s+=+\s+","",text)

	#remove_linebreaks
	
	final_text = re.sub("\s*\n\s*"," ",text)
	
	return final_text





def addresses(text):
	
	adds = re.findall("Mr\. President, [a-zA-Z]",text)
	
	for i in adds:

		text = re.sub(i,i[-1].upper(),text)
	
	adds = re.findall("Mr\. Chairman, [a-zA-Z]",text)
	
	for i in adds:

		text = re.sub(i,i[-1].upper(),text)
		
	adds = re.findall("Mr\. Speaker, [a-zA-Z]",text)
	
	
	for i in adds:

		text = re.sub(i,i[-1].upper(),text)
		
		
	adds = re.findall("Madam President, [a-zA-Z]",text)
	
	
	for i in adds:

		text = re.sub(i,i[-1].upper(),text)
	
	text = re.sub("I yield.*?\.",text,re.S)
	
	##now clean up some formatting problems
	text = re.sub("``","\'\'",text)
	text = re.sub("- ","-",text)
		

	return text


def main(filename):
	
	d = open(filename,'r')
	t = d.read()
	j = json.loads(t)
	
	keys = j.keys()
	
	for k in keys:
		id = j[k]['id']
		transcript_filename = "speaker/%s.txt" %id
		try:
			e = open(transcript_filename,'r')
			text = e.read()
			e.close()		
		
			text = addresses(text)
			text = formatting(text)

			g = open(transcript_filename,'w')
			g.write(text)
			g.close()
		except:
			'''print "File not found: %s" %id'''
			pass