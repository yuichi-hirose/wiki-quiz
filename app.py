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

# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    """
    status_msg = profile.status_message
    if status_msg != "None":
        # LINEに登録されているstatus_messageが空の場合は、"なし"という文字列を代わりの値とする
        status_msg = "なし"
    status_message = TemplateSendMessage(alt_text="Buttons template",
                                    template=ButtonsTemplate(
                                    thumbnail_image_url=profile.picture_url,
                                   title=profile.display_name,
                                   text=f"User Id: {profile.user_id[:5]}...\n"
                                        f"Status Message: {status_msg}",
                                   actions=[MessageAction(label="成功", text="次は何を実装しましょうか？")]))
    """
    userid=profile.user_id
    answering=False
    with open("cache.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            if(row[0]==userid):
                ans=row[1]
                hints=row[2:]
                answering=True
                break
    
    if(answering): #judge
        messages=[]
        if(event.message.text==ans):
            message="正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
        else:
            message="不正解！"
            judge_message=TextSendMessage(text=message)
            messages.append(judge_message)
            #next_hint=
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:  #select question
        message=""
        if(event.message.text=="クイズ"):
            message="問題: "
            #message="ちょっと待ってて！"
            #q,hints=quiz.generate_quiz("織田信長")
            path=os.getcwd()
            with open(f"{path}/quiz_data.csv","r") as f:
                reader = csv.reader(f)
                list_reader=list(reader)
                #idx=random.randint(0,len(list_reader))  #csvの1行目に見出しをつける場合変更が必要
                idx=0
                question=list_reader[idx]
            
            message+="ヒント1: "+question[1]
            """
            with open("cache.csv","a") as f:
                writer = csv.writer(f)
                to_write=[userid,question[0]]+question[2:]
                writer.writerow(to_write)
            """

        else:
            message="「クイズ」と入力してね！"
    
        quiz_message=TextSendMessage(text=message)
        line_bot_api.reply_message(
            event.reply_token,
            quiz_message
        )
    

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)