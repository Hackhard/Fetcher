from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import pickle
import pathlib
import os


def open_non_tor(url, webs, path):
    cook = {}
    ### OPEN USING TOR CONFIG ###
    print("Opening Non-Tor...")
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    # profile.set_preference("security.cert_pinning.enforcement_level", 0)
    # profile.set_preference("network.stricttransportsecurity.preloadlist", False)

    browser = webdriver.Firefox(profile)
    browser.get(url)
    print()

    time.sleep(20)
    all_text = browser.page_source

    # BS4 prettify
    soup = BeautifulSoup(all_text, 'html.parser')

    # HTML file create
    txe = path+"/non_tor_["+webs.replace("/", "")+"].html"
    f = open(txe, "w")
    f.write(soup.prettify())

    print("Html files for Non-Tor Created")
    print()  # BLANK LINE

    print("Length   ", len(all_text))  # Length
    dom_nodes = path+"/non_tor_["+webs.replace("/", "")+"]_DOM_nodes.txt"

    # Number of nodes
    f = open(dom_nodes, "w")
    f.write("All Nodes (Non-Tor): \n")
    i = 0
    for tag in soup.find_all(True):
        i += 1
        # print(i, " -- ", tag.name)  # Print the names of DOM nodes
        f.write("{}--->{}\n".format(i, tag.name))

    f.write("Total Number of Non-Tor Nodes: {}\n".format(i))
    print("Number of Non-Tor Nodes : ", i)

    res = []

    DOM_nodes_non_tor = i
    length_html_non_tor = len(all_text)

    res.append(length_html_non_tor)
    res.append(DOM_nodes_non_tor)

    print()
    # print("Cookies: ")
    cook = (browser.get_cookies())
    # pickle.dump( cook , open("cookies.pkl","wb"))
    # print(cook)

    # script(browser,url)
    ss_non_tor(browser, webs, path)
    close(browser)
    res.append(cook)

    print()
    print("RES (No-TOR): \n", res[0], "\n", res[1])
    return res


def open_tor(url, webs, cook, path):

    ### OPEN USING TOR CONFIG ###
    print("Opening Tor...")
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
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
    # print(cook)

    time.sleep(20)
    all_text = browser.page_source

    # BS4 prettify
    soup = BeautifulSoup(all_text, 'html.parser')

    # HTML file for Tor
    txe = path+"/tor_["+webs.replace("/", "")+"].html"
    f = open(txe, "w")
    f.write(soup.prettify())

    print("Html files for Tor Created")
    print()  # BLANK LINE

    print("Length   ", len(all_text))  # Length

    dom_nodes = path+"/tor_["+webs.replace("/", "")+"]_DOM_nodes.txt"

    # Number of nodes
    f = open(dom_nodes, "w")
    f.write("All Nodes (Tor): \n")
    i = 0
    for tag in soup.find_all(True):
        i += 1
        # print(i, " -- ", tag.name)  # Print the names of DOM nodes
        f.write("{}--->{}\n".format(i, tag.name))

    f.write("Total Number of Tor Nodes: {}\n".format(i))
    print()
    print("Number of Tor Nodes : ", i)

    res = []
    DOM_nodes_tor = i
    length_html_tor = len(all_text)

    res.append(length_html_tor)
    res.append(DOM_nodes_tor)

    print()
    # print("Cookies: ")
    # print(browser.get_cookies())

    # script(browser,url)
    ss_tor(browser, webs, path)
    close(browser)

    print()
    print("RES (TOR): \n", res[0], "\n", res[1])
    return res


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


protocol = "http://"
web_list = [
    #--------Error websites----#
    "dan.me.uk",
    "lloydsbank.com/",
    "bitstamp.net/",
    "sc.com/",
    "rankexploits.com/",
    "dominos.com/",
    "palemoon.org/",
    "adsabs.harvard.edu",
    "montypython.net/",
    "go4go.net/go/",
    #--------------------------#
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
    print("Website being tested: ", web)
    pth = (pathlib.Path().absolute())
    path = os.path.join(pth, web.replace("/", "").replace(".", "_"))
    print("PATH: ", path)
    os.mkdir(path)
    print("Directory created")
    url = protocol + web
    # print(url," ",web)

    tor_list = []
    no_tor_list = []
    no_tor_list = open_non_tor(url, web, path)
    print()
    tor_list = open_tor(url, web, no_tor_list[2], path)
    print()
    print("Scores of length(HTML): ", 100 *
          (no_tor_list[0]-tor_list[0])/tor_list[0], " %")
    print("Scores of DOM_nodes : ", 100 *
          (no_tor_list[1]-tor_list[1])/tor_list[1], " %")
    time.sleep(10)
    print()
