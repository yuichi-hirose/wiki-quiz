import wikipedia

import time
from wikipedia.exceptions import PageError, DisambiguationError
import random
import requests
import numpy as np

# 言語を日本語に設定

def generate_quiz(title):
    wikipedia.set_lang("jp")
    #random.seed(0)
    #title="豊臣秀吉"
    return "織田信長",["安土桃山時代", "前田利長", "滝川一益", "第一次木津川口の戦い","北畠氏"]
    b=time.time()
    page=wikipedia.WikipediaPage(title=title)
    max_links=1000
    links=page.links
    url="https://jp.wikipedia.org/w/api.php"
    links_dict={}
    random.shuffle(links)
    for l in links:
        print(f"link:{l}")
        if(title in l):
            print("pass")
            continue
        blcontinue="0|0"
        backlinks=[]
        try:
            page_l=wikipedia.WikipediaPage(title=l)
        except PageError:
            print("no page")
        except DisambiguationError:
            print("aimai")


        # links_l=page_l.links
        # if(title in links_l):
        #   print("link each other")
        # else: 
        #   print(time.time()-b) 
        #   print("not linked")
        #   continue
        
        # content_l=page_l.content
        # content_l=content_l[:int(len(content_l)/2)]
        # if(title in content_l):
        #   print("link each other")
        # else: 
        #   print(time.time()-b) 
        #   print("not linked")
        #   continue

        content_l=page_l.summary
        if(title in content_l):
            print("link each other")
        else: 
            print(time.time()-b) 
            print("not linked")
            continue

        while(True):
            params={
                "action": "query",
                "list":"backlinks",
                "bltitle": l,
                "format": "json",
                "bllimit":500,
                "blcontinue":blcontinue
            }
            r = requests.get(url, params=params)
            j=r.json()
            #print(j)
            backlinks+=j['query']['backlinks']
            if(len(backlinks)>=max_links):
                break
            elif("continue" in j):
                blcontinue=j['continue']['blcontinue']
            else:
                break

        print(len(backlinks))
        if(len(backlinks)>100):
            links_dict[l]=len(backlinks)
        #for bl in backlinks:
        #  print(bl['title'])
        print(time.time()-b)
        print("------------------------------")
        if(len(links_dict)>=5):break
    
    sorted_dict=sorted(links_dict.items(),key=lambda x:x[1],reverse=True)
    print(sorted_dict)
    hints=np.array(sorted_dict)[:,0]
    return title,list(hints[:5])

if __name__ == "__main__":
    title,hints=generate_quiz("織田信長")
    print(title,hints)