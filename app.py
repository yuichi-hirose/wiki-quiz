# インポートするライブラリ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
     MessageAction,FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import os
import quiz
import csv
import random
import pandas as pd
import math
import sqlite3
import time

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)


#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def quiz_to_user(event):
    userid=event.source.user_id
    
    con = sqlite3.connect('cache.db')
    cur = con.cursor()
    #df = pd.read_csv("cache.csv")
    #user_data=df[df['userid'] ==userid]

    user_sql=cur.execute(f"SELECT * FROM cache WHERE userid = '{userid}'")
    answering=False
    for u in user_sql:
        user_data=u  #tuple
        answering=True

    # answering=len(user_data)>0

    messages=[]

    if(event.message.text=="ステータス"):
        message=str(userid)+"\n"+str(answering)
        status_message=TextSendMessage(text=message)
        messages.append(status_message)
        all_data=cur.execute(f"SELECT * FROM cache")
        con.commit()
        message=""
        for d in all_data:
            message+=str(d)+"\n"
        
        list_message=TextSendMessage(text=message)
        messages.append(list_message)
    elif(answering): #judge
        
        ans=user_data[1]
        hints=user_data[2:]
        if(event.message.text==ans):
            message="正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
            #キャッシュを消去
            cur.execute(f"DELETE FROM cache WHERE userid='{userid}'")
            con.commit()
            #df=df.drop(user_idx)
            #df.to_csv('cache.csv', index=False)
        else:
            message="不正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
            next_idx=0

            for i,hint in enumerate(hints):
                if(hint is None):
                    pass
                else:
                    next_hint=hint
                    next_idx=i

                    message=f"次のヒントは\n{next_hint}"
                    hint_message=TextSendMessage(text=message)
                    messages.append(hint_message)
                    
                    cur.execute(f"UPDATE cache SET hint{next_idx+1}=NULL WHERE userid='{userid}'")
                    con.commit()
                    break
            else:  #all hints are nan
                message=f"答えは{ans}でした！"
                messages.append(TextSendMessage(text=message))
                cur.execute(f"DELETE FROM cache WHERE userid='{userid}'")
                con.commit()
    else:  #select question
        if(event.message.text=="クイズ"):
            message1="問題"
            messages.append(TextSendMessage(text=message1))
            #q,hints=quiz.generate_quiz("織田信長")
            with open("quiz_data.csv","r") as f:
                reader = csv.reader(f)
                list_reader=list(reader)[1:]
                idx=random.randint(0,len(list_reader)-1)
                question=list_reader[idx]
            
            message2="最初のヒントは\n"+question[1]
            messages.append(TextSendMessage(text=message2))

            cur.execute(f"INSERT INTO cache VALUES ('{userid}','{question[0]}','{question[2]}','{question[3]}','{question[4]}','{question[5]}')")
            con.commit()
        else:
            message=f"受け取った入力は「{event.message.text}」\n"
            message+="「クイズ」と入力してね！"
            messages.append(TextSendMessage(text=message))
    con.close()
    return messages

def quiz_to_group(event):
    messages=[]
    userid=event.source.user_id
    profile = line_bot_api.get_profile(event.source.user_id)
    username=profile.display_name
    groupid=event.source.group_id
    
    con = sqlite3.connect('cache.db')
    cur = con.cursor()
    #df = pd.read_csv("cache.csv")
    #user_data=df[df['userid'] ==userid]

    user_sql=cur.execute(f"SELECT * FROM session WHERE groupid = '{groupid}'")
    answering=False
    for u in user_sql:
        user_data=u  #tuple
        answering=True

    if(answering): #judge
        
        ans=user_data[1]
        hints=user_data[2:]
        if(event.message.text==ans):
            message=f"{username}さん正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
            #キャッシュを消去
            cur.execute(f"DELETE FROM session WHERE groupid='{groupid}'")
            con.commit()
            #df=df.drop(user_idx)
            #df.to_csv('cache.csv', index=False)
        else:
            message=f"{username}さん不正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
            next_idx=0

            for i,hint in enumerate(hints):
                if(hint is None):
                    pass
                else:
                    next_hint=hint
                    next_idx=i

                    message=f"次のヒントは\n{next_hint}"
                    hint_message=TextSendMessage(text=message)
                    messages.append(hint_message)
                    
                    cur.execute(f"UPDATE session SET hint{next_idx+1}=NULL WHERE grouprid='{groupid}'")
                    con.commit()
                    break
            else:  #all hints are nan
                message=f"答えは{ans}でした！"
                messages.append(TextSendMessage(text=message))
                cur.execute(f"DELETE FROM session WHERE groupid='{groupid}'")
                con.commit()
    else:  #select question
        if(event.message.text=="クイズ"):
            message1="問題"
            messages.append(TextSendMessage(text=message1))
            #q,hints=quiz.generate_quiz("織田信長")
            with open("quiz_data.csv","r") as f:
                reader = csv.reader(f)
                list_reader=list(reader)[1:]
                idx=random.randint(0,len(list_reader)-1)
                question=list_reader[idx]
            
            message2="最初のヒントは\n"+question[1]
            messages.append(TextSendMessage(text=message2))

            cur.execute(f"INSERT INTO session VALUES ('{groupid}','{question[0]}','{question[2]}','{question[3]}','{question[4]}','{question[5]}')")
            con.commit()
        else:
            #message=f"受け取った入力は「{event.message.text}」\n"
            #message+="「クイズ」と入力してね！"
            #messages.append(TextSendMessage(text=message))
            pass
    con.close()
    return messages


# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #b=time.time()
    #profile = line_bot_api.get_profile(event.source.user_id)
    #userid=profile.user_id
    message_type=event.source.type

    #userid=event.source.user_id
    
    if(message_type=="user"):
        messages=quiz_to_user(event)
    elif(message_type=="group"):
        messages=quiz_to_group(event)
    
    if(len(messages)==0):return 0
    #messages.append(TextSendMessage(text=str(time.time()-b)))
    line_bot_api.reply_message(
        event.reply_token,
        messages
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)