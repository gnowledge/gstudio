#newparser
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from collections import deque
from bs4 import BeautifulSoup

url="http://doer.metastudio.org"
stack=["/explore/courses"]
visited=[]
options=Options()
options.add_argument("--headless")
browser = webdriver.Firefox(firefox_options=options)


while(len(stack)>0 and len(visited)<100000):
    str=stack.pop()
    visited.append(str)
    #print(str)
    print(url+str)
    print(len(visited))

    try:
    	browser.get(url+str)
    	html=browser.page_source
    except Exception as e:
    	logging.exception(e)
    	continue


    if html is not None:
    	soup=BeautifulSoup(html,'html.parser')
    else:
    	continue

    for link in soup.find_all('a'):
            target = link.get('href')
            print(target)
            try:
                if ((target not in visited) and (target not in stack) and type(target) == type("bat") and target[0] == '/'):
                    #print(target)
                    if (".gif" in target or ".jpg" in target or ".png" in target or "/accounts/login" in target):
                        continue
                    stack.append(target)
            except:
                pass




        