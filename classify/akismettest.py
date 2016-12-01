#-*-coding:utf-8-*-
import akismet

defaultkey = 'YOURKEYHERE'
pageurl = "http://yoururlhere.com"
defaultagent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

def isspam(comment,author,ipaddress,agent=defaultagent,apikey=defaultkey):
	try:
		valid = akismet.verify_key(apikey,pageurl)
		if valid:
			return akismet.comment_check(apikey,pageurl,ipaddress,agent,comment_content=comment,comment_author_email=author,coment_type="comment")
		else:
			print "Invalid key"
			return False
	except akismet.AkismetError, e:
		print e.response, e.statuscode
		return False
