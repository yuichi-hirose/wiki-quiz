import wikipedia

import json
import asyncio
import requests

import time
from wikipedia.exceptions import PageError, DisambiguationError
import random
import requests
import numpy as np

from concurrent.futures import ThreadPoolExecutor

URL="https://jp.wikipedia.org/w/api.php"
Max_links=1000
links_dict={}
count = 0

class TitleError(Exception):
    pass
class LinkError(Exception):
    pass

class DictError(Exception):
    pass

def check_link(l, title):
    global URL, Max_links, links_dict, b
    global count

    print(f"link:{l}の検証を開始します")
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
        print(response_str)

    content_l=page_l.summary
    if(title in content_l):
        print(f"{l}は相互リンクです")
    else:
        now_time = time.time()-b
        print(now_time)
        print(f"{l}は相互リンクではありません")
        raise LinkError("相互リンクが成り立ちません")

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
        if(len(backlinks) >= Max_links):
            break
        elif("continue" in j):
            blcontinue=j['continue']['blcontinue']
        else:
            break
    print(f"{l}のリンク数は{len(backlinks)}です")
    count += 1
    print(count)
    if(len(backlinks)>100):
        links_dict[l]=len(backlinks)
    #for bl in backlinks:
    #  print(bl['title'])
    now_time = time.time()-b
    print(now_time)
    print("------------------------------")

def check_link_thread(l, title):
    if(len(links_dict)>=5):
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
    #title="豊臣秀吉"
    page=wikipedia.WikipediaPage(title=title)
    links=page.links
    random.shuffle(links)

    tasks = [f(l,title) for l in links]
    ret = loop.run_until_complete(asyncio.gather(*tasks))

    sorted_dict=sorted(links_dict.items(),key=lambda x:x[1],reverse=True)
    hints=np.array(sorted_dict)[:,0]
    print("hint list:", hints[:5])
    return title,list(hints[:5])

if __name__ == "__main__":
    title = input(">> ")
    b=time.time()
    generate_quiz(title)