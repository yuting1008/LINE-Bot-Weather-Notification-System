import requests 
import datetime
import json

place = {}
place["01"] = "基隆市"	
place["12"] = "嘉義市"
place["02"] = "台北市"	
place["13"] = "嘉義縣"
place["03"] = "新北市"	
place["14"] = "台南市"
place["04"] = "桃園縣"
place["15"] = "高雄市"
place["05"] = "新竹市"	
place["16"] = "屏東縣"
place["06"] = "新竹縣"	
place["17"] = "台東縣"
place["07"] = "苗栗縣"	
place["18"] = "花蓮縣"
place["08"] = "台中市"	
place["19"] = "宜蘭縣"
place["09"] = "彰化縣"	
place["20"] = "澎湖縣"
place["10"] = "南投縣"	
place["21"] = "金門縣"
place["11"] = "雲林縣"	
place["22"] = "連江縣"

# 了解一下現在幾點,+8是因為那是美國時間
time = datetime.datetime.now()
hr = (time.hour + 8)

citynum = input("請輸入縣市代碼：")
location = place[citynum]

url_weather = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001'
url_light = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0005-001'

params = {
    'Authorization':'CWB-C018319F-7863-4F10-B08C-909EA6B23EA5',
    'locationName':location,

}

p = {
    'Authorization':'CWB-C018319F-7863-4F10-B08C-909EA6B23EA5'
}

re = requests.get(url_weather, params = params)
info_w = json.loads(re.text)

req = requests.get(url_light, params = p)
info_l = json.loads(req.text)

condition = info_w["records"]["location"][0]["weatherElement"]
# t1為每天早上6.到晚上6.狀況 t2為晚上6.到隔天
t1 = condition[0]["time"][1]["endTime"]
t2 = condition[0]["time"][2]["endTime"]

# describe為對天氣的描述
describe1 = condition[0]["time"][1]["parameter"]["parameterName"]
describe2 = condition[0]["time"][2]["parameter"]["parameterName"]

# rain為降雨機率
rain1 = condition[1]["time"][1]["parameter"]["parameterName"]
rain2 = condition[1]["time"][2]["parameter"]["parameterName"]

# maxT and minT為高低溫
maxT1 = condition[4]["time"][1]["parameter"]["parameterName"]
maxT2 = condition[4]["time"][2]["parameter"]["parameterName"]
minT1 = condition[2]["time"][1]["parameter"]["parameterName"]
minT2 = condition[2]["time"][2]["parameter"]["parameterName"]


obs = info_l["records"]["weatherElement"]["location"]
loc_code = {}
loc_code["新北市"] = [466850, 466880, 466900]
loc_code["臺北市"] = [466910, 466920, 466930]
loc_code["基隆市"] = [466940, 466950]
loc_code["花蓮縣"] = [466990]
loc_code["桃園市"] = [467050]
loc_code["宜蘭縣"] = [467060, 467080]
loc_code["金門縣"] = [467110]
loc_code["彰化縣"] = [467270]
loc_code["澎湖縣"] = [467300, 467350]
loc_code["臺南市"] = [467410, 467420]
loc_code["高雄市"] = [467440, 467441]
loc_code["嘉義市"] = [467480]
loc_code["臺中市"] = [467490]
loc_code["嘉義縣"] = [467530]
loc_code["臺東縣"] = [467540, 467610, 467620, 467660]
loc_code["南投縣"] = [467550]
loc_code["新竹縣"] = [467571]
loc_code["屏東縣"] = [467590]
loc_code["連江縣"] = [467990]


value = []
for city in obs :
  if int(city["locationCode"]) in loc_code[location] :
    value.append(city["value"])

total = 0
if value == [] :
  avg_light = "no info"
else :
  for i in value :
    total += i

  avg_light = round((total / len(value)), 1)

# 根據現在時間決定輸出t1 or t2的資料
if hr >= 18 :
  output = [describe2, rain2, minT2, maxT2, avg_light]
else :
  output = [describe1, rain1, minT1, maxT1, avg_light]
print(output)



'''
def job(t) :
	print(output)
	
schedule.every().day.at("01:00").do(job,'')
'''
