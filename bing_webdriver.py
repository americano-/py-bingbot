from selenium import webdriver
import time, urllib2, json, random
import threading

url = "http://www.bing.com"
freq_m = 20
freq = 30
double_points = 90

class Bing:
    def __init__(self, is_mobile=False):
        # mobile profile
        self.fp = webdriver.FirefoxProfile()
        #self.fp.set_preference("general.useragent.override", 'User Agent String :: mozilla/5.0 (iphone; cpu iphone os 7_0_2 like mac os x) applewebkit/537.51.1 (khtml, like gecko) version/7.0 mobile/11a501 safari/9537.53')
        self.fp.set_preference("general.useragent.override", "User Agent String :: Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30")
        self._is_mobile = is_mobile
        self._setUp(self._is_mobile)

    def _setUp(self, is_mobile=False):
        print "_setUp mobile?", is_mobile
        global url
        if is_mobile:
            self.driver = webdriver.Firefox(firefox_profile=self.fp)

        else:
            print "webdriver.Firefox()"
            self.driver = webdriver.Firefox()
            print "webdriver.Firefox() done"
        self.driver.implicitly_wait(60)
        self.base_url = url
    
    def get_credits(self):
        return self.driver.find_element_by_css_selector(".credits").text

    def test_bing(self):
        global creds, freq_m
        random.seed(87)
        random.shuffle(creds)
        count = 1
        for u, p, f in creds:
            print "This User (", count, "/", len(creds), ") = ", u,
            if self._is_mobile:
                print "Mobile"
                self.search_mobile(u, p, freq_m)
            else:
                print "Desktop"
                self.search(u, p, f)
            time.sleep(5.0)
            count += 1
        self._tearDown()

    def login(self, username, password):
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("id_s").click()
        driver.find_element_by_css_selector("span.id_link_text").click()
        driver.find_element_by_id("i0116").clear()
        driver.find_element_by_id("i0116").send_keys(username)
        driver.find_element_by_id("i0118").clear()
        driver.find_element_by_id("i0118").send_keys(password)
        driver.find_element_by_id("idSIButton9").click()
        assert "Rewards" in driver.title

    def check_credits(self, username, password):
        driver = self.driver
        self.login(username, password)
        self.get_credits()

    def search(self, username, password, freq):
        driver = self.driver
        self.login(username, password)
        for i in range(freq):
            driver.find_element_by_id("sb_form_q").clear()
            driver.find_element_by_id("sb_form_q").send_keys(self.newWord())
            driver.find_element_by_id("sb_form_go").click()
            time.sleep(1.0)
        driver.get(self.base_url + "/rewards/dashboard")
        print username, "has", self.get_credits(), "credits."
        driver.find_element_by_id("id_n").click()
        driver.find_element_by_css_selector(".lnk").click()

    def search_mobile(self, username, password, freq):
        driver = self.driver
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
            driver.find_element_by_id("sb_form_q").send_keys(self.newWord())
            driver.find_element_by_id("sbBtn").click()
            time.sleep(1.0)
        driver.get(self.base_url + "/rewards/dashboard")
        driver.find_element_by_link_text("Sign out").click()
        time.sleep(5.0)

    def _tearDown(self):
        print "_tearDown"
        self.driver.close()

    def newWord(self):
        url = 'http://api.wordnik.com:80/v4/words.json/randomWord?hasDictionaryDef=false&minCorpusCount=0&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5'
        res = json.load(urllib2.urlopen(url))
        return res['word']

if __name__ == "__main__":
    def bing(is_mobile=False):
        b = Bing(is_mobile)
        b.test_bing()
    creds = []
    with open("config", "r") as f:
        for line in f:
            u, p, f = line.rstrip().split(",")
            creds.append((u.strip(' '),p.strip(' '),int(f)))
    print creds
    td = threading.Thread(name='Bing Desktop', target=bing, args=(False,))
    tm = threading.Thread(name='Bing Mobile', target=bing, args=(True,))
    td.start()
    tm.start()
