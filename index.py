import requests
import json
import urllib3
import urllib
import pymysql
import random
from PIL import ImageFile
from flask import Flask, request, make_response, jsonify
import re
ERROR_MESSAGE = '네트워크 접속에 문제가 발생하였습니다. 잠시 후 다시 시도해주세요.'
NOT_FOUND_MESSAGE = '가게를 찾지 못하였습니다. 다시 한 번 말씀 해 주세요.'
GOOD_BYE_MESSAGE = '감사합니다. ^^ 다음에 또 이용해 주세요~'
NO_MESSAGE = '다시 고르시려면 점심 뭐 먹지? 등의 말을 입력하여 주세요'
URL_OPEN_TIME_OUT = 10
others=''
titles=''
temprdadr=''
app = Flask(__name__)
# -----------------------------
# DB서버와 연동
# -----------------------------
conn = pymysql.connect(
    host = "jmm.cvxf3ahhscl8.us-east-2.rds.amazonaws.com",
    port = 3306,
    user = 'JMM',
    passwd = '1q2w3e4r',
    db = 'JMM',
    charset = 'utf8')

cur = conn.cursor()

# -----------------------------
# 선호도 받아오는 함수 (query 포함)
# -----------------------------
def choice_preference(region_kind):
	answer = region_kind.split()
	types = answer[1]
	store = titles #여기 봐야됨
	#store = "함지박"
	query="예"
	total = cur.execute("SELECT * FROM CHOICE WHERE CHO_TYPE='%s' and CHO_LOC='%s' and CHO_STORE='%s';" % (types,answer[0],store))
	choice_count = cur.execute("SELECT * FROM CHOICE WHERE CHO_STORE='%s' and CHO_LOC='%s' and CHO_TYPE='%s' and CHO_QUERY='%s';"  % (store,answer[0],types,query))
	print(choice_count)
	print(total)
	print(store)
	print(answer[0])
	print(types)
	try:
		avg = int(choice_count / total * 100)
		print("선택한 %s 맛집 선호도 : " % types + str(avg) + "%")
		conn.commit()
		if avg>0:
			return avg
	except ZeroDivisionError as e:
		print(e)

# ------------------------------
# 선호도 받아오는 함수 (query 미포함)# 지역선호도
# ------------------------------
def choice_preference_notquery(region_kind):
	answer = region_kind.split()
	types = answer[1]
	store = titles
	print(store)
	total = cur.execute("SELECT * FROM CHOICE WHERE CHO_TYPE='%s' and CHO_LOC='%s';" % (types,answer[0]))
	choice_count = cur.execute("SELECT * FROM CHOICE WHERE CHO_TYPE='%s' and CHO_LOC='%s' and CHO_STORE='%s';" % (types,answer[0],store))
	try:
		avg = int(choice_count / total * 100)
		print("선택한 %s 맛집 선호도 : " % types + str(avg) + "%")
		conn.commit()
		if avg>0:
			return avg
	except ZeroDivisionError as e:
		print(e)
# -----------------------------
# STORE table에 insert해주는 함수
# -----------------------------
def store_insert(region_kind):
	answer = storeInfo(region_kind)
	
	answer = answer.replace("\n","").replace("🐥","^")
	answer = re.split('\W+\s', answer)
	print('###################')
	print(answer)
	print('###################')
	
	'''
	num = ''
	name = titles
	phone = answer[4]
	rnaddress = temprdadr
	address  = answer[2]

	cur.execute("INSERT INTO STORE VALUES('%s','%s','%s','%s','%s');" %(num,name,phone,rnaddress,address))
	conn.commit()
	conn.close()
'''

# -----------------------------
# CHOICE table에 insert해주는 함수 (query 포함)
# -----------------------------
def choice_insert(region_kind,weard):
	answer = region_kind.split()
	loc = answer[0]
	types = answer[1]
	store = titles #여기도 같음
	#store = "함지박"
	if(weard):
		cur.execute("INSERT INTO CHOICE VALUES('%s','%s','%s','%s');" %(loc,types,store,"예"))
	else:
		cur.execute("INSERT INTO CHOICE VALUES('%s','%s','%s','%s');" %(loc,types,store,""))
	conn.commit()
# ------------------------------------
# CHOICE table에 insert해주는 함수 (query 미 포함)
# ------------------------------------
def choice_insert_notquery(region_kind):
	answer = region_kind.split()
	loc = answer[0]
	types = answer[1]
	store = titles
	cur.execute("INSERT INTO CHOICE VALUES('%s','%s','%s');"%(loc,types,store))
	conn.commit()
# -----------------------------
# Client 가 요구한 STORE table을 select해주는 함수
# -----------------------------
def store_select(store):
    cur.execute("SELECT * FROM STORE WHERE STO_NAME='%s'" %store)
    rows = cur.fetchall()

    for row in rows:
        print("%s" %row[1])
        print("%s" %row[2])
        print("%s" %row[3])

    conn.commit()
    conn.close()

# -----------------------------
# UTF-8로 Encode하고, 적절하게 문자열로 반환해주는 함수
# -----------------------------
def URLEncode(region_or_title):
    encoded=str(region_or_title.encode('utf-8'))
    splited=encoded.replace("\\"," ").replace("x","%").replace("\'"," ").split()
    splited=splited[1:]
    output="".join(splited)
    return output

# -----------------------------
# <b>태그 제거해주는 함수
# -----------------------------
def remove_tag(content):
   cleanr =re.compile('<.*?>')
   cleantext = re.sub(cleanr, '', content)
   return cleantext



# ---------------------------------------
# 네이버 API 이용해 이미지 링크 구해주는 함수
# ---------------------------------------
def getImage(title):

	client_id="fechS4lsKMLVwarW0I01"
	client_secret = "MxwdD119Rv"
	encText=urllib.parse.quote(title)
	image_url= 'https://openapi.naver.com/v1/search/image?query='+encText
	request = urllib.request.Request(image_url)
	request.add_header("X-Naver-Client-Id", client_id)
	request.add_header("X-Naver-Client-Secret", client_secret)
	response=urllib.request.urlopen(request)
	rescode=response.getcode()
	img_not_found='<Photo>http://ugimoa.com/xeshop/img/no_images.jpg</Photo>'
	if(rescode==200):
		response_body=response.read()
		locinfo=response_body.decode('utf-8')
		json_data = json.loads(locinfo)
		item = json_data.get('items')
		if item:
			if len(item)==1:
				j=0
			else:
				j=random.randint(0,len(item)-1)
			s_title = remove_tag(item[j].get('title'))
			s_link=remove_tag(item[j].get('link'))
			image_information = '<Photo>'+s_link+'</Photo>'
				#[s_title, s_telephone, s_address, s_roadAddress, s_mapy, s_mapx]
			return image_information
		else:
			return img_not_found
	#else:
	#	return jsonify(response)
	
	
	
	
# ----------------------------------------
# 네이버 API로 지역명을 받아 크롤링 하여 가게정보를 구하는 함수
# ----------------------------------------
	
def storeInfo(region_kind):
	global titles
	global temprdadr
	client_id = "fechS4lsKMLVwarW0I01"
	client_secret = "MxwdD119Rv"
	temp=region_kind.split(" ")
	region=temp[0]
	location = region_kind
	encText = urllib.parse.quote(location)
	store_url = 'https://openapi.naver.com/v1/search/local?query='+encText
	request = urllib.request.Request(store_url)
	request.add_header("X-Naver-Client-Id", client_id)
	request.add_header("X-Naver-Client-Secret", client_secret)
	response = urllib.request.urlopen(request)
	rescode = response.getcode()
	
	if(rescode ==200):
		response_body = response.read()
		locinfo = response_body.decode('utf-8')

		json_data = json.loads(locinfo)
		item = json_data.get('items')
		print(len(item))
		
		if item:
			if len(item)==1:
				j=0
			else:
				j=random.randint(0,len(item)-1)
			print(item[j])
			s_title = remove_tag(item[j].get('title'))
			titles=s_title
			choice_percent=choice_preference_notquery(region_kind)
			print("storeInfo내의 titles : "+titles)
			s_telephone = remove_tag(item[j].get('telephone'))
			s_address = remove_tag(item[j].get('address'))
			s_roadAddress = remove_tag(item[j].get('roadAddress'))
			temprdadr=s_roadAddress
			s_mapx = remove_tag(item[j].get('mapx'))
			s_mapy = remove_tag(item[j].get('mapy'))
			s_description=remove_tag(item[j].get('description'))
			s_link=remove_tag(item[j].get('link'))
			store_information = ''
			if len(s_title) >0 :
				store_information += '🐥 가게 이름 : ' + s_title + '\n'
				if len(s_address) > 0 :
					store_information += '🐥 주소 : ' + s_address + '\n'
					if len(s_telephone) > 0 :
						store_information += '🐥 전화번호 : ' + s_telephone + '\n'
						if len(s_description) > 0 :
							store_information += '🐥 요약 : ' + s_description + '\n'
							if len(s_link) > 0 :
								store_information += '🐥 사이트 : ' + s_link + '\n'
			
			store_information += '🐥 자세히 보기 (🔍버튼을 눌러주세요): http://maps.google.com/?q='+URLEncode(region)+'+'+URLEncode(titles)+'\n\n😃이 가게를 선택하시겠어요?\n(예/아니오)로만 답하여 주세요.😃\n(이 가게의 선택 점유율 : '+str(choice_percent)+'%)'
			print(store_information)
			#[s_title, s_telephone, s_address, s_roadAddress, s_mapy, s_mapx]
			return store_information
		else:
			
			print(NOT_FOUND_MESSAGE)
			return NOT_FOUND_MESSAGE
	else:
		return jsonify(response)
	
	
	
	
	
# ----------------------------------------------------
# 사진 구함
# ----------------------------------------------------
def get_photo(answer):

	photo = ''
	index = answer.find('</Photo>')
    
	if index >= 0:
		photo = answer[len('<Photo>'):index]
		answer = answer[index + len('</Photo>'):]
	
	return answer, photo
# ----------------------------------------------------
# 사진 크기 구함
# ----------------------------------------------------
def get_photo_size(url):
	width = 0
	height = 0
	if url == '':
		return width, height

	try:
		file = urllib3.urlopen(url, timeout=URL_OPEN_TIME_OUT)
		p = ImageFile.Parser()
		while 1:
			data = file.read(1024)

			if not data:
				break

			p.feed(data)

			if p.image >= 0:
				width = p.image.size[0]
				height = p.image.size[1]
		file.close()
	except:
		print
		'get_photo_size error'
	return width, height


# ----------------------------------------------------
# 메뉴 구함
# ----------------------------------------------------
def get_menu(answer):
    # --------------------------------
    # 메뉴가 있는지 검사
    # --------------------------------
    menu = []
    index = answer.find(' 1. ')

    if index < 0:
        return answer, menu

    menu_string = answer[index + 1:]
    answer = answer[:index]

    # --------------------------------
    # 메뉴를 배열로 설정
    # --------------------------------
    number = 1

    while 1:
        number += 1
        search_string = ' %d. ' % number
        index = menu_string.find(search_string)

        if index < 0:
            menu.append(menu_string[3:].strip())
            break;

        menu.append(menu_string[3:index].strip())
        menu_string = menu_string[index + 1:]

    return answer, menu


# ----------------------------------------------------
# 메뉴 버튼 구함
# ----------------------------------------------------
def get_menu_button(menu):
    if len(menu) == 0:
        return None

    menu_button = {
        'type': 'buttons',
        'buttons': menu
    }

    return menu_button


# ----------------------------------------------------
# Dialogflow에서 대답 구함
# ----------------------------------------------------
def get_answer(text, user_key):
    # --------------------------------
    # Dialogflow에 요청
    # --------------------------------
	data_send = {
	    'lang': 'ko',
	    'query': text,
	    'sessionId': user_key,
	    'timezone': 'Asia/Seoul'
	}

	data_header = {
	    'Content-Type': 'application/json; charset=utf-8',
	    'Authorization': 'Bearer a5bc367b005b4bf08e0c4d3b4b0b8a91'  
        # Dialogflow의 Client access token 입력
	}

	dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'

	res = requests.post(dialogflow_url,
						data=json.dumps(data_send),
						headers=data_header)

    # --------------------------------
    # 대답 처리
    # --------------------------------
	if res.status_code != requests.codes.ok:
		return ERROR_MESSAGE

	data_receive = res.json()
	answer = data_receive['result']['fulfillment']['speech']
	#answer += data_receive['result']['fulfillment']['photo']
	print(answer)
	return answer


# ----------------------------------------------------
# 지역을 받아서 가게정보를 알려주는 함수
# ----------------------------------------------------
def get_place(region_kind):
	
	#answer=storeInfo(region_kind)
	answer =storeInfo(region_kind)
	
	return answer


# ----------------------------------------------------
# 피자 주문 처리
# ----------------------------------------------------
def process_pizza_order(pizza_name, address):
    answer = pizza_name.encode('UTF-8') + '를 주문하셨습니다.'
    answer += " '" + address.encode('UTF-8') + "'의 주소로 지금 배달하도록 하겠습니다."
    answer += ' 이용해주셔서 감사합니다.'

    return answer


# ----------------------------------------------------
# Dialogflow fullfillment 처리
# ----------------------------------------------------
@app.route('/', methods=['POST'])
def webhook():
	global others
	res={}
    # --------------------------------
    # 액션 구함
    # --------------------------------
	req = request.get_json(force=True)
	action = req['result']['action']
	print(req['result']['resolvedQuery'])
    # --------------------------------
    # 액션 처리
    # --------------------------------
	if action == 'FALLBACK':
		region_kind = req['result']['resolvedQuery']
		others=region_kind
		answer = get_place(region_kind)
		if answer != NOT_FOUND_MESSAGE:
			temp = region_kind.split(" ")
			titles = str(temp[1])
			res = {'speech' : str(getImage(titles))+answer}
		else:
			res = {'speech' : NOT_FOUND_MESSAGE}
	
	elif action =='selectit':
		choose_type = req['result']['parameters']['yesEntity']
		if choose_type=="예":
			choice_insert_notquery(others)
			print('################')
			print("DB에 입력완료 : "+str(others))
			print('################')
			res={'speech' : GOOD_BYE_MESSAGE}
	elif action =='notselect':
		choose_type = req['result']['parameters']['noEntity']
		if choose_type=="아니오":
			print('################')
			print("\'아니오\' 이므로 DB 입력 안함")
			print('################')
			res={'speech' : NO_MESSAGE}
			
	
	'''
	elif action == 'pizza_order':
		pizza_name = req['result']['parameters']['pizza_type']
		address = req['result']['parameters']['address']
		answer = process_pizza_order(pizza_name, address)
	else:
		answer = 'error'
	'''
	
	return jsonify(res)


# ----------------------------------------------------
# 카카오톡 키보드 처리
# ----------------------------------------------------
@app.route("/keyboard")
def keyboard():
    res = {
        'type': 'buttons',
        'buttons': ['대화하기']
    }

    return jsonify(res)


# ----------------------------------------------------
# 카카오톡 메시지 처리
# ----------------------------------------------------
@app.route('/message', methods=['POST'])
def message():

	req = request.get_json()
	user_key = req['user_key']
	content = req['content']

	if len(user_key) <= 0 or len(content) <= 0:
		answer = ERROR_MESSAGE
#-----------------------------메세지 받기 -------------------------------#



	if content == u'대화하기':
		answer = '안녕하세요. 점심을 알려주는 챗봇입니다. 점심 메뉴를 추천받고 싶으시다면 ex) 점심 뭐 먹지? 등으로 입력하여 주세요'
	else:
		answer = get_answer(content, user_key)
#-----------------------------답변 구함 --------------------------------#


	
	answer, photo = get_photo(answer)
	photo_width, photo_height = get_photo_size(photo)
	photo_width=200
	photo_height=200
# ----------------------------사진 구함 --------------------------------#



	answer, menu = get_menu(answer)
# ----------------------------메뉴 구함 --------------------------------#



	res = {
		'message': {
			'text': answer
			}
		}
# ----------------------------메세지 설정 ------------------------------#



	if photo != '' and photo_width > 0 and photo_height > 0:
		res['message']['photo'] = {
			'url': photo,
			'width': photo_width,
			'height': photo_height
		}
# ----------------------------사진 설정 --------------------------------#



	menu_button = get_menu_button(menu)

	if menu_button != None:
		res['keyboard'] = menu_button

	return jsonify(res)
# --------------------------메뉴 버튼 설정 ------------------------------#

# ----------------------------------------------------
# 메인 함수
# ----------------------------------------------------
if __name__ == '__main__':
    
	app.run(host='0.0.0.0', port=5000, threaded=True)