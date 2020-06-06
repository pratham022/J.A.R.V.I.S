import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import requests
import time
import os
import alsaaudio
import psutil
import json
import urllib
import re
from pygame import mixer
import random
import smtplib
import sys
import subprocess

# ------------------------------------------------------------------------------------------------------------
# Initialising the pyttsx3 engine
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 30)
# ---------------------------------------------------------------------------------------------------------

# Speak function for utterance
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
# -------------------------------------------------------------------------------------------------------

# This function accepts audio from user and generates string from it using google recogniser
# All the decisions are taken based upen this input
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
       	r.adjust_for_ambient_noise(source, duration = 1)
        print("Listening...")
        # r.pause_threshold = 1
        audio = r.listen(source, timeout= 3, phrase_time_limit=6)

        try:
            print("Recognising...")
            query = r.recognize_google(audio, language='en-US')
            print(f"You entered: {query}\n")
        except Exception as e:
            # print(e)
            print("Say that again please...")
            return "None"
    return query
# ----------------------------------------------------------------------------------------------------------


# Function that gives current date, time and day
def getDateTime():
    date_today = datetime.date.today()
    list1 = ["", "january", "february", "march", "april", "may", "june",
             "july", "august", "september", "october", "november", "december"]
    speak("Sir, This is " + list1[date_today.month] + " " + str(date_today.day) + "; " + str(date_today.year))
    time.sleep(1)
    obj1 = datetime.datetime.now()
    speak("Today is " + obj1.strftime("%A"))
    time.sleep(1)
    hr = obj1.strftime("%X")
    speak("And the current time is " + hr[:2] + " hours " + hr[3:5] + " minutes")


# ----------------------------------------------------------------------------------------------------------
# Function that gives the current weather from openweathermap.org
def getWeather():
    api_key = "your-api-key"
    city_id = 1259229
    complete_url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}"
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"]!= "404":
        y = x["main"]
        current_temp = y["temp"] - 273.15
        current_pressure = y["pressure"]
        current_humidiy = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        speak(f"The current temperature in your city is {'%.2f'%current_temp} degree celcius")
        time.sleep(1)
        speak(f"There is {weather_description} in your city")
        time.sleep(1)
        speak(f"The humidity is {current_humidiy}")
        time.sleep(1)
        speak(f"The current atmospheric pressure is {current_pressure}")
        speak("Now I am ready for your commands, Pinku")
# --------------------------------------------------------------------------------------------------------------

def getSysStatus():
    speak("I am fine, sir. All systems are at 100 percent.")
    battery = psutil.sensors_battery()
    percent = int(battery.percent)
    plugged = battery.power_plugged
    speak("Battery percent, " + str(percent) + "percent")
    if percent <= 10 and plugged == False:
        speak("Sir, battery is critically low, please plug in device charger")

    if plugged == False:
        speak("Battery status, discharging")
    else:
        speak("Battery status, charging")

    m = alsaaudio.Mixer().getvolume()
    speak("Current speaker volume is " + str(m[0]) + "percent")

# -----------------------------------------------------------------------------------------------------------
def playMusic():
    speak("which song should i play, sir")
    song = takeCommand()
    query = "https://www.youtube.com/results?search_query=" + "+".join(song.split())
    html_content = urllib.request.urlopen(query)
    list1 = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    webbrowser.open("https://www.youtube.com/watch?v="+list1[0])
    speak("Playing "+song+"for you, sir")

# -----------------------------------------------------------------------------------------------------------
def playSongs():
    mixer.init()
    list1 = os.listdir("/home/prathamesh/Music")
    speak("Playing songs for you, sir")
    start_ticks = time.time()
    while True:
        # s = takeCommand()
        # print("Entered command : "+str)
        song = random.choice(list1)
        mixer.music.load("/home/prathamesh/Music/"+song)
        mixer.music.play(loops=-1)
        time.sleep(60)              # play a song only for 1 minute then switch to next one
        curr_ticks = time.time()
        if curr_ticks - start_ticks >= 180:
            print("Playback finished, sir")
            break

# ----------------------------------------------------------------------------------------------------------
def sendEmail():
    dict_mail = {"your-name":"your-emailid", "friend1-name": "friend1-emailid",
                 "friend2-name":"friend2-emailid"}  # This dictionary will contain recipient's name and mail-id
    speak("Who should i send it to")
    r = takeCommand()
    recipient = dict_mail[r.lower()]
    speak("What's the subject, sir")
    subject = takeCommand()
    speak("and what's the message, sir")
    content = takeCommand()

    try:
        speak("sending email, sir")
        mail = smtplib.SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        sender = "your email-id"
        mail.login(sender, "your-password")  # Note that password is not secure in this case...
        # Store it in database or text file
        header = "To: " + recipient + "\n" + "From: " + sender + "\n" + "Subject: " + subject + "\n"
        content = header + content
        mail.sendmail(sender, recipient, content)
        mail.close()
        speak("Email successfully, sir")
    except Exception as ex:
        print("Exception caught: "+ex)

# -----------------------------------------------------------------------------------------------------------
# Function that searches for a specified file and then opens it in text editor
def openFile():
    speak("Enter the file name you want to open sir!")
    fname = input("Enter here: ")
    for root, dir, files in os.walk("/home/prathamesh/Documents"):
        if fname in files:
            speak("File found, sir")
            time.sleep(1)
            speak("Opening file in read write mode in text editor..")
            subprocess.call(["xdg-open", os.path.join(root, fname)])
            break
    else:
        speak("File not found sir")

# ------------------------------------------------------------------------------------------------------------
# Function that opens some basic applications like the ones listed in dictionary
def openApp():
    app_dict = {
        "text editor": "gnome-text-editor",
        "calculator": "gnome-calculator",
        "calendar": "gnome-calendar",
        "clock": "gnome-clocks",
        "camera": "cheese",
        "screen recorder": "kazam",
        "browser": "firefox"
    }
    speak("Which application should i open, sir")
    app = takeCommand().lower()
    if app in app_dict:
        os.system(app_dict[app])
    else:
        speak("Application not listed in my memory, sir")
# -----------------------------------------------------------------------------------------------------------
def takeScreenshot():
    speak("taking screenshot, sir")
    os.system("gnome-screenshot")
    pic_name = datetime.datetime.now().strftime("Screenshot from %Y-%m-%d %H-%M-%S.png")
    speak("screenshot taken, sir. Do you want me to open it?")
    ip = takeCommand().lower()
    if ip == "yes":
        subprocess.call(["xdg-open", "/home/prathamesh/Pictures/"+pic_name])
        speak("Here it is sir. Looks good")

# ------------------------------------------------------------------------------------------------------------
def speakFeatures():
    speak("My creator has fed lot of functionalities in me.")
    speak("I can open browser, send email, give updates regarding battery status and speaker volume")
    speak("I can also read daily news bulletin for you, search for content on google, answer general user questions by searching them on google")
    speak("I can also fetch current date time and also the current weather in your city")
    speak("I can also play music for you from youtube or play songs stored in your system")
    speak("I am designed to talk formally with users")
    speak("You can also use me to open any file stored in your system or for opening google maps")
    speak("I can get the location of the specified city on google maps and also your home location")
    speak("I can also open some basic appliations like text editor, calculator, camera, calendar, screen recorder, clock and browser")
    speak("You can also use me to take screenshots")
    speak("Currently I am under development and will have more advanced features in future, Thanks")
# -----------------------------------------------------------------------------------------------------------

# Gives the welcome message
def wishMe():
    speak("Starting all system applications")
    time.sleep(2)
    speak("Installing all drivers")
    time.sleep(1)
    speak("Caliberating and examining all the core processors")
    os.system("inxi -ACdDfFGNiIlmnopSu")
    time.sleep(2)
    speak("All systems have been started, now I am online")
    time.sleep(1)
    speak("Hello I am Jarvis Lite; Pratham's desktop assistant!")
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning")
    elif hour<18:
        speak("Good Afternoon")
    else:
        speak("Good evening")
    time.sleep(1)
    getDateTime()
    time.sleep(1)
    getWeather()
# -------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    wishMe()
    while True:
        query = takeCommand().lower()
        # Different logics based upon queries

        # -------------------------------------------------------------------------------------------------------------
        # BASIC INTERROGATION
        if query == "hello":
            speak(random.choice(["Well, hello", "at your service, sir"]))
        elif "what does jarvis stand for" in query:
            speak("JARVIS stands for Just A Rather Very Intelligent System")
        elif "you are dumb" in query:
            speak(" I don't understand that yet. Maybe you could teach me.")
        elif "no I won't" in query:
            speak(" I don't know how to answer that. Maybe I could interest you in something else.")
        elif "quit" in query:
            speak("GoodBye")
            exit()
        elif "your" in query and "features" in query:
            speakFeatures()

        # -------------------------------------------------------------------------------------------------------------
        # Using wikipedia module to get a basic 2 sentence information about something
        elif "wikipedia" in query:
            print("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to wikipedia")
            print(results)
            speak(results)

        # -------------------------------------------------------------------------------------------------------------
        # Opening google and youtube search engines
        elif "open youtube" in query:
            webbrowser.open("https://www.youtube.com", new=2)
            speak("Right away, sir! Created new tab in existing browser session.")
        elif "open google maps" in query:
            speak("Opening google maps for you")
            webbrowser.open("https://www.google.co.in/maps/@18.4489387,73.8529955,15z?hl=en")
        elif "open google" in query:
            webbrowser.open("https://www.google.com", new=2)
            speak("Right away, sir! Created new tab in existing browser session.")

        # -------------------------------------------------------------------------------------------------------------
        # Get the system status ie battery percentage, speaker volume
        elif "system status" in query:
            getSysStatus()

        # -------------------------------------------------------------------------------------------------------------
        # Searching for content on google
        # Case 1: when i say search google or something like that
        elif "search" in query and "google" in query:
            query = query.replace("search", "")
            query = query.replace("google", "")
            query = query.replace("for", "")
            speak("Right away, sir! Created new tab in existing browser session.")
            url = "https://www.google.com/search?client=ubuntu&channel=fs&q={}+&ie=utf-8&oe=utf-8".format(query)
            webbrowser.open(url, new=2)

        # Case 2: we will perform google search for all types of interrogative questions
        elif query.split()[0] in ["who", "why", "when", "where", "what", "what", "whom", "whose", "how"]:
            speak("Performing google Search on it...")
            url = "https://www.google.com/search?client=ubuntu&channel=fs&q={}+&ie=utf-8&oe=utf-8".format(query)
            webbrowser.open(url, new=2)
            speak("Right away, sir! Created new tab in existing browser session.")

        # -------------------------------------------------------------------------------------------------------------
        # Reading daily news using news api
        elif "read" in query and "headlines" in query:
            url = "http://newsapi.org/v2/top-headlines?country=in&apiKey=your-api-key"
            page = requests.get(url).json()
            articles = page["articles"]
            headlines = []
            for article in articles:
                headlines.append(article["title"])

            speak("Reading top 10 headlines for you sir..")
            for i in range(10):
                print(headlines[i])
                speak(headlines[i])
                time.sleep(1)

            time.sleep(2)
            speak("Hope you were satisfied by my service..")

        # -------------------------------------------------------------------------------------------------------------
        # Play Music - It will ask for song then will play on youtube
        elif "play music" in query:
            playMusic()
        # -------------------------------------------------------------------------------------------------------------
        # Play songs - this will play songs in our saved in our PC
        elif "play songs" in query:
            playSongs()
        # -------------------------------------------------------------------------------------------------------------
        elif "send email" in query:
            sendEmail()
        # -------------------------------------------------------------------------------------------------------------
        elif "open" in query and "file" in query:
            openFile()
        # -------------------------------------------------------------------------------------------------------------
        elif "home location" in query:
            speak("Opening your home location in google maps, sir")
            webbrowser.open("https://www.google.co.in/maps/place/Shri+Siddhivinayak+Manasvi,+Ambegoan+Road,+Behind+D-Mart,+Katraj-Mumbai+Highway,+Katraj+-+Ambegaon+BK+Rd,+Ambegaon+BK,+Pune,+Maharashtra+411046/@18.4498294,73.8399931,17z/data=!4m5!3m4!1s0x3bc2eacd33f95b53:0xbbad0d8b01dbea48!8m2!3d18.4498294!4d73.8421818")
        elif "open" in query and "location in google maps" in query:
            speak("Enter the city name, sir")
            city = takeCommand()
            webbrowser.open("https://www.google.com/maps/place/"+city.capitalize())
        # -------------------------------------------------------------------------------------------------------------
        elif "open" in query and "application" in query:
            openApp()
        # -------------------------------------------------------------------------------------------------------------
        elif "screenshot" in query:
            takeScreenshot()


