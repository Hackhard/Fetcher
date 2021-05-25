import os, pathlib
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time




def work(url):
    # Uncomment these if you need additional information for debugging
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    # The location of the Tor Browser bundle
    # Update this to match the location on your computer
    tbb_dir = "/home/hackhard/tor-browser_en-US/"

    # Disable Tor Launcher to prevent it connecting the Tor Browser to Tor directly
    os.environ['TOR_SKIP_LAUNCH'] = '1'  # 0 doesn't open torrc
    os.environ['TOR_TRANSPROXY'] = '1'  # To be asked

    # Set the Tor Browser binary and profile
    tb_binary = os.path.join(tbb_dir, 'Browser/firefox')
    tb_profile = os.path.join(
        tbb_dir, 'Browser/TorBrowser/Data/Browser/profile.default')
    binary = FirefoxBinary(os.path.join(tbb_dir, 'Browser/firefox'))
    profile = FirefoxProfile(tb_profile)

    # We need to disable HTTP Strict Transport Security (HSTS) in order to have
    #   seleniumwire between the browser and Tor. Otherwise, we will not be able
    #   to capture the requests and responses using seleniumwire.
    profile.set_preference("security.cert_pinning.enforcement_level", 0)
    profile.set_preference("network.stricttransportsecurity.preloadlist", False)
    profile.accept_untrusted_certs = True 

    # Tell Tor Button it is OK to use seleniumwire
    profile.set_preference("extensions.torbutton.local_tor_check", False)
    profile.set_preference("extensions.torbutton.use_nontor_proxy", True)

    # Required if you need JavaScript at all, otherwise JS stays disabled regardless
    #   of the Tor Browser's security slider value
    profile.set_preference("browser.startup.homepage_override.mstone", "68.8.0")

    # Configure seleniumwire to upstream traffic to Tor running on port 9050
    #   You might want to increase/decrease the timeout if you are trying
    #   to a load page that requires a lot of requests. It is in seconds.
    options = {
        'proxy': {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050',
            'connection_timeout': 10
        }
    }

    driver = webdriver.Firefox(firefox_profile=profile,
                            firefox_binary=binary,
                            seleniumwire_options = options)


    driver.get(url)
    time.sleep(5)

    #TOR
    tbb_map={}
    for request in driver.requests:
        if request.response:
            tbb_map[request.path]=request.response.status_code
            # print(
            #     request.path," ",
            #     request.response.status_code," ",
            #     request.response.headers['Content-Type']
            # )
            
    #Make Directory with the name of the url to consists separate screenshots and request lists for each url
    pt = str(pathlib.Path().absolute())
    path = os.path.join(pt, url.replace("/", "").replace(".", "_").replace("https:","").replace("http:",""))

    print(path)
    os.mkdir(path)

    # write the files with dic consisting of tor request.path and request.response.status_codes
    txe = path+"/tor_["+url.replace("/", "")+"].txt"
    f = open(txe, "w")
    f.write(str(tbb_map))
    f.close()

    driver.save_screenshot(path+"/tor_["+url.replace("/", "")+"].png")
    driver.quit()


    tb_binary = os.path.join(tbb_dir, 'Browser/firefox')
    tb_profile = os.path.join(
        tbb_dir, 'Browser/TorBrowser/Data/Browser/profile.default')
    binary = FirefoxBinary(os.path.join(tbb_dir, 'Browser/firefox'))
    profile = FirefoxProfile(tb_profile)

    # We need to disable HTTP Strict Transport Security (HSTS) in order to have
    #   seleniumwire between the browser and Tor. Otherwise, we will not be able
    #   to capture the requests and responses using seleniumwire.
    profile.set_preference("security.cert_pinning.enforcement_level", 0)
    profile.set_preference("network.stricttransportsecurity.preloadlist", False)

    # Tell Tor Button it is OK to use seleniumwire
    profile.set_preference("extensions.torbutton.local_tor_check", False)
    profile.set_preference("extensions.torbutton.use_nontor_proxy", True)

    # Required if you need JavaScript at all, otherwise JS stays disabled regardless
    #   of the Tor Browser's security slider value
    profile.set_preference("browser.startup.homepage_override.mstone", "68.8.0")
    profile.accept_untrusted_certs = True 



    driver=webdriver.Firefox(firefox_profile = profile,
                            firefox_binary = binary)

    driver.get(url)
    time.sleep(5)

    nbb_map={}
    for request in driver.requests:
        if request.response:
            nbb_map[request.path] = request.response.status_code
            # print(
            #     request.path," ",
            #     request.response.status_code," ",
            #     request.response.headers['Content-Type']
            # )
            

    # write the files with dic consisting of non-tor request.path and request.response.status_codes

    txe = path+"/non-tor_["+url.replace("/", "")+"].txt"
    f = open(txe, "w")
    f.write(str(nbb_map))
    f.close()

    # Dict to check if the same request.path from tbb and normal browser have the same request.response.status_code
    # uncommon_pair = {}
    # for key in tbb_map:
    #     if key in nbb_map and tbb_map[key]!=nbb_map[key]:
    #         uncommon_pair[key]=tbb_map[key]

    # if(len(uncommon_pair)>0):
    #     print("Not equal")
    # else:
    #     print("Equal")

    key_t = list(tbb_map.keys())[0]
    key_nt = list(nbb_map.keys())[0]

    #First key-value for tor and non tor
    print(key_t," ",tbb_map[key_t])
    print(key_nt," ",nbb_map[key_nt])

    if tbb_map[key_t] == nbb_map[key_nt]:
        print("No redirection, additional tests on consensus and DOM checks required")
    else:
        if(int(tbb_map[key_t])>399):
            print("Tor is Blocked!!")
        else:
            print("Needs Inspection (possibility of GDPR, redirection, captcha)")
    print()
    print("----------")
    driver.save_screenshot(path+"/non-tor_["+url.replace("/", "")+"].png")
    driver.quit()


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
    # # #--------------------------#
    "google.com",
    "youtube.com",
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
    "reddit.com",
    "www.yahoo.com",
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
    "check.torproject.org",
    # # --------------------------------
    # # ACCESS DENIED Websites
    "mastercard.de",
    "santander.de",
    "tdbank.com",
    "allmodern.com/",
    "autozone.com/",
    "baskinrobbins.com/",
    "benjerry.com/",
    "bestbuy.com/",
    "breyers.com/",
    "delta.com/",
    "dunkindonuts.com/",
    "hyatt.com/",
    "immonet.de/",
    "kohls.com/",
    "lowes.com/",
    "lufthansa.com/",
    "lg.com/",
    "samsung.com/",
    "staples.com/",
    "tacobell.com/",
    "olx.com/",
    "nvidia.com/",
    "nasa.gov",
    "www.netflix.com/",
    "google.com/search?q=tor",
    "discord.com"
]

# print(len(web_list))

for url in web_list:
    try: 
        print("http://"+str(url))
        work("http://"+str(url))
    except TimeoutException as t:
        print("Error: "+ str(t))

