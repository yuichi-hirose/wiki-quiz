from lib2to3.pgen2.token import BACKQUOTE
import wikipedia

import json
import asyncio
import requests
import re

import time
from wikipedia.exceptions import PageError, DisambiguationError
import random
import numpy as np

from concurrent.futures import ThreadPoolExecutor

URL="https://jp.wikipedia.org/w/api.php"
Max_links=800
links_dict={}
count = 0
# Backlinks_min_defo = 50
Backlinks_min_Sum = 0
Backlinks_min_Ave = 0 #Backlinks_min_defo


class TitleError(Exception):
    pass
class LinkError(Exception):
    pass

class DictError(Exception):
    pass

def check_link(l, title):
    global URL, Max_links, links_dict, b, Backlinks_min_Sum, Backlinks_min_Ave
    global count

    flag_dict = False
    flag_link = False

    print(f"link:{l}の検証を開始します")
    if(l=="曖昧さ回避"):
        return
    if(title in l):
        now_time = time.time()-b
        print(now_time)
        print(f"{l}は{title}を含みます")
        raise TitleError(f"{l}は{title}を含みます")
    blcontinue="0|0"
    backlinks=[]
    try:
        page_l=wikipedia.WikipediaPage(title=l)
    except PageError:
        now_time = time.time()-b
        print(now_time)
        print(f"{l}のpageは存在しません")
    except DisambiguationError:
        print(f"{l}のpageは曖昧さ回避のpageです")

    content_l=page_l.summary
    if(title in content_l):
        #print(f"{l}は相互リンクです")
        flag_dict = True
        flag_link = True
    #else:
        #now_time = time.time()-b
        #print(now_time)
        #print(f"{l}は相互リンクではありません")
        # raise LinkError("相互リンクが成り立ちません")

    while(True):
        params={
            "action": "query",
            "list":"backlinks",
            "bltitle": l,
            "format": "json",
            "bllimit":500,
            "blcontinue":blcontinue
        }
        r = requests.get(URL, params=params)
        j=r.json()
        #print(j)
        backlinks+=j['query']['backlinks']
        if(len(backlinks) >= 500):
            flag_dict = True

        if(len(backlinks) >= Max_links):
            flag_dict = False
            break
        elif("continue" in j):
            blcontinue=j['continue']['blcontinue']
        else:
            break

    if (l not in links_dict) and flag_dict:
        count += 1
        # Backlinks_min_Sum += len(backlinks)
        # Backlinks_min_Ave = min(Backlinks_min_Sum / (count + 1), 100)
        print(f"{l}のリンク数は{len(backlinks)}です")
        print("linked: ", count)
        # print("border: ", Backlinks_min_Ave)
        # if(len(backlinks) > Backlinks_min_Ave or len(backlinks) < 10):
        links_dict[l]=len(backlinks)
        if flag_link:
            print(f"{l}は相互リンクのため、辞書に加えます")
        else:
            print(f"{l}は相互リンクではありませんが、関連性を見出し辞書に加えます")
    else:
        print(f"{l}は関連対象外です")

    #for bl in backlinks:
    #  print(bl['title'])
    now_time = time.time()-b
    print(now_time)
    print("-----------------------------------------------------------")

def check_link_thread(l, title):
    if(len(links_dict)>=7):
        return
    try:
        check_link(l, title)
    except DictError as e:
        pass
        #print("catch DictError:", e)
    except TitleError as e:
        pass
        #print("catch TitleError:", e)
    except LinkError as e:
        pass
        #print("catch LinkError:", e)
    except PageError as e:
        pass
        #print("catch PageError:", e)
    except DisambiguationError as e:
        pass
        #print("catch DisambiguationError:", e)
    except:
        print("Unknown Error")


def generate_quiz(title):
    global links_dict

    async def f(l,title):
        res = await loop.run_in_executor(None, check_link_thread, l, title)
        return None#res.json()
    loop = asyncio.get_event_loop()

    # 言語を日本語に設定
    wikipedia.set_lang("jp")
    #random.seed(0)
    page=wikipedia.WikipediaPage(title=title)
    # ページの上から順にリンクを取ってくる
    html_content = page.html()
    links = re.findall('<a href="/wiki/.*?" title="(.*?)">', html_content)
    # シンプルにリンクを引っ張ってくる
    #links=page.links
    #random.shuffle(links)

    tasks = [f(l,title) for l in links]
    ret = loop.run_until_complete(asyncio.gather(*tasks))

    sorted_dict=sorted(links_dict.items(),key=lambda x:x[1],reverse=True)
    hints=np.array(sorted_dict)[:,0]

    shuffle_hints = []
    while(True):
        if len(shuffle_hints) >= 5 or len(shuffle_hints) >= len(hints):
            break
        add_int = random.randint(0,len(hints)-1)
        if hints[add_int] not in shuffle_hints:
            shuffle_hints.append(hints[add_int])
    print("All int list:", hints)
    print("hint list:", shuffle_hints)
    return title,list(hints[:5])

if __name__ == "__main__":
    title = input(">> ")
    b=time.time()
    generate_quiz(title)