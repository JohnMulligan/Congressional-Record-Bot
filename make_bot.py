import re,json
import os
import clean_speaker
import speaker_to_json
from optparse import OptionParser, Option, OptionValueError



parser = OptionParser()
parser.add_option("-f", action="store", type="str", dest="filename", default="cr_pages.json")
parser.add_option("-s", action="store", type="str", dest="speakername")

(options, args) = parser.parse_args()


if __name__ == '__main__':
	
	filename = options.filename
	speakername = options.speakername
	
	d = open(filename,'r')
	t = d.read()
	j = json.loads(t)
	
	keys = j.keys()
	
	for k in keys:
		

		id = j[k]['id']
		transcript_filename = "transcripts/%s.txt" %id
		e = open(transcript_filename,'r')
		text = e.read()
		
		speakerisms = re.findall("((?<=%s\.).*?(?=(The PRESIDENT|The SPEAKER|The PRESIDING OFFICER|The CHAIRMAN pro tempore|Mrs\. [A-Z][A-Z]+|Mr\. [A-Z][A-Z]+|Ms\. [A-Z][A-Z]+|Mr\. De[A-Z][A-Z]+|Mrs\. De[A-Z][A-Z]+|Ms\. De[A-Z][A-Z]+|Mr\. Mc[A-Z][A-Z]+|Mrs\. Mc[A-Z][A-Z]+|Ms\. Mc[A-Z][A-Z]+|Mr\. Mac[A-Z][A-Z]+|Mrs\. Mac[A-Z][A-Z]+|Ms. Mac[A-Z][A-Z]+|Mr\. La[A-Z][A-Z]+|Mrs\. La[A-Z][A-Z]+|Ms. La[A-Z][A-Z]+)))" %speakername.upper(),text,re.S)
		
		clean_speakerisms = []
		
		for i in speakerisms:
			
			clean_speakerisms += [l for l in i if len(re.findall(" ",l))>2]
		
		if not os.path.exists('speaker'):
			os.makedirs('speaker')
		
		output_filename = "speaker/%s.txt" %id
		
		g = open(output_filename,'a')
		
		for b in clean_speakerisms:
			g.write(b+"\n")
		
		g.close()
		
	print "Cleaning up records"
	
	clean_speaker.main(filename)
	
	print "Making final database"
	
	speaker_to_json.main(filename)