# -*- encoding: UTF-8 -*-

import sys
import time
import codecs
from naoqi import ALProxy
from py2neo import Graph

from master import Master
from recognition import Recognition

reload(sys)
sys.setdefaultencoding('utf8')

# Initializing robot connections
with open("config/nao.conf", "r") as f:
	IP = f.readline()[0:-1]
	PORT = int(f.readline()[0:-1])

# Declaring robot APIs
motion = ALProxy("ALMotion", IP, PORT)
posture = ALProxy("ALRobotPosture", IP, PORT)
tts = ALProxy("ALAnimatedSpeech", IP, PORT) # ALTextToSpeech
auto = ALProxy("ALAutonomousLife", IP, PORT)

auto.stopAll()

# Configuing tts
# tts.setLanguage("Chinese")
# tts.setVolume(0.75)


# Wake up robot
print("Initializing robot.")
motion.wakeUp()


print("Building knowledge graph.")
master = Master()

# build model
master.buildModel()

for _ in range(10):
	# Listening using recognition.py, record.py, and sftp.py
	try:
		print("Listening for question.")
		rcg = Recognition()
		qst = rcg.recognize()
		print("Question: " + qst)

		# query using the model
		print("Finding answer in graph.")
		ans = master.query(qst)
		print("Answer: " + ans)
		tts.say(ans, {"bodyLanguageMode":"contextual"})

		time.sleep(0.5)
	except KeyboardInterrupt:
		break 
	except:
		tts.say("我没太听懂你说的话", {"bodyLanguageMode":"contextual"})

# put robot to sleep
print("Putting robot to rest")
motion.rest()