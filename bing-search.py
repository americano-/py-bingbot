#!/usr/bin/env python
from selenium import webdriver
from time import sleep
import urllib2
import random
import sys
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
else:
    driver = webdriver.Firefox()

driver.get("http://www.outlook.com")
elem = driver.find_element_by_name("login")
elem.send_keys(username)
_pass = driver. find_element_by_name("passwd")
_pass.send_keys(password)
_pass.submit()
assert "Outlook" in driver.title
print "logged in as: " + username

# start searching
url = 'http://www.iheartquotes.com/api/v1/random'
for i in range(30):
    print username, "(", i, ")"
    query = urllib2.urlopen(url).read()
    driver.get("http://www.bing.com/search?q=" + query)
    sleep(random.randint(1,2))
driver.close()

