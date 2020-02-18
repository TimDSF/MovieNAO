# -*- encoding: UTF-8 -*-

# Movie Master, © 2019 ShiFan Dong, Copyright Reserved

import sys
import codecs
import numpy as np
from sklearn.naive_bayes import GaussianNB
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.ensemble import RandomForestClassifier
import jieba
import py2neo
from py2neo import Node, Graph, Relationship



reload(sys)
sys.setdefaultencoding('utf8')

class Master:
	def __init__(self):
		# declaring global varibales
		self.vocab = []
		self.genres = []
		self.movies = []
		self.actors = []
		self.scores = []
		self.d = {}
		self.clf = GaussianNB()

		# connecting to the graph
		with open("config/neo4j.conf", "r") as f:
			self.HOST = f.readline()[0:-1]
			self.USER = f.readline()[0:-1]
			self.PASS = f.readline()[0:-1]

	# remove potential "\r" in the end of the string
	def clean(self, var):
		for i in range(len(var)):
			if var[i].find("\r") != -1:
				var[i] = var[i][0:var[i].find("\r")]

	def cleanRead(self, path, var):
		f = codecs.open(path, "r", "utf-8")
		var += f.read().split("\n")
		f.close()
		self.clean(var)


	def buildModel(self):

		# vocab[]: the dictionary of the vocabulary, same as traits
		# line[]: string array of training data
		# ans[]: number array of training data's question type, same as target
		# d{}: dictionary linking words to its id

		# personalized dictionary
		jieba.load_userdict("vocabulary/genreDict.txt")
		jieba.load_userdict("vocabulary/movieDict.txt")
		jieba.load_userdict("vocabulary/scoreDict.txt")
		jieba.load_userdict("vocabulary/actorDict.txt")
		jieba.load_userdict("vocabulary/vocabulary.txt")

		# loading personalized dictionary, ng for genre
		self.cleanRead("vocabulary/genreDict.txt", self.genres)

		# loading personalized dictionary, nm for movie
		self.cleanRead("vocabulary/movieDict.txt", self.movies)

		# loading personalized dictionary, nnt for actor
		self.cleanRead("vocabulary/actorDict.txt", self.actors)

		# loading personalized dictionary, for scores
		self.cleanRead("vocabulary/scoreDict.txt", self.scores)

		# loading vocab[]
		self.cleanRead("vocabulary/vocabulary.txt", self.vocab)

		# initializing dict d, linking words to indexes
		for i in range(len(self.vocab)):
			self.d[self.vocab[i]] = i

		# loading train_line[] and train_ans[]
		train_line = []
		train_ans = []
		N = 14
		for i in range(N):
			tmp = []
			self.cleanRead("train/" + str(i) + ".txt", tmp)

			for j in range(len(tmp)):
				train_line.append(tmp[j])
				train_ans.append(i)

		# using jieba to split line[] into words[][ID of words]
		train_table = [[0 for i in range(len(self.vocab))] for j in range(len(train_line))]
		for i in range(len(train_line)):
			s = jieba.lcut(train_line[i])
			for w in s:
				if self.d.get(w, 0x7fffffff) != 0x7fffffff:
					train_table[i][self.d[w]] = 1

		# training GNB model
		# clf = GaussianNB()
		# clf = DecisionTreeClassifier()
		# clf = RandomForestClassifier()

		self.clf.fit(train_table,train_ans)

	def query(self, qst_line):

		qst_actor = []
		qst_movie = ""
		qst_genre = ""
		qst_score = -1

		tmpW = jieba.lcut(qst_line)
		tmpT = [0 for i in range(len(self.vocab))]

		for w in tmpW:
			if w in self.actors:
				tmpT[self.d["nnt"]] = 1
				qst_actor.append(w)
			elif w in self.genres:
				tmpT[self.d["ng"]] = 1
				if w.find(u"片") != -1:
					w = w[0:w.find(u"片")]
				elif w.find(u"电影") != -1:
					w = w[0:w.find(u"电影")]
				qst_genre = w
			elif w in self.movies:
				tmpT[self.d["nm"]] = 1
				qst_movie = w
			elif w in self.scores:
				tmpT[self.d["x"]] = 1
				qst_score = int(w)
			elif self.d.get(w,0x7fffffff) != 0x7fffffff:
				tmpT[self.d[w]] = 1

		qstT = []
		qstT.append(tmpT)

		# using model to predict results
		qst_ans = self.clf.predict(np.array(qstT))[0]
		print("Predicted question types are: " + str(qst_ans))

		graph = Graph(self.HOST, username=self.USER, password=self.PASS)

		# self-defined function to simplified the process of query
		def neo(s):
			g = graph.run(s)
			s = ""
			for j in g:
				s += str(j[0]) + " "
			return s

		if qst_ans == 0:
			return str(qst_movie) + "的评分是" + neo("match (m:Movie{title:\"" + qst_movie + "\"}) return m.rating")
		elif qst_ans == 1:
			return str(qst_movie) + "的上映日期是" + neo("match (m:Movie{title:\"" + qst_movie + "\"}) return m.releasedate")
		elif qst_ans == 2:
			return str(qst_movie) + "是一部" + neo("match (Movie{title:\"" + qst_movie + "\"})-[:is]-(g:Genre) return g.name")[0:-1].replace(" ", ",") + "片"
		elif qst_ans == 3:
			return str(qst_movie) + "的剧情是" + neo("match (m:Movie{title:\"" + qst_movie + "\"}) return m.introduction")
		elif qst_ans == 4:
			return str(qst_movie) + "的主演有" + neo("match (n:Person)-[:actedin]-(:Movie{title:\"" + qst_movie + "\"}) return n.name")[0:-1].replace(" ", ",")
		elif qst_ans == 5:
			return str(qst_actor[0]) + "的生平是" + neo("match (n:Person{name:\"" + qst_actor[0] + "\"}) return n.biography")
		elif qst_ans == 6:
			return str(qst_actor[0]) + "的" + str(qst_genre) + "片有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie)-[:is]-(:Genre{name:\"" + qst_genre + "\"}) return m.title")[0:-1].replace(" ", ",")
		elif qst_ans == 7:
			return str(qst_actor[0]) + "演过的电影有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie) return m.title")[0:-1].replace(" ", ",")
		elif qst_ans == 8:
			return str(qst_actor[0]) + "评分大于" + str(qst_score)  + "的电影有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie) where m.rating >= " + str(qst_score) + " return m.title")[0:-1].replace(" ", ",")
		elif qst_ans == 9:
			return str(qst_actor[0]) + "评分小于" + str(qst_score)  + "的电影有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie) where m.rating <= " + str(qst_score) + " return m.title")[0:-1].replace(" ", ",")
		elif qst_ans == 10:
			return str(qst_actor[0]) + "演过的电影风格有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(:Movie)-[:is]-(g:Genre) return distinct(g.name)")[0:-1].replace(" ", ",")
		elif qst_ans == 11:
			return str(qst_actor[0]) + "和" + str(qst_actor[1]) + "共同出演的电影有" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie) where (:Person{name:\"" + qst_actor[1] + "\"})-[:actedin]-(m:Movie) return m.title").replace(" ", ",")
		elif qst_ans == 12:
			return str(qst_actor[0]) + "一共演过" + neo("match (:Person{name:\"" + qst_actor[0] + "\"})-[:actedin]-(m:Movie) return count(m)") + "部电影"
		elif qst_ans == 13:
			return str(qst_actor[0]) + "的生日是" + neo("match (n:Person{name:\"" + qst_actor[0] + "\"}) return n.birth")




	############################################################################
	#############################  USEFUL RESOURCE TEMPLET  ####################
	############################################################################

	#################################  jieba  ##################################

	# s = jieba.lcut("大家好，我是吴煜青！")

	###############################  GaussianNB  ###############################

	# data = np.array([[0,1,0,1],[1,0,1,0]])
	# target = np.array([[0],[1]])

	# containing warnings:

	# clf = GaussianNB()
	# clf.fit(data,target)
	# a = clf.predict(np.array([[0,1,0,1],[1,1,1,0]]))
	# print(a)

	###############################  py2neo  ###################################

	# graph = Graph("http://localhost:7474", username="neo4j", password="pass")
	#
	# g = graph.run("MATCH (n:Movie) where n.rating > 9.8 RETURN n.title")
	# for i in g:
	# 	print(i[0])