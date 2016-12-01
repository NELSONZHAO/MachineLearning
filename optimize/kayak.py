#-*-coding:utf-8-*-
import time
import urllib2
import xml.dom.minidom

#KEY为申请api的秘钥
kayakkey = 'KEY'

#
def getkayaksession():
	#构造以URL以开启一个会话
	url = 'http://www.kayak.com/k/ident/apisession?token=%s&version=1' % kayakkey

	#解析返回的XML
	doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

	#找到<sid>xxxxxx</sid>标签
	sid = doc.getElementsByTagName('sid')[0].fisrtChild.data
	return sid
	
