This makes a twitter bot from a congressperson, by pulling her/his statements from the publicly-available congressional record.

The bot will respond to @mentions of it by selecting from the corpus of statements what it thinks is the most relevant sentence, plus one on either side, plus an extra tweet with a date, title of the CR entry, and a link back to the original on congress.gov.


1. Dependencies:
	numpy (above 1.7, because I use numpy.random.choice)
	python-twitter
	nltk ** download the LITE version if you're pushing to heroku
		python -m textblob.download_corpora lite
		(more on this below)


2. How to build

	a. Go to https://www.congress.gov/congressional-record and run a search for a particular member. Narrow to "remarks in the congressional record" (a link on the right) -- this program doesn't do bills. When you're satisfied that the search results are coming out right, dump the url into download_records.py:
			python download_records.py -u URL
	   This will build a file called "cr_pages.json" that indexes all the records, and then download those records into a new folder called "transcripts".
   
	b. Feed "cr_pages.json" and the last name of your chosen speaker into make_bot.py:
			python make_bot.py -f "cr_pages.json" -s mcconnell
	   This should build a separate directory, "speaker", of (mostly) cleaned-up text, only of your chosen speaker's statements. It will then turn around and break these files down into keywords using nltk. The final output file, "final.json", will automatically be saved to the heroku folder.
	   If you want to go through an extra step of cleaning up the statements by hand -- and it does help -- you can do this by breaking "make_bot" before the final line, where it calls "speaker_to_json()". If you want to break up individual files between themes (good for filibusters, for instance), just add "<break>" where the subject matter changes, and speaker_to_json will create these as separate records when you do finally run it.
   
   
3. Now you can build your heroku app!

	a. Procfile is already in there.

	b. The regular nltk build is way too big, my git push without the lite build fails every time otherwise. You want to download the lite version (see #1 above), copy the nltk_data folder into your heroku folder, then change the heroku path variable to this new nltk_data folder:
	b1. python
	b2. import heroku
	b3. nltk.data.path = ['......../congressional_record_bot/heroku/nltk']
			(That last step is a bit drastic, it should be noted -- if you move this folder, you'll break nltk. But I couldn't get it to work with nltk.data.path.append('newpath'). Happy to fix this instruction if someone has a better way. n.b. I found this fix here: https://github.com/sloria/TextBlob/issues/59)
	b4. Change your git push config here as well:
			git config --global http.postBuffer 2M

	c. Follow the instructions on Heroku to get your twitterbot up and running: https://devcenter.heroku.com/articles/getting-started-with-python-o


3 ALT -- You can use this without heroku. Just run congressbot_tw_interface:
		python congressbot_tw_interface.py
	That's it!