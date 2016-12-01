#-*-coding:utf-8 -*-
from math import sqrt
from PIL import Image, ImageDraw
import random

def readfile(filename):
	lines = [line for line in file(filename)]

	#第一行是列标题
	colnames = lines[0].strip().split('\t')[1:]
	rownames = []
	data = []
	for line in lines[1:]:
		p = line.strip().split('\t')
		#每行的第一列是行名，是博客名
		rownames.append(p[0])
		#剩余部分就是该行对应的数据
		data.append([float(x) for x in p[1:]])
	return rownames, colnames, data

#列聚类，对矩阵进行转置
def rotatematrix(data):
	newdata = []
	for i in range(len(data[0])): #i代表列
		newrow = [data[j][i] for j in range(len(data))] #j代表行，返回list即为第i列数据
		newdata.append(newrow) #按照行加入数组
	return newdata

#pearson求两个博客的紧密度
def pearson(v1,v2):
	#简单求和
	sum1 = sum(v1)
	sum2 = sum(v2)

	#求平方和
	sum1Sq = sum([pow(v,2) for v in v1])
	sum2Sq = sum([pow(v,2) for v in v2])

	#求乘积之和
	pSum = sum([v1[i]*v2[i] for i in range(len(v1))])

	#计算r（Pearson Score)
	num = pSum - (sum1*sum2/len(v1))
	den = sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
	if den == 0: return 0

	return 1.0 - num/den #1-Pearson相关系数，为的是能够表示相似度越大的元素之间距离越小

#描述树的结构
class bicluster:
	def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
		self.left = left
		self.right = right
		self.vec = vec #向量
		self.id = id
		self.distance = distance

def hcluster(rows, distance=pearson):
	distances = {}
	currentclustid = -1

	#最开始的聚类就是数据集中的每一行，返回一个list，存储的是bicluster对象序列
	clust = [bicluster(rows[i],id=i) for i in range(len(rows))]

	#循环遍历开始聚类，直到最后变为一个类别为止
	while len(clust) > 1:
		lowestpair = (0,1) #将最近距离配对初始化为0和1
		closest = distance(clust[0].vec, clust[1].vec) #最近距离设置为0和1之间的距离

		#遍历每一个配对，寻找最小距离。下面这种遍历只需计算该元素与其后元素的相似度，计算量为(n-1)*n/2次
		for i in range(len(clust)):
			for j in range(i+1,len(clust)):
				#用distances来缓存距离的计算值
				if (clust[i].id, clust[j].id) not in distances:
					distances[(clust[i].id,clust[j].id)] = distance(clust[i].vec, clust[j].vec)

				d = distances[(clust[i].id, clust[j].id)]

				if d < closest:
					closest = d
					lowestpair = (i,j)

		#计算两个聚类的平均值
		mergevec = [clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i]/2.0 for i in range(len(clust[0].vec))]

		#建立新的聚类
		newcluster = bicluster(mergevec, left=clust[lowestpair[0]],right=clust[lowestpair[1]],distance=closest,id=currentclustid)

		#不在原始集合中的聚类，其id为负数。这里实际是更新clust对象，将第一步聚类中聚成一类的两个元素删除，而将新聚的类加入clust
		currentclustid -= 1
		del clust[lowestpair[1]]
		del clust[lowestpair[0]]
		clust.append(newcluster)
		#此后紧接着重新进入while循环，此时总类别减小1

	return clust[0] #此时clust已经聚为一类，返回最后的聚类对象

#打印分层结果
def printclust(clust, labels=None, n=0):
	#利用缩进来建立层级布局
	for i in range(n): print ' ',
	if clust.id<0:
		#负数标记代表这是一个分支
		print '-'
	else:
		#正数标记代表这是一个叶节点
		if labels == None: print clust.id
		else: print labels[clust.id]

	#现在开始打印右侧分支和左侧分支
	if clust.left != None: printclust(clust.left,labels=labels,n=n+1)
	if clust.right != None: printclust(clust.right,labels=labels,n=n+1)

#——————————————————————绘图部分——————————————————————————————————好难
#获得图形高度（递归的方式）
def getheight(clust):
	#这是一个叶节点吗？若是，则高度为1
	if clust.left == None and clust.right == None: return 1

	#否则，高度为每个分支的高度之和
	return getheight(clust.left) + getheight(clust.right)

#误差深度？不知道这是什么(这也是递归)
def getdepth(clust):
	#一个叶节点的距离深度为0.0
	if clust.left == None and clust.right == None: return 0

	#一个枝节点的距离等于左右两侧分支中距离较大者，加上该节点自身的距离
	return max(getdepth(clust.left),getdepth(clust.right)) + clust.distance

#创建图片
def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
	#高度和宽度
	h = getheight(clust)*20
	w = 1200
	depth = getdepth(clust)

	#由于宽度是固定的，因此我们需要对距离值做相应的调整
	scaling = float(w-150)/depth

	#新建一个白色背景的图片
	img = Image.new('RGB',(w,h),(255,255,255))
	draw = ImageDraw.Draw(img)

	draw.line((0,h/2,10,h/2),fill=(255,0,0))

	#画第一个节点
	drawnode(draw, clust, 10, (h/2),scaling,labels)
	img.save(jpeg, 'JPEG')

#图片调整
def drawnode(draw, clust, x, y, scaling, labels):
	if clust.id<0:
		h1 = getheight(clust.left)*20
		h2 = getheight(clust.right)*20
		top = y-(h1+h2)/2
		bottom = y+(h1+h2)/2
		#线的长度
		ll = clust.distance*scaling
		#聚类到其子节点的垂直线
		draw.line((x, top+h1/2, x, bottom-h2/2), fill=(255,0,0))

		#连接左侧节点的水平线
		draw.line((x, top+h1/2, x+ll, top+h1/2), fill=(255,0,0))

		#连接右侧节点的水平线
		draw.line((x, bottom-h2/2, x+ll, bottom-h2/2), fill=(255,0,0))

		#调整函数绘制左右节点
		drawnode(draw, clust.left, x+ll, top+h1/2, scaling, labels)
		drawnode(draw, clust.right, x+ll, bottom-h2/2, scaling, labels)
	else:
		#如果这是一个叶节点，则绘制节点的标签
		draw.text((x+5,y-7), labels[clust.id], (0,0,0))


#K-means聚类
def kcluster(rows, distance=pearson, k=4):
	#确定每个点的最小值和最大值
	ranges = [(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))] #双层迭代器，ranges存储了每一列的最小值和最大值

	#随机创建k个中心点
	clusters = [[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for j in range(k)] #极差*随机数+最小值

	lastmatches=None
	for t in range(100): #设置最大迭代次数，也就是说，当迭代到100次还没有收敛则停止
		print 'Iteration %d' % t #显示迭代进度
		bestmatches = [[] for i in range(k)] #生成包含四个list的一个list，bestmatches = [[], [], [], []]

		#在每一行中寻找距离最近的中心点。准确地说，是寻找四个中心点各自所包含的数据项，最后存储在bestmatches中
		for j in range(len(rows)): #遍历行
			row = rows[j]
			bestmatch = 0
			for i in range(k):
				d = distance(clusters[i],row)
				if d < distance(clusters[bestmatch], row): bestmatch = i
			bestmatches[bestmatch].append(j)
		#------------------以上循环返回一个包含四个中心点数据项列表的大列表bestmatches—————————————————————————————

		#如果结果与上一次相同，则整个过程结束
		if bestmatches == lastmatches: 
			print [len(bestmatches[i]) for i in range(len(bestmatches))]
			break
		lastmatches = bestmatches
		print [len(bestmatches[i]) for i in range(len(bestmatches))]

		#把中心点移到其所有成员的平均位置处
		for i in range(k):
			avgs = [0.0] * len(rows[0]) #返回一个含有len(row[0])个元素的列表，列表元素均为0.0
			if len(bestmatches[i]) > 0: #如果第i类中有元素
				for rowid in bestmatches[i]: #遍历这个第i个聚类的元素，这里面每个元素代表的是数据项的id
					for m in range(len(rows[rowid])): #遍历当前数据项的列：m
						avgs[m] += rows[rowid][m] #将当前数据项的列加在avgs对应列
				#对avgs求平均值
				for j in range(len(avgs)): #遍历avgs的列
					avgs[j]/=len(bestmatches[i]) #对每一列取平均值
				clusters[i] = avgs #将第i类所有成员的平均位置赋给该类的中心点

	return bestmatches #啊啊啊啊啊啊，注意缩进啊！！！！！

#Tanimoto系数
def tanimoto(v1, v2):
	c1,c2,shr =0,0,0

	for i in range(len(v1)):
		if v1[i]!=0: c1+=1 #出现在v1中
		if v2[i]!=0: c2+=1 #出现在v2中
		if v1[i]!=0 and v2[i]!=0: shr+=1 #在两个句子中都出现

	return 1.0 - (float(shr)/(c1+c2-shr))

#多维缩放
def scaledown(data,distance=pearson,rate=0.01):
	n = len(data)

	#每一对数据项之间的真实距离
	realdist  =[[distance(data[i], data[j]) for j in range(n)] for i in range(0,n)]

	#随机初始化节点在二维空间中的起始位置
	loc = [[random.random(),random.random()] for i in range(n)] #初始化随机位置
	fakedist = [[0.0 for j in range(n)] for i in range(n)] #初始化距离都为0

	lasterror = None
	#开始迭代
	for m in range(0,1000):
		#寻找投影后的距离
		for i in range(n):
			for j in range(n):
				fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))
		#移动节点
		grad = [[0.0,0.0] for i in range(n)]

		totalerror = 0
		for k in range(n):
			for j in range(n):
				#不和自己比较
				if j == k: continue
				#误差值等于目标距离与当前距离之间差值的百分比
				errorterm = (fakedist[j][k]-realdist[j][k])/realdist[j][k]

				#每一个节点都须要根据误差的多少，按比例移离或移向其他节点
				grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm #移动横坐标的量
				grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm #移动纵坐标的量

				#记录总的误差值
				totalerror += abs(errorterm)
		print totalerror

		#如果节点移动之后的情况变得更糟，则程序结束
		if lasterror and lasterror<totalerror:break
		lasterror = totalerror

		#根据rate参数与grad值相乘的结果，移动每一个节点
		for k in range(n):
			loc[k][0]-=rate*grad[k][0] #移动横坐标位置
			loc[k][1]-=rate*grad[k][1] #移动纵坐标位置

	return loc

#绘制二维图像
def draw2d(data, labels, jpeg='mds2d.jpg'):
	img = Image.new('RGB',(2000,2000),(255,255,255))
	draw = ImageDraw.Draw(img)
	for i in range(len(data)):
		x=(data[i][0]+0.5)*1000
		y=(data[i][1]+0.5)*1000
		draw.text((x,y), labels[i], (0,0,0))
	img.save(jpeg,'JPEG')

#——————————————————————————————————作业————————————————————————————————————————
#修改后的k-Means算法,，可以返回总数据项之间的距离总和以及它们各自的中心点位置
def kcluster_m(rows, distance=pearson, k=4):
	#确定每个点的最小值和最大值
	ranges = [(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))] #双层迭代器，ranges存储了每一列的最小值和最大值

	#随机创建k个中心点
	clusters = [[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for j in range(k)] #极差*随机数+最小值

	lastmatches=None
	for t in range(100): #设置最大迭代次数，也就是说，当迭代到100次还没有收敛则停止
		#print 'Iteration %d' % t #显示迭代进度
		bestmatches = [[] for i in range(k)] #生成包含四个list的一个list，bestmatches = [[], [], [], []]

		#在每一行中寻找距离最近的中心点。准确地说，是寻找四个中心点各自所包含的数据项，最后存储在bestmatches中
		for j in range(len(rows)): #遍历行
			row = rows[j]
			bestmatch = 0
			for i in range(k):
				d = distance(clusters[i],row)
				if d < distance(clusters[bestmatch], row): bestmatch = i
			bestmatches[bestmatch].append(j)
		#------------------以上循环返回一个包含四个中心点数据项列表的大列表bestmatches—————————————————————————————

		#如果结果与上一次相同，则整个过程结束
		if bestmatches == lastmatches: 
			#print [len(bestmatches[i]) for i in range(k)]
			break
		lastmatches = bestmatches
		#print [len(bestmatches[i]) for i in range(k)]

		#把中心点移到其所有成员的平均位置处
		for i in range(k):
			avgs = [0.0] * len(rows[0]) #返回一个含有len(row[0])个元素的列表，列表元素均为0.0
			if len(bestmatches[i]) > 0: #如果第i类中有元素
				for rowid in bestmatches[i]: #遍历这个第i个聚类的元素，这里面每个元素代表的是数据项的id
					for m in range(len(rows[rowid])): #遍历当前数据项的列：m
						avgs[m] += rows[rowid][m] #将当前数据项的列加在avgs对应列
				#对avgs求平均值
				for j in range(len(avgs)): #遍历avgs的列
					avgs[j]/=len(bestmatches[i]) #对每一列取平均值
				clusters[i] = avgs #将第i类所有成员的平均位置赋给该类的中心点

	#遍历所有的分类，计算每个类别中数据项距离该类中心的距离
	dist = [0.0 for i in range(k)] #初始化每个类别的距离总和为0
	for i in range(k):
		for j in bestmatches[i]:
			dist[i] += distance(rows[j], clusters[i]) #计算第i类中每个元素距离该聚类中心的距离并累加

	#计算所有数据项的距离总和
	sum_dist = sum(dist)

	return bestmatches,clusters,sum_dist #啊啊啊啊啊啊，注意缩进啊！！！！！

#对总距离进行统计，观察数据项总距离随着聚类数的化
def sumdist_list(data, distance=pearson,k=4):
	#定义一个字典，key值为聚类数，value值为该聚类数下的总距离
	dist_dict = {}
	#循环调用k-means聚类方法将得到的总距离统计的字典
	for k in range(1,len(data)):
		dist_dict.setdefault(k,0)
		results, centers, dist = kcluster_m(data,k=k)
		dist_dict[k] = dist
		print '当前定义的类别为 %d' % k

	print [(k,v) for k,v in dist_dict.items()]
	#return dist_dict



