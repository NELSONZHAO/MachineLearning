#-*- coding:utf-8 -*-
import feedparser
import re

#返回一个RSS订阅源的标题和包含单词计数情况的字典
def getwordwcounts(url):
	#解析订阅源
	d = feedparser.parse(url) #解析以后返回的d是一个字典
	wc = {} #wc是wordcount，即统计词频的字典

	#循环遍历所有的文章条目
	for e in d.entries:
		if 'summary' in e: summary = e.summary
		else: summary = e.description

		#提取一个单词列表
		words = getwords(e.title+' '+e.summary)
		for word in words:
			wc.setdefault(word, 0)
			wc[word] += 1
	return d.feed.title, wc

#处理文本单词
def getwords(html):
	#去除所有HTML标记
	txt = re.compile(r'<[^>]+>').sub('',html) #正则表达式表示了<>的标签

	#利用所有非字母字符拆分出单词
	words = re.compile(r'[^A-Z^a-z]+').split(txt)

	#转换成小写
	return [word.lower() for word in words if word != '']

apcount = {}
wordcounts = {}
feedlist = [line for line in file('/Users/apple/collective_intelligence/chapter3/feedlist.txt')] #将feelist文件中的所有url链接存为list
#遍历每个url
for feedurl in feedlist:
	try:
		title, wc = getwordwcounts(feedurl) #得到博客标题和词频统计字典
		wordcounts[title] = wc
		for word, count in wc.items(): #在当前url的博客的词频统计字典中，遍历单词和词频统计
			apcount.setdefault(word, 0) #对于每个单词作为字典的key，每次循环将置为0
			if count > 1: #词频大于1
				apcount[word] += 1 #才计数
	except:
		print 'Failed to parse feed %s' % feedurl

wordlist = []
for w, bc in apcount.items():
	frac = float(bc)/len(feedlist)
	if frac > 0.1 and frac < 0.5:
		wordlist.append(w)

#建立文件
out = file('blogdata.txt','w')
out.write('Blog')
for word in wordlist:
	out.write('\t%s' % word)
out.write('\n')
for blog, wc in wordcounts.items():
	out.write(blog)
	for word in wordlist:
		if worrd in wc:
			out.write('\t%d' % wc[word])
		else:
			out.write('\t0')
	out.write('\n')