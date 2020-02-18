# -*- coding:utf-8 -*-
import time
from naoqi import ALProxy
 
class Record:

	def __init__(self):
		# declaring API interfaces 
		with open("config/nao.conf", "r") as f:
			self.IP = f.readline()[0:-1]
			self.PORT = int(f.readline()[0:-1])

		self.rcd = ALProxy("ALAudioRecorder", self.IP, self.PORT)
		self.ply = ALProxy("ALAudioPlayer", self.IP, self.PORT)

	def record(self, duration, remoteDir, fmt = "wav" , rate = 16000, channels = [0, 0, 1, 0]):
		try:
			self.rcd.startMicrophonesRecording(remoteDir, fmt, rate, channels)
			print("Started recording.")
			time.sleep(duration)
		finally:
			self.rcd.stopMicrophonesRecording()
			print("Finished recording.")

	def recordStart(self, remoteDir, fmt = "wav" , rate = 16000, channels = [0, 0, 1, 0]):
		try:
			self.rcd.startMicrophonesRecording(remoteDir, fmt, rate, channels)
			print("Started recording.")
		except:
			print("Already Started.")

	def recordStop(self):
		try:
			self.rcd.stopMicrophonesRecording()
			print("Finished recording.")
		except:
			print("Already Stopped.")

	def play(self, remoteDir):
		self.ply.play(self.ply.loadFile(remoteDir))
