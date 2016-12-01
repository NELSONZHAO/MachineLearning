#-*-coding:utf-8-*-
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite

#构造过滤单词表，这些单词将被忽略
ignorewords = set(['the','of','to','and','a','in','is','it'])

class crawler:
	#初始化crawler类并传入数据库名称
	def __init__(self,dbname):
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()

	def dbcommit(self):
		self.con.commit()

	#辅助函数，用于获取条目的id，并且如果条目不存在，就将其加入数据库中
	def getentryid(self,table,field,value,createnew=True):
		cur = self.con.execute("select rowid from %s where %s='%s'" % (table,field,value))
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute("insert into %s (%s) values ('%s') " % (table,field,value))
			return cur.lastrowid
		else:
			return res[0]

	#为每个网页建立索引
	def addtoindex(self,url,soup):
		if self.isindexed(url): return
		print 'Indexing' + url

		#获取每个单词
		text = self.gettextonly(soup) #获取文本
		words = self.separatewords(text) #获取文本中的单词，返回的words是list

		#得到URL的id
		urlid = self.getentryid('urllist','url',url)

		#将每个单词与该url关联
		for i in range(len(words)):
			word = words[i]
			if word in ignorewords: continue
			wordid = self.getentryid('wordlist','word',word)
			self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))

	#从一个HTML网页中提取文字（不带标签）
	def gettextonly(self,soup):
		v = soup.string #取出不含标签的文本
		if v==None:
			c = soup.contents
			resulttext=''
			for t in c:
				subtext = self.gettextonly(t)
				resulttext+=subtext+'\n'
			return resulttext
		else:
			return v.strip()

	#根据任何非空白字符进行分词处理
	def separatewords(self,text):
		splitter = re.compile('\\W*') #将任何非单词字符视为分隔符
		return [s.lower() for s in splitter.split(text) if s!='']

	#如果url已经建立过索引，则返回true
	def isindexed(self,url):
		return False

	#添加一个关联两个网页的链接
	def addlinkref(self,urlFrom,urlTo,linkText):
		pass

	#从一个小组网页开始进行广度优先搜索，直至某一给定深度，期间为网页建立索引
	def crawl(self,pages,depth=2):
		for i in range(depth):
			newpages = set() #定义一个存储网页链接的集合
			for page in pages: #对pages进行遍历
				try:
					c = urllib2.urlopen(page)
				except:
					print "Could not open %s" % page
					continue
				soup = BeautifulSoup(c.read(),"html") #将结果生成soup对象
				self.addtoindex(page,soup)

				links = soup('a') #解析链接
				for link in links: #遍历解析出的链接
					if ('href' in dict(link.attrs)): #找出href头中的内容
						url = urljoin(page,link['href']) #将该内容添加至page尾部生成链接
						if url.find("'") != -1: continue
						url = url.split('#')[0] #去掉位置部分
						if url[0:4] == 'http' and not self.isindexed(url):
							newpages.add(url)
						linkText = self.gettextonly(link)
						self.addlinkref(page,url,linkText)

				self.dbcommit()
			pages = newpages
		pass

	#创建数据库表
	def createindextables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid,wordid,location)')
		self.con.execute('create table link(fromid integer,toid integer)')
		self.con.execute('create table linkwords(wordid,linkid)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.dbcommit()
