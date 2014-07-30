from selenium import webdriver
import sys, time, urllib2, json, random, threading

class Bing:

    def __init__(self, is_mobile=False):
        global url, creds
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
        random.seed(time.localtime().tm_yday)
        random.shuffle(creds)
    
    def _tearDown(self):
        self.driver.close()

    def _login(self, username, password):
        driver = self.driver
        driver.get("https://ssl.bing.com/fd/auth/signin?action=interactive&provider=windows_live_id&return_url=http%3a%2f%2fwww.bing.com%2f")
        driver.find_element_by_id("i0116").clear()
        driver.find_element_by_id("i0116").send_keys(username)
        driver.find_element_by_id("i0118").clear()
        driver.find_element_by_id("i0118").send_keys(password)
        driver.find_element_by_id("idSIButton9").click()
        time.sleep(2.0)
        assert "Bing" in driver.title

    def _search(self, username, password, freq):
        driver = self.driver
        self._login(username, password)
        for i in range(freq):
            driver.find_element_by_id("sb_form_q").clear()
            driver.find_element_by_id("sb_form_q").send_keys(self._newWord())
            driver.find_element_by_id("sb_form_go").click()
            time.sleep(random.randint(1,15))
        driver.get(self.base_url + "/rewards/dashboard")
        print username, "has", self._get_credits(freq), "credits."
        driver.find_element_by_id("id_n").click()
        driver.find_element_by_css_selector(".lnk").click()

    def _search_mobile(self, username, password, freq):
        driver = self.driver
        # mobile has its own login mechanism
        driver.get(self.base_url + "/rewards/signin")
        driver.find_element_by_css_selector("span.idText").click()
        driver.find_element_by_id("i0116").clear()
        driver.find_element_by_id("i0116").send_keys(username)
        driver.find_element_by_id("i0118").clear()
        driver.find_element_by_id("i0118").send_keys(password)
        driver.find_element_by_id("i0011").click()
        time.sleep(2.0)
        driver.switch_to_alert().accept()
        time.sleep(5.0)
        assert "Rewards" in driver.title
        driver.get(self.base_url)
        for i in range(freq):
            driver.find_element_by_id("sb_form_q").click()
            driver.find_element_by_id("sb_form_q").clear()
            driver.find_element_by_id("sb_form_q").send_keys(self._newWord())
            driver.find_element_by_id("sbBtn").click()
            time.sleep(1.0)
        driver.get(self.base_url + "/rewards/dashboard")
        driver.find_element_by_link_text("Sign out").click()
        time.sleep(5.0)

    def _get_credits(self, f):
        self.driver.get(self.base_url + "/rewards/dashboard")
        credits = self.driver.find_element_by_css_selector(".credits").text
        self.driver.implicitly_wait(1)
        try: progress_desktop = self.driver.find_element_by_id("srch1x0610").find_element_by_css_selector(".progress").text
        except: pass
        try: progress_desktop = self.driver.find_element_by_id("srch1x0611").find_element_by_css_selector(".progress").text
        except: pass
        try: progress_desktop = self.driver.find_element_by_id("srch1x0612").find_element_by_css_selector(".progress").text
        except: pass
        self.driver.implicitly_wait(60)
        progress_mobile = self.driver.find_element_by_id("mobsrch01").find_element_by_css_selector(".progress").text
        return credits, progress_desktop, progress_mobile

    def _check_credits(self, username, password, freq):
        self._login(username, password)
        c, d, m = self._get_credits(freq)
        print username, c, ",", d, ",",  m,
        if "of" in d or "of" in m:
            print "***"
        else: # finish the ,
            print 
        self.driver.find_element_by_id("id_n").click()
        self.driver.find_element_by_css_selector(".lnk").click()
        time.sleep(2.0)

    def _newWord(self):
        url = 'http://api.wordnik.com:80/v4/words.json/randomWord?hasDictionaryDef=false&minCorpusCount=0&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5'
        res = json.load(urllib2.urlopen(url))
        return res['word']

    def test_bing(self):
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
        global creds
        count = 1
        for u,p,f in creds:
            print count, "of", len(creds),
            self._check_credits(u, p, f)
            count += 1

# end of Bing class

# GLOBALS
url = "http://www.bing.com"
FREQ_M = 20        # of searches for mobile

## helper functions
# Pass in a config file
# in csv style: 
# user@hotmail.com, password, number of searches
def getCreds(filename):
    creds = []
    with open(filename, "r") as f:
        for line in f:  
            if not '#' in line:
                u, p, f = line.rstrip().split(",")
                creds.append( (u.strip(' '), p.strip(' '), int(f)) )
    return creds

if __name__ == "__main__":
    # define a thread
    def bing(is_mobile=False):
        bing = Bing(is_mobile)
        bing.test_bing()

    # YOU NEED TO WRITE YOUR OWN config file
    #   in csv style. E.g.:
    #   user1@hotmail.com, password, number of searches 
    #   user2@hotmail.com, password, number of searches
    creds = getCreds(filename="config")

    # CHECK THIS TO 0 if you want to perform a credit check    
    checkonly = 0
    threading = 0

    if checkonly or 'balance' in sys.argv[1]:

        # check available credits, 
        # progress of the day for desktop search, 
        # progress of the day for mobile search
        b = Bing(is_mobile=False)
        b.check_credits()

    else:
        if threading:
            # search for points
            td = threading.Thread(name='Bing Desktop', target=bing, args=(False,))
            tm = threading.Thread(name='Bing Mobile', target=bing, args=(True,))
            td.start()
            tm.start()

        else:
            bing(False)
            bing(True)
