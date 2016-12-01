#-*-coding:utf-8-*-
import time
import random
import math

people = [('Seymour','BOS'),
('Franny','DAL'),
('Zooey','CAK'),
('Walt','MIA'),
('Buddy','ORD'),
('Les','OMA')]

destination = 'LGA'

flights = {}
#
for line in file('schedule.txt'):
	origin,dest,depart,arrive,price = line.strip().split(',')
	flights.setdefault((origin,dest),[])

	#降航班详情添加入航班列表中
	flights[(origin,dest)].append((depart,arrive,int(price)))


def getminutes(t):
	x = time.strptime(t, '%H:%M')
	return x[3]*60+x[4]
	#这里传入的t必须是24小时制时间，否则返回的结果是错误的。x是struct_time类型

#格式化输出结果,r是往返航班选择的list
def printschedule(r):
	for d in range(len(r)/2):
		name = people[d][0]
		origin = people[d][1]
		#out存储来的信息
		out = flights[(origin,destination)][r[2*d]]
		#ret存储返回的信息
		ret = flights[(destination,origin)][r[2*d+1]]
		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,out[0],out[1],out[2],ret[0],ret[1],ret[2])

#计算成本,传入solution
def schedulecost(sol):
	totalprice = 0
	latestarrival = 0
	earliestdep = 24*60

	for d in range(len(sol)/2):
		#得到往程航班和返程航班
		origin = people[d][1]
		outbound = flights[(origin,destination)][int(sol[2*d])]
		returnf = flights[(destination,origin)][int(sol[2*d+1])]

		#总价格等于所有往程航班和返程航班价格之和
		totalprice+=outbound[2]
		totalprice+=returnf[2]

		#记录最晚到达时间和最早离开时间
		if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
		if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])

	#每个人必须在机场等待直到最后一个人到达为止
	#他们也必须在相同时间到达，并等候他们的返程航班
	totalwait = 0
	for d in range(len(sol)/2):
		origin = people[d][1]
		outbound = flights[(origin,destination)][int(sol[2*d])]
		returnf = flights[(destination,origin)][int(sol[2*d+1])]
		#加上每个人等待最晚到达人的时间
		totalwait+=latestarrival-getminutes(outbound[1])
		#加上每个人提前到达的时间
		totalwait+=getminutes(returnf[0])-earliestdep
	
	#是否对超期租车进行罚款
	if latestarrival<earliestdep: totalprice+=50

	return totalprice+totalwait

#随机搜索，遍历每一种随机解求结果再比较
def randomoptimize(domain,costf):
	best = 999999999
	bestr = None
	for  i in range(1000):
		#创建一个随机解
		r = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
		#得到成本
		cost = costf(r)

		#与到目前为止的最优解比较
		if cost<best:
			best = cost
			#记录题解
			bestr = r

	return r

#爬山法
def hillclimb(domain,costf):
	#创建一个随机解
	sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

	#主循环
	while 1:
		#创建相邻解的列表
		neighbors=[]

		for j in range(len(domain)):

			#在每个方向上相对于原值偏离一点
			if sol[j]>domain[j][0]:
				neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])

			if sol[j]<domain[j][1]:
				neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])

		#在相邻解中寻找最优解
		current = costf(sol)
		best = current
		for j in range(len(neighbors)):
			cost = costf(neighbors[j])
			if cost<best:
				best=cost
				sol=neighbors[j] #生成的新题解再返回进入循环
		
		#如果没有更好的解，则退出循环
		
		if best==current:
			break

	return sol

#模拟退火算法，T是温度，cool是冷却系数
def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
	#随机初始化值，需要强制类型转换为float类型
	vec = [float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]

	#循环事实上是一个不断退火的过程
	while T>0.1:
		#选择一个索引值
		i = random.randint(0,len(domain)-1)

		#选择一个改变索引值的方向
		dir = random.randint(-step,step)

		#创建一个代表题解的新列表，改变其中一个值
		vecb = vec[:]
		#给其中随便一个量进行改变
		vecb[i]+=dir
		if vecb[i]<domain[i][0]: vecb[i]=domain[i][0]
		elif vecb[i]>domain[i][1]: vecb[i]=domain[i][1]

		#计算当前成本和新的成本
		ea = costf(vec)
		eb = costf(vecb)

		#它是更好的解吗？或者是趋向最优解的可能的临界解吗？
		if (eb<ea or random.random()<pow(math.e,-(eb-ea)/T)):
			vec = vecb

		#降低温度
		T = T*cool
	vec = [int(v) for v in vec]
	return vec

#遗传算法，popsize为种群大小，step为步进距离，mutprob为变异比率，elite为精英比例，maxiter为最大迭代次数
def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):

	#变异操作
	def mutate(vec):
		i = random.randint(0,len(domain)-1)
		if random.random()<0.5 and vec[i]>domain[i][0]:
			return vec[0:i]+[vec[i]-step]+vec[i+1:]
		elif vec[i]<domain[i][1]:
			return vec[0:i]+[vec[i]+step]+vec[i+1:]

	#交叉操作
	def crossover(r1,r2):
		i = random.randint(1,len(domain)-2)
		return r1[0:i]+r2[i:]

	#构造初始种群
	pop = []
	#生成包含50个题解的种群pop
	for i in range(popsize):
		vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
		pop.append(vec)

	#每一代中有多少胜出者（精英选择数量）
	topelite = int(elite*popsize)

	#准循环
	for i in range(maxiter):
		#计算种群中每个题解的成本
		scores = [(costf(v),v) for v in pop]
		scores.sort() #排序
		ranked = [v for (s,v) in scores] #生成排序后的列表

		#从纯粹的胜出者开始
		pop = ranked[0:topelite]

		#添加变异和配对后的胜出者
		while len(pop)<popsize:
			if random.random()<mutprob:
				#满足变异比例时进行变异，并将改变异题解加入精英种群
				c = random.randint(0,topelite)
				pop.append(mutate(ranked[c]))
			else:
				#将交叉题解加入精英种群
				c1 = random.randint(0,topelite)
				c2 = random.randint(0,topelite)
				pop.append(crossover(ranked[c1],ranked[c2]))

		#打印当前最优值
		print scores[0][0]
	return scores[0][1]