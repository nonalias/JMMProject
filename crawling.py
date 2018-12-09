import urllib.request
import requests
from bs4 import BeautifulSoup
import json
import datetime
import re
import math
def get():
  url = 'https://place.map.daum.net/26345420'
  response = requests.get(url, headers={'content-type':'application/json'})
  raw = response.raw
  result = raw.read()
  return result

def GPSfind(posx, posy):
    dic1 = {}
    dic2 = {}
    dic3 = {}
    dic4 = {}
    for i in range(0,89):
        th = math.radians(i)
        posx_cos = 1879 * math.cos(th) + posx
        posy_sin = 1879 * math.sin(th) + posy
        print(int(posx_cos),int(posy_sin))
        dic1[int(posx_cos)] = int(posy_sin)
    for i in range(90,179):
        th = math.radians(i)
        posx_cos = 1879 * math.cos(th) + posx
        posy_sin = 1879 * math.sin(th) + posy
        print(int(posx_cos), int(posy_sin))
        dic2[int(posx_cos)] = int(posy_sin)
    for i in range(180,269):
        th = math.radians(i)
        posx_cos = 1879 * math.cos(th) + posx
        posy_sin = 1879 * math.sin(th) + posy
        print(int(posx_cos), int(posy_sin))
        dic3[int(posx_cos)] = int(posy_sin)
    for i in range(270,360):
        th = math.radians(i)
        posx_cos = 1879 * math.cos(th) + posx
        posy_sin = 1879 * math.sin(th) + posy
        print(int(posx_cos), int(posy_sin))
        dic4[int(posx_cos)] = int(posy_sin)
    print(dic1)
    print(dic2)
    print(dic3)
    print(dic4)



def userGPS():
    client_id = "fechS4lsKMLVwarW0I01"
    client_secret = "MxwdD119Rv"
    location = input("현재 위치를 말씀해 주세요 : ")
    encText = urllib.parse.quote(location)

    url = 'https://openapi.naver.com/v1/search/local?query='+encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        locinfo = response_body.decode('utf-8')
        json_data = json.loads(locinfo)
        item = json_data.get('items')
        posx = item[0].get('mapx')
        posy = item[0].get('mapy')
        print(location+"의 GPS 주소는 ("+posx+","+posy+")입니다.")
        return posx, posy
    else:
        print("Error Code:" + response)

def storeInfo(region_kind):
    client_id = "fechS4lsKMLVwarW0I01"
    client_secret = "MxwdD119Rv"
	
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

        for j in range(10):
            s_title = item[j].get('title')
            s_telephone = item[j].get('telephone')
            s_address = item[j].get('address')
            s_roadAddress = item[j].get('roadAddress')
            s_mapx = item[j].get('mapx')
            s_mapy = item[j].get('mapy')
            store_information = [s_title, s_telephone, s_address, s_roadAddress, s_mapy, s_mapx]
            return store_information
    else:
        return jsonify(response)

def find_info(mapping_url):
    search_url = 'https://place.map.daum.net/'+str(mapping_url)
    res = requests.get(search_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    section_sname = soup.findAll("h2", {"class" : "tit_location"})
    section_pnum = soup.findAll("span", {"class" : "txt_contact"})
    section_addr = soup.findAll("span", {"class" : "txt_address"})

    for name in section_sname:
        print(name)
    for pnum in section_pnum:
        print(pnum)
    for addr in section_addr:
        print(addr)

def search_info():
    loc=input("현재 위치를 말씀해 주세요 : ")
    location = input("음식 종류를 입력해 주세요 : ")
    location+=loc
    encText = urllib.parse.quote(location)
    search_url = 'https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&q=' + encText

    html = requests.get(search_url).text
    soup = BeautifulSoup(html,'html.parser')
    maps = soup.findAll('div',{'class':"wrap_place"})
    for b in maps:
        for link in b.findAll('a'):
            if 'href' in link.attrs:
                if 'place' in link.attrs['href']:
                    store_mapping = (link.attrs['href']).split('/')
                    print(store_mapping[0])
                    find_info(store_mapping[0])

def menuCraw():
    dt = datetime.datetime.now()
    today_week = dt.weekday()
    url = 'http://skhu.ac.kr/uni_zelkova/uni_zelkova_4_3_view.aspx?idx=350'
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    lunch_menu = soup.find_all("td", {"class" : "color606"})
    a = lunch_menu[today_week]
    b = str(a).split('<br/>')
    print(b)

def calGPS(sposx, sposy):
    userGPS()
    if(sposx > posx):
        print(dic1)
    else:
        print("hi")

def matgip():
    client_id = "fechS4lsKMLVwarW0I01"
    client_secret = "MxwdD119Rv"
    location = input("가게 이름 : ")
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

        print(item)
    else:
        print("Error Code:"+response)







	#'https://github.com/s-owl/skhufeeds/blob/master/skhufeeds/crawlers/crawlers/menu.py'