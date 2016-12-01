#-*-coding:utf-8-*-
from PIL import Image,ImageDraw
my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]

class decisionnode:
	def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
		self.col = col			#待检验的判断条件所对应的列索引值
		self.value = value		#为了使结果为true，当前列必须匹配的值
		self.results = results	#保存的是针对于当前分支的结果，是一个dict，除了叶节点外，在其他节点上该值都为None
		self.tb = tb			#decisionnode
		self.fb = fb			#decisionnode

#在某一列上对数据集合进行拆分，能够处理数值型数据或名词性数据
def divideset(rows,column,value):
	#定义一个函数，令其告诉我们数据行属于第一组（返回true）还是第二组（返回false）
	split_function = None
	if isinstance(value,int) or isinstance(value,float):
		split_function = lambda row: row[column] >= value
	else:
		split_function = lambda row: row[column] == value

	#将数据集拆分成两个集合，并返回
	set1 = [row for row in rows if split_function(row)]
	set2 = [row for row in rows if not split_function(row)]
	return (set1,set2)

#对各种可能的结果进行计数（每一行数据的最后一列记录了这一计数结果）
def uniquecounts(rows):
	results = {}
	for row in rows:
		#计数结果在最后一列
		r = row[len(row)-1]
		#r是用户的付费选择
		if r not in results: results[r]=0
		results[r]+=1
	return results


#giniimpurity,随机放置的数据项出现于错误分类中的概率
def giniimpurity(rows):
	total = len(rows)
	counts = uniquecounts(rows)
	imp = 0
	for k1 in counts:
		p1 = float(counts[k1])/total
		for k2 in counts:
			if k1 == k2: continue #这一语句决定了“预测错误”这一条件
			p2 = float(counts[k2])/total
			imp += p1*p2
	return imp

#Entropy，熵是遍历所有可能的结果之后所得到的p(x)log(p(x))之和
def entropy(rows):
	from math import log
	log2 = lambda x: log(x)/log(2)
	results = uniquecounts(rows)
	#此处开始计算熵的值
	ent = 0.0
	for r in results.keys():
		p = float(results[r])/len(rows)
		ent = ent-p*log2(p)
	return ent

#构造决策树
def buildtree(rows,scoref=entropy,limit_gain=0.3):
	if len(rows)==0: return decisionnode() #如果接受的数据集为空，则返回一个decisionnode对象？
	current_score = scoref(rows) #计算当前数据集的熵值

	#定义一些变量以记录最佳拆分条件
	best_gain = 0
	best_criteria = None
	best_sets = None

	column_count = len(rows[0])-1
	for col in range(0,column_count): #遍历除最后一列的每一列（因为最后一列存储的是用户结果），寻找可能的分类条件
		#在当前列中生成一个由不同值构成的序列，用序列中的每一个值去进行分类，确定最合理的分界值
		column_values = {}
		for row in rows:
			column_values[row[col]]=1 #字典格式，保证了某一列中的值只出现一次
		#接下来根据这一列中的每个值，尝试对数据集进行拆分
		for value in column_values.keys():
			(set1,set2)=divideset(rows,col,value)

			#信息增益
			p = float(len(set1))/len(rows)
			gain = current_score-p*scoref(set1)-(1-p)*scoref(set2)
			if gain > best_gain and len(set1)>0 and len(set2)>0:
				best_gain = gain #最佳信息增益
				best_criteria = (col,value) #最佳分类标准
				best_sets = (set1,set2) #最佳分类数据集
	#创建子分支，开始递归/此时得到的best_gain是当前阶段分支中最大值
	#print best_criteria,best_gain
	if best_gain > limit_gain:
		trueBranch = buildtree(best_sets[0]) #传入满足第一层分解条件的数据集
		falseBranch = buildtree(best_sets[1]) #传入不满足第一层分解条件的数据集
		return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=trueBranch,fb=falseBranch)
	else: #此时已经没有分类的必要
		return decisionnode(results=uniquecounts(rows))

#输出树
def printtree(tree,indent=''):
	#这是一个叶节点吗？
	if tree.results!=None: #叶节点的结果非空，保存的是用户目标列的计数结果
		print str(tree.results)
	else:
		#打印判断条件
		print str(tree.col)+':'+str(tree.value)+'? '

		#打印分支
		print indent+'T->',
		printtree(tree.tb,indent+'  ')
		print indent+'F->',
		printtree(tree.fb,indent+'  ')

#可视化树
#节点及分支宽度
def getwidth(tree):
	if tree.tb == None and tree.fb == None: return 1
	return getwidth(tree.tb)+getwidth(tree.fb)

#节点深度，一个分支的深度等于其最长自分支的总深度加1
def getdepth(tree):
	if tree.tb==None and tree.fb==None: return 0
	return max(getdepth(tree.tb),getdepth(tree.fb))+1

#绘制图
def drawtree(tree,jpeg='tree.jpg'):
	w = getwidth(tree)*100
	h = getdepth(tree)*100+120

	img = Image.new('RGB',(w,h),(255,255,255))
	draw = ImageDraw.Draw(img)

	drawnode(draw,tree,w/2,20)
	img.save(jpeg,'JPEG')

#绘制节点
def drawnode(draw,tree,x,y):
	if tree.results == None:
		#得到每个分支的宽度
		w1 = getwidth(tree.fb)*100
		w2 = getwidth(tree.tb)*100

		#确定此节点要占据的总空间
		left = x-(w1+w2)/2
		right = x+(w1+w2)/2

		#绘制判断条件字符串
		draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))

		#绘制到分支的连线
		draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
		draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))

		#绘制分支的节点
		drawnode(draw,tree.fb,left+w1/2,y+100)
		drawnode(draw,tree.tb,right-w2/2,y+100)
	else:
		txt = ' \n'.join(['%s:%d'%v for v in tree.results.items()])
		draw.text((x-20,y),txt,(0,0,0))

#决策树测试（接受新的数据对其进行分类）
def classify(observation,tree):
	if tree.results!=None:
		output={}
		total = sum(tree.results.values())
		for k,v in tree.results.items():
			output[k]=v/total
		return output
	else:
		v = observation[tree.col]
		branch=None
		if isinstance(v,int) or isinstance(v,float):
			if v>=tree.value: branch=tree.tb
			else: branch=tree.fb
		else:
			if v==tree.value: branch=tree.tb
			else: branch=tree.fb
		return classify(observation,branch)

#剪枝
def prune(tree,mingain):
	#如果分支不是叶节点，则对其进行剪枝操作
	if tree.tb.results == None:
		prune(tree.tb,mingain)
	if tree.fb.results == None:
		prune(tree.fb,mingain)

	#如果两个子分支都是叶节点，则判断它们是否须要合并
	if tree.tb.results!=None and tree.fb.results!=None:
		#构造合并后的数据集
		tb,fb=[],[]
		for v, c in tree.tb.results.items():
			tb+=[[v]]*c
		for v, c in tree.fb.results.items():
			fb+=[[v]]*c

		#检查熵减少的情况
		delta = entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)
		if delta < mingain:
			#合并分支
			tree.tb, tree.fb = None,None
			tree.results=uniquecounts(tb+fb)

#带有处理缺失数据的预测函数
def mdclassify(observation,tree):
	#判断是否为叶节点，如果是，直接返回最后统计结果
	if tree.results!=None:
		output={}
		total = sum(tree.results.values())
		for k,v in tree.results.items():
			output[k]=v/total
		return output
	#如果不是叶节点
	else:
		#取观测数据的第一个分类值
		v = observation[tree.col]
		#如果该值缺失
		if v == None:
			tr,fr = mdclassify(observation,tree.tb),mdclassify(observation,tree.fb)
			tcount = sum(tr.values())
			fcount = sum(fr.values())
			#计算正分支占父枝的比例
			tw = float(tcount)/(tcount+fcount)
			#计算负分支占父枝的比例
			fw = float(fcount)/(tcount+fcount)
			result = {}
			for k,v in tr.items(): result[k]=v*tw
			for k,v in fr.items():
				if k not in result: result[k]=0
				result[k]+=v*fw
			return result
		#如果该值是一个范围tuple
		elif isinstance(v,tuple):
			#先判断最小值是否大于分支条件，若大于则遍历tb枝；最大值是否小于分支条件，若小于则遍历fb枝
			if v[0]>=tree.value:
				branch=tree.tb
				return mdclassify(observation,branch)
			elif v[1]<=tree.value:
				branch=tree.fb
				return mdclassify(observation,branch)
			else:
				tr,fr = mdclassify(observation,tree.tb),mdclassify(observation,tree.fb)
				tcount = sum(tr.values())
				fcount = sum(fr.values())
				#计算正分支占父枝的比例
				tw = float(tcount)/(tcount+fcount)
				#计算负分支占父枝的比例
				fw = float(fcount)/(tcount+fcount)
				result = {}
				for k,v in tr.items(): result[k]=v*tw
				for k,v in fr.items():
					if k not in result: result[k]=0
					result[k]+=v*fw
				return result
		#如果该值不缺失，那么与classify方法一样进行递归
		else:
			if isinstance(v,int) or isinstance(v,float):
				if v>=tree.value: branch=tree.tb
				else: branch=tree.fb
			else:
				if v == tree.value: branch=tree.tb
				else: branch = tree.fb
			return mdclassify(observation,branch)

#处理数值型结果,计算方差函数
def variance(rows):
	if len(rows)==0: return 0
	#取出输出结果列并转化为float
	data = [float(row[len(row)-1]) for row in rows]
	mean = sum(data)/len(data)
	variance=sum([(d-mean)**2 for d in data])/len(data)
	return variance




