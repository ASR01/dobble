import streamlit as st 
import numpy as np
import requests
import json
import random
import os
from PIL import Image
import pandas as pd
# Spech modules
import speech_recognition as sr
import msvcrt
import playsound as p # make sure that the version of playsound ios 1.2.2, beacuse  1.3.0 is giving problems
from gtts import gTTS
# for displaying stats
import altair as alt
#from casual_chat import casual_chat

st.set_page_config(page_title ="Play Dobble App",initial_sidebar_state="collapsed", layout="wide", page_icon="📱")

#Variables

stop_words = ['quit', 'stop', 'exit', 'abort', 'leave']
game_start_phrase= ['play game', 'play game', "let's play"]
exit_flag = False

files_path = '../data/original_cards/'
files_list = []

#Get files df

for root, dirs, files in os.walk(files_path):
    for file in files:
        if file.endswith('.JPEG'):
            files_list.append(file)
random.shuffle(files_list)
max_rounds = int(len(files_list)/2)
print(f'max rounds: {max_rounds}' )

#Classes

df = pd.read_csv('../data/classes_words.csv', index_col = 'Word')
cl = dict(zip(df.index, df['Class']))

# Session_state streamlit variable
if "score" not in st.session_state:
	st.session_state.score = [0,0]
if 'files' not in st.session_state:
    st.session_state.files = [] 
if 'level' not in st.session_state:
    st.session_state.level = 0 
if 'diplay_score' not in st.session_state:
    st.session_state.display_score = 0 
if 'choice' not in st.session_state:
    st.session_state.choice = 'Casual Chat'#'Casual Chat'
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = random.randint(0,9999)
if 'init' not in st.session_state:
    st.session_state.init = 0
    


st.session_state.files = files_list


#****************** Voice Commands Instances *******************

recognizer = sr.Recognizer()
#Parameters for fine tuning if needed
recognizer.energy_threshold = 4000
recognizer.pause_threshold = 1 # in seconds
microphone = sr.Microphone()
# phrase_time_duration
ptl = [10, 3]
#timeout waiting for audio
timeout = [5, 15]

#****************************** Voice Commands ************************

def voice_input(ptl, timeout):
    
	print('Please state yor phrase....')
    
	spoken = speech2text(recognizer, microphone, ptl, timeout)
	voc_count=0
		
	#Loop for waiting an answer in casual mode
	while spoken['error'] == 'Unable to recognize speech':
		print('Waiting')
		spoken = speech2text(recognizer, microphone, ptl, timeout)
		print('voice_input function: ',spoken, 'checkpoint', voc_count) #To check
		if st.session_state.choice == 'Play Game':
			voc_count += 1
		
		if (msvcrt.kbhit() and msvcrt.getch() == chr(27).encode()) or voc_count==5:
			exit_flag = True
			spoken['transcription'] = 'Time is over, you lost.'
			break
	
	if spoken['transcription'] in game_start_phrase:
		st.session_state.choice = 'Play Game'
		print('break')
	
	return spoken

def voice_output(text, chat_history_id):

    print("You said: {}".format(text)) # implement the chat api here
    #response, chat_history_id = casual_chat(text, chat_history_id)
    print(text)
    text2speech(text)

    return(text, chat_history_id)


# input speech
def speech2text(recognizer, microphone, ptl, timeout):
	"""Transcribe speech from recorded from `microphone`.
	Dictionary with three keys:

	"success": a boolean indicating whether or not the API request was successful

	"error":   `None` if no error occured, otherwise a string containing an error message if the API could not be reached or speech was unrecognizable
    
	"transcription": `None` if speech could not be transcribed, otherwise a string	containing the transcribed text
	"""
	#adjust for ambient noise
	with microphone as source:
		recognizer.adjust_for_ambient_noise(source, duration = 0.5)
		audio = recognizer.listen(source, timeout=timeout, phrase_time_limit= ptl)
	#print('timeout:' + str(timeout) +'\nPTL: ' + str(ptl) )
    # initialise the response object
	response = {
		"success": True,
		"error": None,
		"transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
	try:
		response["transcription"] = recognizer.recognize_google(audio)
	except sr.RequestError:
        # API was unreachable or unresponsive
		response["success"] = False
		response["error"] = "API unavailable"
	except sr.UnknownValueError:
        # speech was unintelligible
		response["error"] = "Unable to recognize speech"
        #Repeat the listening, the funcion should be called again
	return response

# output speech

def text2speech(text):
	print(text)
	tts = gTTS(text=text)
	filename = 'voice.mp3'
	tts.save(filename)
	# mp3_fp = BytesIO()	
	# tts.write_to_fp(mp3_fp)
	# #p.playsound(mp3_fp, True)
	p.playsound(filename, True)
	os.remove(filename)

	return


def get_class(word):
    
    try:
        res = cl[str.lower(word)]
    except:
        res = word
        
    return res

#**************************** NPLP and CV Model calls ***********

# DO not forget the chat_id

def predict_voice(text):
	print('predict ', text)
	header = {'Content-Type': 'application/json'}
	url="http://localhost:8001/chat"
	
	payload=json.dumps(text)
	#st.text(payload)
 
	# print(payload)
	# print(url)
	
	response = requests.post(url, headers=header, data=payload)
	#print(response.status_code)
	#print(dir(response))
	#print(response.url)
	response = json.loads(response.text)
	#print(response)
	return response

# def classify(img1, img2):
	
# 	header = {'Content-Type': 'application/json'}
# 	url="http://localhost:8002/detect_images"
# 	#remember the right address when dockerizing
# 	data = {'name1':img1, 'name2':img2}
# 	payload=json.dumps(data)
# 	response = requests.post(url, headers=header, data = payload)
# 	#print(response.status_code)
# 	response = response
	
# 	return response

def classify(img0, img1):
	
	last = 'last_image.jpg'
	
	img_f = np.concatenate((img0, img1), axis=1)
	img_conc = Image.fromarray(img_f)
	img_conc.save(last, 'JPEG')
	url="http://localhost:8002/predict/"
	#remember the right address when dockerizing
	files = {'filename':last, 'file':open(last, 'rb' ), 'content_type':'image/jpeg'}
 
	response = requests.post(url, files = files)
	return response


def new_choice():
    if st.session_state.activity_radio_button:
    	st.session_state.choice = st.session_state.activity_radio_button

def main():
	
	if st.session_state.init == 0:
		st.title("Dobble")
		st.write("**Welcome** \nDo you want to talk a bit before we play a comple of hands of dobble?. \nJust say **let's play** or similar to access the game.")
		st.session_state.init = 1	
	#caching.clear_cache()


	activities = ["Casual Chat", "Play Game"]
	st.sidebar.title("Navigation")
	activity = st.sidebar.radio("Activity",activities, on_change=new_choice, key ='activity_radio_button')
	st.sidebar.write('Just say out loud the repeated object')
	with st.sidebar.expander("See explanation"):
		st.write("""
		You will see two random images on screen just detect the one repeated and try to say is out loud with you best american accent. The game are 26 pairs tha are selected randomly. *good luck*
		""")

	if st.session_state.choice == 'Casual Chat':
		st.header('Real-time chat')
		col1, col2 = st.columns(2)
		with col1:
			myspeech = st.empty()
		
		col1, col2 = st.columns(2)
		with col2:
			nlpspeech = st.empty()
   
		default_id = st.session_state.chat_id
		text2speech('Tell me something')
		nlpspeech.info('Tell me something')

		
		for x in range(1000):
			spoken = voice_input(ptl[0], timeout[0])
			if st.session_state.choice == 'Play Game':
				#st.button('Should we play dobble?')
				text2speech('Press the button when you are ready')
				break
			text = spoken['transcription']
			myspeech.info(text)
			#text = st.text_input('Text', key="1")
			dict = {'text': text, 
					'chat_history_id' : default_id}
			#dict = {'text': text} 
			if text == "":
				response = 'hmmm'
			else:
				response = predict_voice(dict)
			dict_res = eval(response)
			nlpspeech.info(dict_res['output'])
			text2speech(dict_res['output'])
		
	if st.session_state.choice == 'Play Game':
	

		col1, col2 = st.columns(2)
		with col1:
			play = st.button('Start now')

		standings = pd.DataFrame({'Users': ['Me', 'Computer'], 'Result': [0, 0]})
		progress = st.empty()
		col1, col2, col3 = st.columns(3)
		with col1:
			image0 = st.empty()
		with col2:
			image1 = st.empty()
		with col3:
			round_counter = st.empty()
			user_r0 = st.empty()
			user_result = st.empty()
			comp_r0 = st.empty()
			computer_result = st.empty()
			result_g = st.empty()

	  
		if play == True:

			text2speech('Welcome to the game')
						
			for x in range(max_rounds):

				text2speech('Playing round ' + str(x+1))
				
				progress.progress(x/max_rounds)
				user_r0.text = ('Your value')
				comp_r0.text = ('Correct value')

				img0 = Image.open(files_path + files_list[x*2])        
				img1 = Image.open(files_path + files_list[x*2 + 1])        

				# We call via API the CV module   
				results = classify(img0,img1)

				image0.image(img0, caption=files_list[x*2])        
				image1.image(img1, caption=files_list[x*2 + 1])#, use_column_width = auto)
				#play_round(x)
				round_counter.info('Round:' + str(x + 1))
				

				print('waiting for voice')
				spoken = voice_input(ptl[1], timeout[1])
				text = spoken['transcription']
				text2speech(text)
				norm_text = get_class(spoken['transcription']) 
			
    
				print(spoken['transcription'])
	
        
				

				# We tranfors the json into pandas DataFrame
				i0 = json.loads(results.json())
				i1 = json.dumps(json.loads(i0['dataframe']))
				df = pd.read_json(i1,orient='split')

				# we calculate the item repeated

				df0 = df[['class', 'name']]
				dobble_result = df0.groupby('name')['class'].size().idxmax()
				dobble_result.lower()
    
				if str.lower(dobble_result) == str.lower(norm_text):
			        #text2speech('You are right, point for you. It was' + str(dobble_result))
					standings.at[0, 'Result'] += 1
					user_result.success(norm_text)
					computer_result.success(str(dobble_result))
					trend = [1,0]
				
				else:          
					standings.at[1, 'Result'] += 1
        			#text2speech('Sorry I bet it is: '+ str(dobble_result))
					user_result.error(norm_text) 
					computer_result.error(dobble_result) 
					trend = [0,1]
				alt_bar = alt.Chart(standings).mark_bar().encode(x='Users', y = 'Result').properties(width=300)
				result_g.altair_chart(alt_bar)			

				
				print('end of round')
			
	return	

if __name__ == '__main__':
	main()
