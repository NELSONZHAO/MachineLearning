#-*-coding:utf-8-*-
import httplib
from xml.dom.minidom import parse, parseString,Node

devKey='0a65644f-1147-407b-97f9-3c331ce9c85e'
appKey='NelsonZh-DataAnal-PRD-05770b0cf-a793b0f5'
certKey='PRD-5770b0cf284b-8ed5-413b-a511-7982'
userToken='AgAAAA**AQAAAA**aAAAAA**Iu6nVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkYaoAZSFpAmdj6x9nY+seQ**9mMDAA**AAMAAA**KVuO0xHu3Bl5ZnSNI1pL2g/j6Di+SkJ0QNmoSTDQLsm7vzBPJhCkojb3zNMlH1y7EuRJdtm7d0EA5JiFYXobr6KKDRTjmNniJmVl21WYxSn3IK/ef2bePEjOoxmmiz2YnJVYOeb+/4I7dsqD0OmNdgf70SPYaVZ8eTWEMwbXr6Wx9e5Pw/fZblxlDV0ZiLTab12Z0nxg0D0wwRpcUgBezAxmj6SaVF24KtDcrLb0IAsGEhWyC2h2drVASheND55CCJa2cOoKE1Pl4drWwSPBT2ZkYyK7U/cB5UkzpYnN6+qZMCaFkgu+/vIHwmsB9CPlwxFEiyPHB076WwlaavjvW3et3p5CpVhKH8qBYxkfBwhnFRa6Qn5eGGPOEr03OZo2BPXnn+Lly1dcruF64NPTufe8T7mgwP6fNosEq6dh+4Ch5Ltz7tcGlfpuQBkOp7/9HLXlPQyKeIWerO3t78ifOegf2oErlGzJnutAV0ZEzWhJFgCDFgpWDG/TGs3yIJ2onnRaYkVHWZ1qM5k47pbeBiUonaRGCQwwmu5ArRzAUJzlDlkR2GptVr93uPLSYE3GwYCvaOlfM897x+whibCgtrfYXZKRdnMKs/v6AfBDHIG6HyPgMFearTYTFVwo8kD7dC7dUm0lQPYc/FWgpEsFr9X+YYkMjzpFpHdCBTl5vQlDP8Rilkfr0LP952HJ90HpYUUeZcNfset7CaSzlZOFP0HvaM04/sApPUe5FNEUfviNTHJ1dnePoCwIXlZ5AQRA'
serverUrl='api.ebay.com'

#返回头信息
def getHeaders(apicall,siteID="0",compatabilityLevel="433"):
	headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
	"X-EBAY-API-DEV-NAME": devKey,
	"X-EBAY-API-APP-NAME": appKey,
	"X-EBAY-API-CERT-NAME": certKey,
	"X-EBAY-API-CALL-NAME": apicall,
	"X-EBAY-API-SITEID": siteID,
	"Content-Type":"text/xml"}
	return headers

#发送请求
def sendRequest(apicall,xmlparameters):
	#建立连接
	connection=httplib.HTTPConnection(serverUrl)
	#提交headers
	connection.request("POST",'/ws/api.dll',xmlparameters,getHeaders(apicall))
	#获取结果
	response=connection.getresponse()
	if response.status!=200:
		print "Error sending request:" + response.reason
	else:
		data=response.read()
		connection.close()
	return data

#查找节点并返回节点对应内容
def getSingleValue(node,tag):
	nl=node.getElementByTagName(tag)
	if len(nl)>0:
		tagNode=nl[0]
		if tagNode.hasChildNodes():
			return tagNode.firstChild.nodeValue
	return '-1'

#
def doSearch(query,categoryID=None,page=1):
	xml = "<?xml version='1.0' encoding='utf-8'?>"+\
		"<GetSearchResultsRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
		"<RequesterCredentials><eBayAuthToken>" +\
		userToken +\
		"</eBayAuthToken></RequesterCredentials>" + \
		"<Pagination>"+\
		"<EntriesPerPage>200</EntriesPerPage>"+\
		"<PageNumber>"+str(page)+"</PageNumber>"+\
		"</Pagination>"+\
		"<Query>" + query + "</Query>"
	if categoryID!=None:
		xml+="<CategoryID>"+str(categoryID)+"</CategoryID>"
	xml+="</GetSearchResultsRequest>"

	data=sendRequest('GetSearchResults',xml)
	response = parseString(data)
	itemNodes = response.getElementsByTagName('Item');
	results = []
	for item in itemNodes:
		itemId=getSingleValue(item,'ItemID')
		itemTitle=getSingleValue(item,'Title')
		itemPrice=getSingleValue(item,'CurrentPrice')
		itemEnds=getSingleValue(item,'EndTime')
		results.append((itemId,itemTitle,itemPrice,itemEnds))
	return results

def getCategory(query='',parentID=None,siteID='0'):
	lquery=query.lower()
	xml = "<?xml version='1.0' encoding='utf-8'?>"+\
		"<GetCategoriesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
		"<RequesterCredentials><eBayAuthToken>" +\
		userToken +\
		"</eBayAuthToken></RequesterCredentials>"+\
		"<DetailLevel>ReturnAll</DetailLevel>"+\
		"<ViewAllNodes>true</ViewAllNodes>"+\
		"<CategorySiteID>"+siteID+"</CategorySiteID>"
	if parentID==None:
		xml+="<LevelLimit>1</LevelLimit>"
	else:
		xml+="<CategoryParent>"+str(parentID)+"</CategoryParent>"
		xml += "</GetCategoriesRequest>"
		data=sendRequest('GetCategories',xml)
		categoryList=parseString(data)
		catNodes=categoryList.getElementsByTagName('Category')
	for node in catNodes:
		catid=getSingleValue(node,'CategoryID')
		name=getSingleValue(node,'CategoryName')
		if name.lower().find(lquery)!=-1:
			print catid,name