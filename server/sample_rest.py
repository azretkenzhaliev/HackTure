import json
import os

from flask import Flask
from flask import request
from flask_restful import Resource, Api
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import googleapiclient.discovery
import requests


app = Flask(__name__)
CORS(app)

api = Api(app)


@app.route("/videos", methods=["POST"])
def get_video_list():
    data = request.get_json()
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyCi05vc19O6v3T49Ji-X9IAiekHbuHOpl4"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    query = youtube.search().list(
        part="snippet",
        q=data["query"],
        maxResults=15
    )

    response = query.execute()
    return json.dumps(response)


@app.route("/subtitles", methods=["POST"])
def get_video_subtitles():
	
	data = request.get_json()

	r = requests.get(
		"https://subtitles-for-youtube.p.rapidapi.com/subtitles/"
		f"{data['videoID']}?translated=None&type=None",
		headers={
			"X-RapidAPI-Host": "subtitles-for-youtube.p.rapidapi.com",
			"X-RapidAPI-Key":
				"042f3fd40bmsh299a3d264e6259ep190110jsnf075030f8fec"})
    
	script = json.dumps(r.json())
	full_text = get_full_script(eval(script))
	keyPhrases = get_key_phrases(full_text)

	script = highlight_keywords(eval(json.dumps(r.json())),keyPhrases)

	return json.dumps(script)


def highlight_keywords(script, keyPhrases):
	for s in script:
		if "text" in s:
			words = "'".join(s["text"].split("&#39;")).split(" ")
			for i in range(len(words)):
				if words[i] in keyPhrases:
					words[i] = "*"+words[i]+"*"
				else:
					for key in keyPhrases:
						keys = key.split()
						if len(keys)==2 and (keys[0]==words[i] or keys[1]==words[i]):
							words[i] = "*"+words[i]+"*"
			s["text"] = " ".join((" ".join(words).split("\n")))

	return script

def get_full_script(script):
    full_text = ""
    for s in script:
        if "text" in s:
            full_text += "'".join(s['text'].strip().split("&#39;"))
            full_text += " "
    return " ".join(full_text.split('\n'))

def get_key_phrases(full_text):
	if True:
		return ['mountain', 'MIT OpenCourseWare', 'neural net', 'chain rule', 'partial derivative', 'Creative Commons license', 'neuron', 'dot product', 'MIT', 'sigmoid function', 'exponential', 'convolution', 'neural net', 'assembly', 'neuron', 'memory', 'GPUs', 'kernel', 'mite', 'neural net', 'green values', 'zn', 'blackboard', 'force', 'zebra', 'giraffe', 'neurons', 'vampire', 'cheetah', 'dn', 'GPUs', 'Boltzmann', 'neurons', 'cheetah', 'school bus', 'test case', 'sigmoid', 'formula', 'mystery', 'algorithm', 'normalizing factor', 'gradient ascent', 'softmax', 'vector', 'partial derivatives', 'neuron', 'noise', 'sigmoid function', 'containership', 'probability', 'neural net', 'prop', 'softmax', 'Boltzmann', 'biologist', 'net.', 'blackboard', 'zebra', 'plague', 'giraffe', 'rerun', 'neuron', 'cheetah', 'cliff', 'sigmoid curve', 'local maximum', 'grasshopper', 'frequency', 'engineering', 'Venice', 'neural net', 'cottage industry', 'cat', 'wolf', 'frequency band', 'toilet', 'baseball', 'barbell', 'artificial intelligence', 'Giraffe', 'Frisbee', 'Russian wolfhound', 'neurons', 'rabbit', 'guitar', 'bird', 'school bus', 'Google', 'saddle', 'rectangle', 'local maximum', 'railroad car']

	keyPhrases = []
	length = len(full_text)

	for i in range(length//5000):
		text = full_text[i*5000:(i+1)*5000]
		text = "+".join(text.split(" "))
		text = "https://aylien-text.p.rapidapi.com/concepts?text=" + text + "&language=en"
		r= requests.get(text,
			headers={
				"X-RapidAPI-Host": "aylien-text.p.rapidapi.com",
				"X-RapidAPI-Key": "9840da312emshb785be15f2be366p1b76efjsnbca35920968f"
			}
		)
		for key in r.json()['concepts'].keys():
			keyPhrases.append(r.json()['concepts'][key]['surfaceForms'][0]['string'])

	text = full_text[(length//5000)*5000:length]
	text = "+".join(text.split(" "))
	text = "https://aylien-text.p.rapidapi.com/concepts?text=" + text + "&language=en"
	r = requests.get(text,
		headers={
			"X-RapidAPI-Host": "aylien-text.p.rapidapi.com",
			"X-RapidAPI-Key": "9840da312emshb785be15f2be366p1b76efjsnbca35920968f"
	})
	
	for key in r.json()['concepts'].keys():
		keyPhrases.append(r.json()['concepts'][key]['surfaceForms'][0]['string'])

	return keyPhrases


@app.route("/wiki", methods=["POST"])
def get_wiki():
    data = request.get_json()
    keyword = data["keyword"]

    print(data)
    print(keyword)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--lang=en")
    driver = webdriver.Chrome(chrome_options=options)

    driver.get("https://www.google.com/")
    english = driver.find_element_by_xpath('//a[contains(text(), "English")]')
    english.send_keys(Keys.ENTER)

    q = driver.find_element_by_name("q")
    q.send_keys(keyword, Keys.ENTER)

    knowledge_panel = driver.find_element_by_xpath(
        '//div[contains(@class, "knowledge-panel")]')

    code = knowledge_panel.get_attribute("innerHTML")
    print(code)

    return code


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
