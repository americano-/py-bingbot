#!/usr/bin/env python
from selenium import webdriver
from time import sleep
import urllib2
import random
import sys
import json

username = sys.argv[1]
password = sys.argv[2]
try: 
    is_mobile = sys.argv[3]
except:
    is_mobile = ''

if "mobile" in is_mobile.lower():
    # profile
    fp = webdriver.FirefoxProfile()
    fp.set_preference("general.useragent.override", 'User Agent String :: mozilla/5.0 (iphone; cpu iphone os 7_0_2 like mac os x) applewebkit/537.51.1 (khtml, like gecko) version/7.0 mobile/11a501 safari/9537.53')
    driver = webdriver.Firefox(firefox_profile=fp)
    num_searches = 20
else:
    driver = webdriver.Firefox()
    num_searches = 30

driver.get("http://www.outlook.com")
elem = driver.find_element_by_name("login")
elem.send_keys(username)
_pass = driver. find_element_by_name("passwd")
_pass.send_keys(password)
_pass.submit()
assert "Outlook" in driver.title
print "logged in as: " + username

# start searching
url = 'http://api.wordnik.com:80/v4/words.json/randomWord?hasDictionaryDef=false&minCorpusCount=0&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5'

for i in range(num_searches):
    print username, "(", i, ")"
    res = json.load(urllib2.urlopen(url))
    driver.get("http://www.bing.com/search?q=" + res['word'])
    sleep(random.randint(2,5))
driver.close()

