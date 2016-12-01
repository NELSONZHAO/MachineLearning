#-*-coding:utf-8 -*-
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

#返回一个有关person1与person2的基于距离的相似度评价
#这里的prefs是一个字典
def sim_distance(prefs, person1, person2):
	#得到share_item的列表
	si = {}
	#如果person1所喜欢的电影在person2喜欢电影中，则对si字典赋值1
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1 #此时得到的是一个存储person1和person2共同评价电影的字典

	#如果两者没有共同之处，则返回0
	if len(si) == 0: return 0

	#计算所有差值的平方和
	sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])

	return 1/(1+sqrt(sum_of_squares))

#返回p1和p2的皮尔逊相关系数
def sim_pearson(prefs, p1, p2):
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	#得到列表元素的个数
	n = len(si)

	#如果两者没有共同之处，则返回1
	if n == 0: return 1

	#对所有偏好求和
	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])

	#求平方和
	sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
	sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

	#求乘积之和
	pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])

	#计算皮尔逊评价值
	num = pSum - (sum1*sum2/n)
	den = sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
	if den == 0: return 0

	r = num/den

	return r

#返回p1和p2的Tanimoto分值(作业1)
def sim_tanimoto(prefs, p1, p2):
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	#返回公式
	s = float(len(si))/(len(prefs[p1])+len(prefs[p2])-len(si))
	return s

#从反映偏好的字典中返回最为匹配者
def topMatches(prefs, person, n=5, similarity=sim_pearson):
	scores = [(similarity(prefs, person, other),other) for other in prefs if other != person]

	#对列表进行排序，评价值最高者排在最前面
	scores.sort() #默认为升序
	scores.reverse() #改为降序
	return scores[0:n]

#利用所有他人评价值的加权平均为某人提供意见
def getRecommendations(prefs, person, similarity=sim_pearson):
	totals = {}
	simSums = {}
	#不和自己作比较
	for other in prefs:
		if other == person: continue
		sim = similarity(prefs, person, other) #计算与其他人的皮尔逊系数

		#忽略评价值为零或小于零的情况
		if sim <= 0: continue
		#遍历其他人的观影列表
		for item in prefs[other]:

			#只对自己还未曾看过的影片进行评价
			if item not in prefs[person] or prefs[person][item] == 0:
				#相似度*评价值
				totals.setdefault(item, 0) #将字典中的内容初始化为0
				totals[item] += prefs[other][item] * sim
				#相似度之和
				simSums.setdefault(item, 0)
				simSums[item] += sim

	#建立一个归一化的列表
	rankings = [(total/simSums[item],item) for item,total in totals.items()]

	#返回经过排序的列表,rankings存储的是对于当前个体没有看的电影的评分表
	rankings.sort()
	rankings.reverse()
	return rankings

#利用当前用户外的其他前5名用户来给出推荐(作业3)
def getRecommendations_n(prefs, useritems, person, n=5):
	totals = {}
	simSums = {}
	#取出相似用户数据集中的的前n个数据进行推荐
	for (sim,user) in useritems[person][:n]:
		#遍历他人的的观影列表
		for item in prefs[user]:
			#只对自己还未曾看过的影片进行评价
			if item not in prefs[person] or prefs[person][item] == 0:
				#相似度*评价值
				totals.setdefault(item, 0) #将字典中的内容初始化为0
				totals[item] += prefs[user][item] * sim
				#相似度之和
				simSums.setdefault(item, 0)
				simSums[item] += sim

	#建立一个归一化的列表
	rankings = [(total/simSums[item],item) for item,total in totals.items()]

	#返回经过排序的列表,rankings存储的是对于当前个体没有看的电影的评分表
	rankings.sort()
	rankings.reverse()
	return rankings

#转换数据集
def transformPrefs(prefs):
	result={}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item, {})

			#将物品和人员对调
			result[item][person] = prefs[person][item]
	return result

#构造物品相似集
def calculateSimilarItems(prefs, n=10):
	#建立字典，以给出与这些物品最为相近的所有其他物品
	result = {}

	#以物品为中心对偏好矩阵实施倒置处理
	itemPrefs = transformPrefs(prefs)
	c = 0
	for item in itemPrefs:
		#针对大数据集更新状态变量，这个是用来显示当前数据处理进度的，例如100/1170代表目前处理了100条数据
		c += 1
		if c%100 == 0: print "%d / %d" % (c, len(itemPrefs))
		#寻找最为相近的物品
		scores = topMatches(itemPrefs,item,n=n,similarity = sim_distance)
		result[item] = scores
	return result

#构造用户相似集
def calculateSimilarUser(prefs, n=10):
	#建立结果字典存储相近用户
	result = {}

	c = 0
	for user in prefs:
		c += 1
		if c%100 == 0: print "%d / %d" % (c, len(prefs))
		#寻找相近用户
		scores = topMatches(prefs, user, n=n, similarity = sim_distance)
		result[user] = scores
	return result

def getRecommendedItems(prefs,itemMatch,user):
	userRatings = prefs[user]
	scores = {}
	totalSim = {}

	#循环遍历由当前用户评分的物品
	for (item, rating) in userRatings.items():
		#循环遍历与当前物品相近的物品
		for (similarity, item2) in itemMatch[item]:

			#如果更该用户已经对当前物品做过评价，则将其忽略
			if item2 in userRatings: continue

			#评价值与相似度的加权之和
			scores.setdefault(item2, 0)
			scores[item2] += similarity*rating

			#全部相似度之和
			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity
	#将每个合计值除以加权和，求出平均值
	rankings = [(score/totalSim[item],item) for item, score in scores.items()]

	#按最高值到最低值的顺序，返回评分结果
	rankings.sort()
	rankings.reverse()
	return rankings

def loadMovieLens(path='/Users/apple/collective_intelligence/mldata'):

	#获取影片标题
	movies = {}
	for line in open(path+'/u.item'):
		(id, title) = line.split('|')[0:2]
		movies[id] = title

	#加载数据
	prefs = {}
	for line in open(path+'/u.data'):
		(user, movieid, rating, ts) = line.split('\t')
		prefs.setdefault(user, {})
		prefs[user][movies[movieid]] = float(rating)
	return prefs




