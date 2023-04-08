########測試中##########
# 載入LineBot所需要的套件
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import schedule
import openpyxl
#from apscheduler.schedulers.blocking import BlockingScheduler
#from collections.abc import MutableMapping

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('Gs3ViKUtJfshfDX8MGwyog2+oC9y9XSidDtziEJeYndON7C1RziCbBgU16BrUxoP+GfkSvrAusya0JNI8IijE42hIFrDcog19rEFSXeWF1XTPQCr3h9OIQT/kmKTvIkpVynRg4/M9kq/ZVwSbnCgOgdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('726a61fc3ef897983a264dab897709a4')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True) # 取得收到的訊息內容
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = text=event.message.text
    global action, notify
    if re.match('查詢天氣',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('請輸入您想查詢天氣的縣市，並請輸入完整縣市名稱，例如：台北市、雲林縣、嘉義市等。'))
        action = 'search'

    elif re.match('立即設定',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('請輸入您希望獲得每日天氣通知的縣市，並請輸入完整縣市名稱，例如：台北市、雲林縣、嘉義市等。'))
        action = 'setting'
        
    elif re.match('設定所在地',message):
        buttons_template_message = TemplateSendMessage(
        alt_text='天氣通知',
        template=ButtonsTemplate(
            title='每日通知設定',
            text='請問您要設定每日天氣通知嗎？',
            actions=[
                MessageAction(
                    label='立即設定',
                    text='立即設定'
                ),
                MessageAction(
                    label='取消',
                    text='取消' 
                )
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    elif re.match('取消',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('謝謝使用！若想進行更多設定或查詢，歡迎使用下方選單！'))

    elif re.match('市',message[-1]) or re.match('縣',message[-1]):
        global city_search, city_setting
        if re.match('search',action):
            city_search = text=event.message.text.replace('臺','台') #如果有臺的話換台

        if re.match('setting',action):
            city_setting = text=event.message.text.replace('臺','台') #如果有臺的話換台
        line_bot_api.reply_message(event.reply_token,TextSendMessage('請輸入完整區域名稱，例如：大安區、鼓山區等。'))
    
    elif re.match('區',message[-1]):
        global town_search, town_setting
        if re.match('search',action):
            town_search = text=event.message.text
            info(city_search, town_search)
            text = '目前天氣概況：\n實際溫度：{0}°C\n體感溫度：{1}°C\n天氣狀況：{2}'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text.format(temp_now, at_now, weather_now))) #連接爬蟲

        elif re.match('setting',action):
            notify = 'done'
            town_setting = text=event.message.text
            text = '感謝您的設定，我們將在每日早上8點傳送{0}{1}的天氣資訊給您！'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text.format(city_setting, town_setting)))

    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage('目前尚無法辨識您的訊息。'))

def info(city, town):
    global temp_now, temp_3hr, at_now, at_3hr, weather_now, weather_3hr, avg_light
    df = pd.read_excel("TID.xlsx")
    CID = df.loc[(df['縣市名稱'] == city) & (df['區鄉鎮名稱'] == town)].values[0][0]
    TID = df.loc[(df['縣市名稱'] == city) & (df['區鄉鎮名稱'] == town)].values[0][2]
    url = "https://www.cwb.gov.tw/Data/js/3hr/ChartData_3hr_T_" + str(CID) + ".js?"
    now = datetime.now()
    current_time = now.strftime("%Y%m%d%H-%M")[:-1]
    re = requests.get(url, data = {"T" : current_time})
    data = json.loads(re.text[re.text.find("TempArray_3hr") + len("TempArray_3hr") + 3: -1].replace("'", '"'))
    soup = BeautifulSoup(re.text, "html.parser")
    dic = data[str(TID)]
    #現在跟3hr後的溫度
    temp_now = dic["C"]["T"][0]
    temp_3hr = dic["C"]["T"][1]
    #體感溫度
    at_now = dic["C"]["AT"][0]
    at_3hr = dic["C"]["AT"][1]
    #天氣狀況
    weather_now = dic["Wx"]["C"][0][1]
    weather_3hr = dic["Wx"]["C"][1][1]
    #紫外線強度
    url_light = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0005-001'
    p = {'Authorization':'CWB-C018319F-7863-4F10-B08C-909EA6B23EA5'}
    req = requests.get(url_light, params = p)
    info_l = json.loads(req.text)

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
    for c in obs :
        if int(c["locationCode"]) in loc_code[city.replace('台','臺')] :
            value.append(c["value"])

    total = 0
    if value == []:
        avg_light = "no info"
    else:
        for i in value :
            total += i
        avg_light = str(round((total / len(value)), 1))

def notify():
    if re.match ('done', notify):
        info(city_setting, town_setting)
        text = '目前天氣概況：\n實際溫度：{0}°C\n體感溫度：{1}°C\n天氣狀況：{2}\n\n三小時後天氣概況：\n實際溫度：{3}°C\n體感溫度：{4}\n天氣狀況：{5}\n\n今日平均紫外線：{6}'
        line_bot_api.push_message('U4b278b3e7aab4e54b52f81e5379262ff',TextSendMessage(text.format(temp_now, at_now, weather_now, temp_3hr, at_3hr, weather_3hr, avg_light)))


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
#     sched = BlockingScheduler()
#     sched.add_job(func=notify, trigger='cron', month='*', day='*', hour='08', minute='00')
#     sched.start()
