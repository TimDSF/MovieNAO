# -*- coding:utf-8 -*-
import paramiko

from naoqi import ALProxy

class SFTP:

	def download(self, ip, port, usr, pas, remoteDir, localDir):
		tsp = paramiko.Transport((ip, port))
		tsp.connect(username = usr, password = pas)
		sftp = paramiko.SFTPClient.from_transport(tsp)
		sftp.get(remoteDir, localDir)
		tsp.close()

	def upload(self, ip, port, usr, pas, localDir, remoteDir):
		tsp = paramiko.Transport((ip, port))
		tsp.connect(username = usr, password = pas)
		sftp = paramiko.SFTPClient.from_transport(tsp)
		sftp.put(localDir, remoteDir)
		tsp.close()
