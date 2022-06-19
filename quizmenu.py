import os
from linebot import (
    LineBotApi
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
     MessageAction,FollowEvent, MessageEvent, MessageAction, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize
)
from linebot.models.actions import PostbackAction

line_bot_api = LineBotApi(os.environ["YOUR_CHANNEL_ACCESS_TOKEN"])

def initMenu(line_bot_api):
    rich_menu_to_create = RichMenu(
        size = RichMenuSize(width=1200, height=405),
        selected = True,
        name = 'richmenu for randomchat',
        chat_bar_text = 'タップでクイズ',
        areas=[RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1200, height=405),
            action=MessageAction(text="クイズ"))]           
        )

    richMenuId = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    #path = '/Users/suguruiwasaki/Documents/line_wiki/image/quizswitch.png'
    with open("image/wikiQuizBot.png", 'rb') as f:
        line_bot_api.set_rich_menu_image(richMenuId, "image/png", f)

    # set the default rich menu
    line_bot_api.set_default_rich_menu(richMenuId)

