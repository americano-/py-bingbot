from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys, time, urllib2, json, random, threading

class Bing:

    def __init__(self, is_mobile=False):
        global url, creds, DEBUG, RANDOM_ORDER
        if DEBUG:
            print "__init__"
        # mobile profile
        self.fp = webdriver.FirefoxProfile()
        self.fp.set_preference("general.useragent.override", "User Agent String :: Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30")
        self._is_mobile = is_mobile
        if is_mobile:
            self.driver = webdriver.Firefox(firefox_profile=self.fp)
        else:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(60)
        self.base_url = url
        if RANDOM_ORDER:
            random.seed(time.localtime().tm_yday)
            random.shuffle(creds)
    
    def _tearDown(self):
        global DEBUG
        if DEBUG:
            print "_tearDown"
        self.driver.close()

    def _login(self, username, password):
        global DEBUG
        if DEBUG:
            print "_login"
        driver = self.driver
        driver.get("https://ssl.bing.com/fd/auth/signin?action=interactive&provider=windows_live_id&return_url=http%3a%2f%2fwww.bing.com%2f")
        driver.find_element_by_id("i0116").clear()
        driver.find_element_by_id("i0116").send_keys(username)
        driver.find_element_by_id("i0118").clear()
        driver.find_element_by_id("i0118").send_keys(password)
        driver.find_element_by_id("idSIButton9").click()
        time.sleep(2.0)

    def _search(self, username, password, freq):
        global DEBUG, SEARCH_SLEEP
        if DEBUG:
            print "_search"
        driver = self.driver
        self._login(username, password)
        assert driver.find_element_by_id("id_n").text != "", driver.find_element_by_id("id_n").text
        driver.get(self.base_url)
        for i in range(freq):
            driver.find_element_by_id("sb_form_q").clear()
            driver.find_element_by_id("sb_form_q").send_keys(self._newWord())
            driver.find_element_by_id("sb_form_go").click()
            if i == freq-1: # last one no need to sleep
                break;
            time.sleep(random.randint(SEARCH_SLEEP, SEARCH_SLEEP+5))

    def _search_mobile(self, username, password, freq):
        global DEBUG, SEARCH_SLEEP
        if DEBUG:
            print "_search_mobile"
        driver = self.driver
        # mobile has its own login mechanism
        driver.get(self.base_url + "/rewards/signin")
        driver.find_element_by_css_selector("span.idText").click()
        driver.find_element_by_id("i0116").clear()
        driver.find_element_by_id("i0116").send_keys(username)
        driver.find_element_by_id("i0118").clear()
        driver.find_element_by_id("i0118").send_keys(password)
        driver.find_element_by_id("idSIButton9").click()
        time.sleep(2.0)
        try: driver.switch_to_alert().accept()
        except: pass
        time.sleep(5.0)
        assert "Rewards" in driver.title
        driver.get(self.base_url)
        for i in range(freq):
            driver.find_element_by_id("sb_form_q").click()
            driver.find_element_by_id("sb_form_q").clear()
            driver.find_element_by_id("sb_form_q").send_keys(self._newWord())
            driver.find_element_by_id("sb_form_q").send_keys(Keys.RETURN)
            if i == freq-1: # last one no need to sleep
                break
            time.sleep(random.randint(SEARCH_SLEEP, SEARCH_SLEEP+5))

    def _get_credits(self, f):
        global DEBUG
        if DEBUG:
          	print "_get_credits"    
        self.driver.get(self.base_url + "/rewards/dashboard")
        self.driver.implicitly_wait(5)
        credits = self.driver.find_element_by_css_selector(".credits").text
        self.driver.implicitly_wait(1)
        temp_progress_list= [o.text for o in self.driver.find_elements_by_css_selector(".progress")]
        progress_desktop = ''
        for item in temp_progress_list:
            if '15 ' in item or '30 ' in item or '60 ' in item:
                progress_desktop = str(item)    
        self.driver.implicitly_wait(60)
        progress_mobile = self.driver.find_element_by_id("mobsrch01").find_element_by_css_selector(".progress").text
        return credits, progress_desktop, progress_mobile

    def _check_credits(self, username, password, freq):
        global DEBUG
        if DEBUG:   
            print "_check_credits"
        self._login(username, password)
        c, d, m = self._get_credits(freq)
        print username, c, ",", d, ",",  m,
        if "of" in d or "of" in m:
            print "***"
        else: # finish the ,
            print 

    def _newWord(self):
        global DEBUG, API_KEY, DO_NOT_CACHE_WORDS
        if DEBUG:
            print "_newWord:", 
        url = 'http://api.wordnik.com:80/v4/words.json/randomWord?hasDictionaryDef=false&minCorpusCount=0&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key=' + API_KEY
        res = json.load(urllib2.urlopen(url))
        if DEBUG:
            print res['word']
        if not DO_NOT_CACHE_WORDS:
            with open("cache", "a") as f:
                f.write(res["word"] + "\n")        
        return res['word']

    def test_bing(self):
        global DEBUG
        if DEBUG:
            print "test_bing"
        global creds, FREQ_M
        count = 1
        for u, p, f in creds:
            print u, "(", count, "/", len(creds), ") ",
            if self._is_mobile:
                print "Mobile"
                self._search_mobile(u, p, FREQ_M)
            else:
                print "Desktop"
                self._search(u, p, f)
            time.sleep(5.0)
            count += 1
        self._tearDown()

    def check_credits(self):
        global creds, DEBUG
        if DEBUG:
            print "check_credits"
        count = 1
        for u,p,f in creds:
            print count, "of", len(creds),
            self._check_credits(u, p, f)
            count += 1
            self._tearDown()

# end of Bing class

# GLOBALS
API_KEY = "9999999999999999999999999999999999999999999999999"
url = "http://www.bing.com"
FREQ_M = 22 # of searches for mobile
SEARCH_SLEEP = 0
DEBUG = 0
RANDOM_ORDER = 0 # random order for users in config file
DO_NOT_CACHE_WORDS = 0

## helper functions
# Pass in a config file
# in csv style: 
# user@hotmail.com, password, number of searches
def getCreds(filename):
    global DEBUG
    if DEBUG:
        print "getCreds"
    creds = []
    with open(filename, "r") as f:
        for line in f:  
            if not '#' in line:
                u, p, f = line.rstrip().split(",")
                creds.append( (u.strip(' '), p.strip(' '), int(f)) )
    if not len(creds):            
        print "Error: nothing read from", filename
    else:
        return creds

if __name__ == "__main__":

    # YOU NEED TO WRITE YOUR OWN config file
    #   in csv style. E.g.:
    #   user1@hotmail.com, password, number of searches 
    #   user2@hotmail.com, password, number of searches
    creds = getCreds(filename="config")
    if creds:
        # define a thread
        def bing(is_mobile=False):
            bing = Bing(is_mobile)
            bing.test_bing()

        # CHECK THIS TO 0 if you want to perform a credit check    
        checkonly = 0
        thread = 0

        if 'both' in sys.argv[1]:
        # both desktop and mobile search
            thread = 1
        elif 'mobile' in sys.argv[1]:
            count = 1
            for u,p,__not_used in creds:
                print "Mobile:", count, "of", len(creds), u, FREQ_M
                b = Bing(is_mobile=True)
                b._search_mobile(u, p, FREQ_M)
                b._tearDown()
                count += 1
        elif 'desktop' in sys.argv[1]:
            count = 1
            for u,p,f in creds:
                print "Desktop:", count, "of", len(creds), u, f
                b = Bing(is_mobile=False)
                b._search(u, p, f)
                b._tearDown()
                count += 1
        elif checkonly or 'balance' in sys.argv[1]:
            # check available credits, 
            # progress of the day for desktop search, 
            # progress of the day for mobile search
            count = 1
            for u,p,f in creds:
                b = Bing(is_mobile=False)
                print count, "of", len(creds),
                b._check_credits(u, p, f)
                b._tearDown()
                count += 1

        if thread:
            # search for points
            td = threading.Thread(name='Bing Desktop', target=bing, args=(False,))
            tm = threading.Thread(name='Bing Mobile', target=bing, args=(True,))
            td.start()
            tm.start()

