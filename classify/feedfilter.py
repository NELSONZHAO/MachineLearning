#-*coding:utf-8-*-
import feedparser
import re

#接受一个博客订阅源的URL文件名并对内容项进行分类
def read(feed,classifier):
	#得到订阅源的内容并遍历循环
	f = feedparser.parse(feed)
	for entry in f['entries']:
		print 
		print '-------'
		#将内容打印输出
		print 'Title:	'+entry['title'].encode('utf-8')
		print 'Publisher:	'+entry['publisher'].encode('utf-8')
		print
		print entry['summary'].encode('utf-8')

		#将所有文本组合在一起，为分类器构造一个内容项
		fulltext='%s\n%s\n%s' % (entry['title'],entry['publisher'],entry['summary'])

		#将当前分类的最佳推测结果打印输出
		print 'Guess:	'+str(classifier.classify(entry))

		#请求用户给出正确分类，并据此进行训练
		cl = raw_input('Enter category: ')
		classifier.train(entry,cl)

#新特征提取函数
def entryfeatures(entry):
	splitter = re.compile('\\W*')
	f = {}

	#提取标题中的单词并进行标示
	titlewords = [s.lower() for s in splitter.split(entry['title']) if len(s)>2 and len(s)<20]
	for w in titlewords: f['Title:'+w]=1

	#提取摘要中的单词
	summarywords = [s.lower() for s in splitter.split(entry['summary']) if len(s)>2 and len(s)<20]

	#统计大写单词
	uc = 0
	for i in range(len(summarywords)):
		w = summarywords[i]
		f[w]=1 #每个词只计数一次
		if w.isupper(): uc+=1

		#将从摘要中获得的词组作为特征
		if i < len(summarywords)-1:
			twowords=' '.join(summarywords[i:i+1]) #将摘要中相邻两个单词进行组合
			f[twowords]=1

	#保持文章创建者和发布者名字的完整性
	f['Publisher:'+entry['publisher']]=1

	#UPPERCASE是一个“虚拟”单词，用以指示存在过多的大写内容
	if float(uc)/len(summarywords) > 0.3: f['UPPERCASE']=1

	return f