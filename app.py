import os
import re
import urllib.request
import urllib.parse
import requests
import itertools
from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy


DEVELOPER_KEY = 'AIzaSyDhI-lLDWtO07DV1atZsOdpgNcCX6OR05s'

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()
dbresults = []

from models import Results

def initDownload(vidID):
	""" Executes youtube-dl command.

	Keyword Arguments:
	vidID -- Id of the video to be downloaded
	"""
	print('Inside initDownload')
	qStore = "youtube-dl --extract-audio --audio-format 'mp3' --audio-quality 0 --youtube-skip-dash-manifest -o '/Users/redfruit/Documents/Projects/Python-YTD/File-Store/%(title)s.%(ext)s' https://www.youtube.com/watch?v="
	print('after qStore')
	query = qStore + str(vidID)
	print('after query')
	print(query)
	try:
		os.system(query)

	except:
		print('Something went wrong.')




def getvidId(searchtext):
	""" Extract video ids for the search made.

	Keyword Arguments:
	searchtext -- Input from the Searchbox
	"""
	print('Inside getVidID')
	query_string = urllib.parse.urlencode({"search_query" : searchtext})
	html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
	search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
	print('Returning searchresults')
	return search_results


def getvidDetails(ids):
	""" Retrive title and image from YoutubeAPI
	
	Initially retrieves the title and image of the requested
	videos from the YoutubeAPI, then dumps the data onto the
	database for later use to display to the user
	Keyword Arguments:
	ids -- List of ids retrieved from the search in getvidId()
	"""
	print('Inside getviddetails')
	key = DEVELOPER_KEY
	region = "IN" 
	url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ids}&key={api_key}"
	r = requests.get(url.format(ids=",".join(ids), api_key=key))
	js = r.json()

	
	items = js["items"]

	for item in items:
		
		try:
			result = Results(vid_name=item["snippet"]["title"], vid_img=item["snippet"]["thumbnails"]["high"]["url"], vid_id=item["id"])
			print(type(result))
			dbresults.append(result)
			db.session.add(result)
			print('Added result to session')
			db.session.commit()
			print('DB Addition Success')
		except Exception as e:
			db.session.rollback()
			print("Unable to add item to database.")
			print(e)
		finally:
			db.session.close()
			
	
		yield item["id"], item["snippet"]["title"], item["snippet"]["thumbnails"]["high"]["url"]



@app.route('/download', methods=['GET', 'POST'])
def downloadMp3():
	""" Serves the downloaded video for upload.

	Video id is retrieved from the Database.
	and matched with the video id caught from the
	input form. 
	"""
	file_fetch = ""
	file_path = ""
	if request.method == "POST":

		try:

			vidID = request.form['downloadvidID']
			print('Got vid ID', vidID)

			initDownload(vidID)
			print('Completed downloading')

			getResult = dbresults[0]
			print('Got DBresults')
			row = getResult.query.filter_by(vid_idd=vidID).first_or_404()
			print('Got Row')
			file_fetch = row.vid_namee + '.mp3'
			print(file_fetch)
			file_path = '/Users/redfruit/Documents/Projects/Python-YTD/File-Store/'+file_fetch



		except:

			print('DB Fetch failed')

	print('Printing File Path', file_path)
	return send_from_directory('/Users/redfruit/Documents/Projects/Python-YTD/File-Store', file_fetch ,as_attachment=True)



@app.route('/', methods=['GET', 'POST'])
def index():
	""" Inital page for the app

	"""
	errors = []
	final_results = []
	
	if request.method == "POST":
        
		try:
			searchtext = request.form['input']
			print('Got searchtext')
			results = getvidId(searchtext)
			print(results)
			
			for idd, title, image in getvidDetails(results):
				print('inside loop')
				print(idd, title, image)
				merge_store = []
				merge_store.append(idd)
				merge_store.append(title)
				merge_store.append(image)

				final_results.append(merge_store)
			
		except:
			errors.append(
				"Unable to get ID. Please make sure it's valid and try again."
			)
    
	print('before sorting')
	

	fnn_results = []
	for elem in final_results:
		if elem not in fnn_results:
			fnn_results.append(elem)
	final_results = fnn_results

	print('After sorting, going to render now')

	#return render_template('index.html', errors=errors, fnn_results=final_results)
	#return render_template('testfront.html', errors=errors, fnn_results=final_results)
	return render_template('nindex.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()	


if __name__ == '__main__':
    app.run()