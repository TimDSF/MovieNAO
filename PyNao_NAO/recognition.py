# -*- coding:utf-8 -*-

import time
import codecs

from naoqi import ALProxy
from aip import AipSpeech

from record import Record

class Recognition():

	def __init__(self):

		with open("config/nao.conf", "r") as f:
			self.IP = f.readline()[0:-1]
			self.PORT = int(f.readline()[0:-1])
			self.usr = f.readline()[0:-1]
			self.pas = f.readline()[0:-1]

		self.APP_ID = "16907241"
		self.API_Key = "HBO9vAxx9CyGCyH0TcukjF0K"
		self.Secret_Key = "DG5G5C3QwR3sYk0UdCeLBa0kou7QIbgR"

		self.aip = AipSpeech(self.APP_ID, self.API_Key, self.Secret_Key)

		self.detProxy = ALProxy("ALSoundDetection", self.IP, self.PORT)
		self.memProxy = ALProxy("ALMemory", self.IP, self.PORT)

		self.record = Record()

	def recognize(self, timeoutCount = 5000):

		try:
			# speech recognition

			self.detProxy.setParameter("Sensitivity", 0.99)
			self.detProxy.subscribe("Listener")
			print('Started detecting.')
			
			b = 0
			rcd = 0

			for _ in range(timeoutCount):
				val = self.memProxy.getData("SoundDetected")
				# print(str(val[0][1]) + str(b))
				try:
					if val[0][1] == 1 and b == 0:
						b = 1
						self.record.recordStart("/home/nao/audio.wav")
					elif val[0][1] == 0 and b == 1:
						b = 0
						self.record.recordStop()
						rcd = 1
						break
				except:
					continue
		finally:
			print("Stopped detecting.")
			self.detProxy.unsubscribe("Listener")

		def get_file_content(filePath):
		    with open(filePath, 'rb') as fp:
		        return fp.read()

		if rcd == 0:
			print("timeout")
			return ""
		else:
			rst = self.aip.asr(get_file_content("/home/nao/audio.wav"), "wav", 16000, {'dev_pid': 1536,})

			if rst["err_no"] == 0:
			# 	with codecs.open("tmp.txt", "w", encoding = "utf-8") as f:
			# 		f.write(rst["result"][0])
				return rst["result"][0]