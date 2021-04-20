from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import pickle
import pathlib
import os


# url = "check.torproject.org/"
# url = "dan.me.uk/"

def open_non_tor(url, webs, path):
    cook = {}
    ### OPEN USING TOR CONFIG ###
    print("Opening Non-Tor...")
    profile = webdriver.FirefoxProfile()
    # profile.set_preference("security.cert_pinning.enforcement_level", 0)
    # profile.set_preference("network.stricttransportsecurity.preloadlist", False)

    browser = webdriver.Firefox(profile)
    browser.get(url)

    print("---------------HTML(NON-TOR)-----------------")
    print()  # BLANK LINE
    time.sleep(20)
    all_text = browser.page_source
    soup = BeautifulSoup(all_text, 'html.parser')

    # BS4 prettify

    print("Length   ", len(all_text))  # Length
    print("All Nodes (Tor): ")
    # Number of nodes
    i = 0
    for tag in soup.find_all(True):
        i += 1
        print(i, " -- ", tag.name)  # Print the naemes of DOM Nodes
    print()
    print("Number of Non Tor Nodes : ", i)

    # print(soup.prettify()) # print and write to a file to vim-diff
    print()
    print("Cookies: ")
    cook = (browser.get_cookies())
    # pickle.dump( cook , open("cookies.pkl","wb"))
    print(cook)
    print()
    txe = path+"/non_tor_["+webs.replace("/", "")+"].txt"
    f = open(txe, "w")
    f.write(soup.prettify())

    # ss_tor(browser,webs)
    # script(browser,url)
    ss_non_tor(browser, webs, path)
    close(browser)
    return cook


def open_tor(url, webs, cook, path):

    ### OPEN USING TOR CONFIG ###
    print("Opening Tor...")
    print()
    profile = webdriver.FirefoxProfile()
    # profile.set_preference("security.cert_pinning.enforcement_level", 0)
    # profile.set_preference("network.stricttransportsecurity.preloadlist", False)

    # profile.set_preference("extensions.torbutton.local_tor_check", False)
    # profile.set_preference("extensions.torbutton.use_nontor_proxy", True)

    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9050)

    browser = webdriver.Firefox(profile)
    browser.get(url)
    # browser.add_cookie(cook)
    # cookies = pickle.load(open("cookies.pkl", "rb"))

    # Load Cookie from Non-Tor

    # for cookie in cook:
    #     browser.add_cookie(cookie)

    print(cook)
    print()
    print("---------------HTML(TOR)-----------------")
    print()  # BLANK LINE
    time.sleep(20)
    all_text = browser.page_source
    soup = BeautifulSoup(all_text, 'html.parser')

    # BS4 prettify

    print("Length   ", len(all_text))  # Length
    print("All Nodes (Non-Tor): ")

    # Number of nodes
    i = 0
    for tag in soup.find_all(True):
        i += 1
        print(i, " -- ", tag.name)  # Print the names of DOM nodes
    print()
    print("Number of Tor Nodes : ", i)

    # print(soup.prettify()) # print and write to a file to vim-diff
    print()
    print("Cookies: ")
    print(browser.get_cookies())
    print()

    txe = path+"/tor_["+webs.replace("/", "")+"].txt"
    f = open(txe, "w")
    f.write(soup.prettify())

    # ss_tor(browser,webs)
    # script(browser,url)
    ss_tor(browser, webs, path)
    close(browser)

    # print(browser.page_source)


def script(browser, url):
    # # USE JS TO GET HTTP STATUS
    js = '''
    var xhr = new XMLHttpRequest();
    xhr.open('GET', arguments[arguments.length-1], false);
    xhr.send(null);
    return xhr.status;
    '''
    print()  # BLANK LINE
    time.sleep(5)
    status_code = browser.execute_script(js, url)

    print("STATUS CODE NON-TOR ", status_code)
    print()
    # browser.save_screenshot("tor_"+url.replace("/","").replace(".","_")+".png")


def ss_tor(browser, web, url):
    # time.sleep(10)
    print("Screenshoting tor...")
    browser.save_screenshot(url+"/tor_["+web.replace("/", "")+"].png")


def ss_non_tor(browser, web, url):
    # time.sleep(10)
    print("Screenshoting non-tor...")
    browser.save_screenshot(url+"/non-tor_["+web.replace("/", "")+"].png")


def close(browser):
    browser.close()

# ###########################################

# ### OPEN USING NORMAL CONFIG ###
# profile = webdriver.FirefoxProfile()
# profile.set_preference("security.cert_pinning.enforcement_level", 0)
# profile.set_preference("network.stricttransportsecurity.preloadlist", False)

# # profile.set_preference("extensions.torbutton.local_tor_check", False)
# # profile.set_preference("extensions.torbutton.use_nontor_proxy", True)

# browser = webdriver.Firefox(profile)
# browser.get(url)

# print("---------------HTML(NON-TOR)-----------------")
# print()
# # print(browser.page_source)

# # USE JS TO GET HTTP STATUS
# js = '''
# var xhr = new XMLHttpRequest();
# xhr.open('GET', arguments[arguments.length-1], false);
# xhr.send(null);
# return xhr.status;
# '''
# print()  # BLANK LINE
# status_code = browser.execute_script(js, url)
# print("STATUS CODE NON-TOR ", status_code)
# print()

# # browser.save_screenshot("non-tor_"+web.replace("/","").replace(".","_")+".png")
# browser.save_screenshot("non-tor_["+web_list[0].replace("/", "")+"].png")
# browser.close()


protocol = "https://"
web_list = [
            "dan.me.uk",
            "www.lloydsbank.com/",
            "www.bitstamp.net/",
            "www.sc.com/",
            "rankexploits.com/",
            "www.dominos.com/",
            "www.palemoon.org/",
            "adsabs.harvard.edu/",
            "www.montypython.net/",
            "www.go4go.net/go/",
        #----------------------#    
            "google.com",
            "Youtube.com",
            # "Tmall.com",
            # "Baidu.com",
            # "Qq.com",
            # "Sohu.com",
            "Facebook.com",
            # "Taobao.com",
            # "360.cn",
            # "Jd.com",
            "Amazon.com",
            "Yahoo.com",
            "Wikipedia.org",
            # "Zoom.us",
            # "Weibo.com",
            # "Sina.com.cn",
            # "Xinhuanet.com",
            "Live.com",
            "Reddit.com",
            "Netflix.com",
            "Microsoft.com",
            "Office.com",
            # "Panda.tv",
            # "Zhanqi.tv",
            "Instagram.com",
            # "Alipay.com",
            # "Csdn.net",
            # "Vk.com",
            # "Google.com.hk",
            # "Myshopify.com",
            # "Okezone.com",
            # "Microsoftonline.com",
            "bing.com",
            # "Yahoo.co.jp",
            "Twitch.tv",
            # "Naver.com",
            "Ebay.com",
            # "Bongacams.com",
            "Adobe.com",
            "Twitter.com",
            # "Aliexpress.com",
            "Amazon.in",
            # "Huanqiu.com",
            "Stackoverflow.com",
            # "Tianya.cn",
            # "Yy.com",
            # "Amazon.co.jp",
            # "Aparat.com",
            # "Chaturbate.com",
            "Linkedin.com",
            "check.torproject.org"
]

for web in web_list:
    pth = (pathlib.Path().absolute())
    path = os.path.join(pth, web.replace("/", "").replace(".", "_"))
    print("PATH: ", path)
    os.mkdir(path)
    print("Directory created")
    url = protocol + web
    # print(url," ",web)
    cook = open_non_tor(url, web, path)
    print()
    open_tor(url, web, cook, path)
    print()
    time.sleep(10)
