#-*-coding:utf-8-*-
from random import random, randint
import math
from pylab import *

def wineprice(rating,age):
	peak_age = rating-50

	#根据等级来计算价格
	price = rating/2
	if age>peak_age:
		#经过“峰值年”，后继5年里品质将会变差
		price = price*(5-(age-peak_age))
	else:
		#价格在接“峰值年”时会增加到原值的5倍
		price = price*(5*((age+1)/peak_age))

	if price<0: price=0
	return price

def wineset1():
	rows=[]
	for i in range(300):
		#随机生成年代和等级
		rating = random()*50+50
		age=random()*50

		#得到一个参考价格
		price=wineprice(rating,age)

		#增加“噪声”
		price *= (random()*0.4+0.8)

		#加入数据集
		rows.append({'input':(rating,age),'result':price})
	return rows

#Euclidian
def euclidean(v1,v2):
	d=0.0
	for i in range(len(v1)):
		d+=(v1[i]-v2[i])**2
	return math.sqrt(d)

#计算待估计向量与所有已有向量间的距离，并按照距离从近到远排序
def getdistances(data,vec1):
	distancelist=[]
	for i in range(len(data)):
		vec2=data[i]['input']
		distancelist.append((euclidean(vec1,vec2),i))
	distancelist.sort()  #将列表升序排列
	return distancelist

#估算价格
def knnestimate(data,vec1,k=5):
	#得到经过排序的距离值
	dlist = getdistances(data,vec1)
	avg=0.0

	#对钱k项结果求平均
	for i in range(k):
		idx=dlist[i][1]
		avg+=data[idx]['result']
	avg=avg/k
	return avg

#为近邻赋权重
#反函数法
def inverseweight(dist,num=1.0,const=0.1):
	return num/(dist+const) #加入常量的目的是避免完全相同或者高度相似的产品的反函数值趋近于无穷大

#减法函数：用一个常量值减去距离，如果相减结果大于0，则权重为相减结果；否则为0（常量选择是一个问题啊！）
def subtractweight(dist,const=1.0):
	if dist>const:
		return 0
	else:
		return const-dist

#gaussian函数法：最大值为1，克服反函数法的问题；最小值不会达到0，而不断趋近于0，因此克服了减法函数无法找到近邻的缺陷r
def gaussian(dist,sigma=10.0):
	return math.e**((-dist**2)/(2*sigma**2))

#加权KNN
def weightedknn(data,vec1,k=5,weightf=gaussian):
	#得到距离值
	dlist=getdistances(data,vec1)
	avg=0.0
	totalweight=0.0

	#得到加权平均值
	for i in range(k):
		dist=dlist[i][0]
		idx=dlist[i][1]
		weight=weightf(dist)
		#print weight,dist
		avg+=data[idx]['result']*weight
		totalweight+=weight
	avg=avg/totalweight
	return avg

#交叉验证
#拆分数据集
def dividedata(data,test=0.05):
	trainset=[]
	testset=[]
	for row in data:
		if random()<test:
			testset.append(row)
		else:
			trainset.append(row)
	return trainset,testset

#测试数据集
def testalgorithm(algf,trainset,testset):
	error=0.0
	for row in testset:
		#algf接受一个算法
		guess=algf(trainset,row['input'])
		error+=(row['result']-guess)**2
		return error/len(testset)


#算法评分
def crossvalidate(algf,data,trials=100,test=0.05):
	error=0.0
	#检验100次
	for i in range(trials):
		trainset,testset=dividedata(data,test)
		error+=testalgorithm(algf,trainset,testset)
	return error/trials

##########留一式交叉验证
def leaveoneout(algf,data):
	error=0.0
	#拆分数据集
	for i in range(len(data)):
		trainset=[]
		testset=[]
		testset.append(data[i])
		for j in range(len(data)):
			if j==i:continue
			else:
				trainset.append(data[i])
		#print '\n'+str(i+1)+':',
		#print len(testset),len(trainset)
		#调用计算函数
		error+=testalgorithm(algf,trainset,testset)

	return error/len(data)



#不同类型的值
def wineset2():
	rows=[]
	for i in range(300):
		rating=random()*50+50
		age=random()*50
		#通道aisle
		aisle=float(randint(1,20))
		bottlesize=[375.0,750.0,1500.0,3000.0][randint(0,3)]
		price=wineprice(rating,age)
		#默认一瓶750ml的wine价格
		price*=(bottlesize/750)
		price*=(random()*0.9+0.2)
		rows.append({'input':(rating,age,aisle,bottlesize),'result':price})

	return rows

#对数据进行缩放（归一）处理/scale是一个list，分别对应实体不同属性的缩放比例
def rescale(data,scale):
	scaleddata=[]
	for row in data:
		scaled=[scale[i]*row['input'][i] for i in range(len(scale))]
		scaleddata.append({'input':scaled,'result':row['result']})
	return scaleddata

#缩放结果（比例）优化
def createcostfunction(algf,data):
	def costf(scale):
		sdata=rescale(data,scale)
		return crossvalidate(algf,sdata,trials=10)
	return costf

weightdomain=[(0,20)]*4 #包含4个tuple的list

#
def wineset3():
	rows=wineset1()
	for row in rows:
		if random()<0.5:
			#葡萄酒是从折扣店里购买的
			row['result']*=0.5
	return rows

#估计概率密度/即指定规格葡萄酒落在某个价格范围内的概率
def probguess(data,vec1,low,high,k=5,weightf=gaussian):
	dlist=getdistances(data,vec1)
	nweight=0.0 #落在价格范围内的权重之和
	tweight=0.0 #所有近邻的权重之和

	for i in range(k):
		dist=dlist[i][0]
		idx=dlist[i][1]
		weight=weightf(dist)
		v=data[idx]['result']

		#判断当前数据点位于指定范围吗？
		if v>=low and v<=high:
			nweight+=weight
		tweight+=weight
	if tweight==0: return 0

	return nweight/tweight

#绘制累积概率分布图
def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
	t1=arange(0.0,high,1) #arange()每隔1生成一个数，从0到high
	cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
	plot(t1,cprob)
	show()

#绘制概率分布图
def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
	#建立一个代表价格的值域范围
	t1 = arange(0.0,high,0.1)

	#得到整个值域范围内的所有概率
	probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]

	#通过加上近邻概率的高斯计算结果，对概率值做平滑处理
	smoothed=[]
	for i in range(len(probs)):
		sv=0.0
		for j in range(0,len(probs)):
			dist=abs(i-j)*0.1
			weight=gaussian(dist,sigma=ss)
			sv+=weight*probs[j]
		smoothed.append(sv)
	smoothed=array(smoothed)

	plot(t1,smoothed)
	show()