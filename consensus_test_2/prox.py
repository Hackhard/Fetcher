import requests, re, time
from stem.process import launch_tor_with_config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

import os 
# form typing import Optional

tor_path = "/usr/bin/tor"


class Proxy:
    def __init__(self,url):
        self.proxy_url = "https://spys.me/proxy.txt"
        self.url = url
        self.proxy_host = []
        self.proxy_port = []
        self.proxy_country = []
        self.proxy_google_pass = []
        self.proxy_anon = []
        self.incoming_ip_different_from_outgoing_ip = []
        self.proxy_ssl = []
        self.proxies_matching_loc = []
        print("----------------------------")
        print(self.url)
        print("----------------------------")

    def get_proxy_details(self):
        """
        Get the informations regarding the proxies from https://spys.me/proxy.txt.
        """

        page = requests.get(self.proxy_url)

        proxy_list = page.text.split("\n")

        # Remove first 9 lines and last 2 lines to get just the details of the proxies
        proxy_list = proxy_list[9:-2]

        # Format: IP address:Port CountryCode-Anonymity(Noa/Anm/Hia)-SSL_support(S)-Google_passed(+)

        for line in proxy_list:

            proxy_host = line[:line.index(":")]
            proxy_port = line[line.index(":")+1:line.index(" ")]
            proxy_country = line[line.index(" ")+1:line.index(" ")+3]
            proxy_ssl = (re.findall("[-][S]",line))
            proxy_google_pass = (re.findall("[ ][+]",line))

            proxy_anon = line[line.index(proxy_country)+3:line.index(proxy_country)+4]

            if len(proxy_ssl)==0:
                proxy_ssl = False
            else:
                proxy_ssl = True

            if len(proxy_google_pass)==0:
                proxy_google_pass = False
            else:
                proxy_google_pass = True
            
            if "!" in line:
                incoming_ip_different_from_outgoing_ip = True
            else:
                incoming_ip_different_from_outgoing_ip = False

            self.proxy_host.append(proxy_host)
            self.proxy_port.append(proxy_port)
            self.proxy_country.append(proxy_country)
            self.proxy_google_pass.append(proxy_google_pass)
            self.proxy_anon.append(proxy_anon)
            self.incoming_ip_different_from_outgoing_ip.append(incoming_ip_different_from_outgoing_ip)
            self.proxy_ssl.append(proxy_ssl)

            # print(f"Host: {proxy_host}; port: {proxy_port}; country: {proxy_country}; Google Pass: {proxy_google_pass}; SSL: {proxy_ssl}; Anonymity: {proxy_anon}; Route: {incoming_ip_different_from_outgoing_ip}")

    def no_proxy(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        
        try:
            driver.get(self.url)

            time.sleep(10)
            file_url = (self.url).replace("/","_").replace(":","_").replace(".","_")
            driver.save_screenshot(f"{file_url}_No_proxy.png")
            all_text = driver.page_source
            soup = BeautifulSoup(all_text, 'html.parser')

            c=0
            for i in soup.find_all(True):
                c+=1
            print("Normal")
            print(c)
            driver.quit()

        except Exception as e:
            print(e)
            driver.quit()

    def choose_proxy(self,proxy,k,google_passer):
        options = Options()
        options.headless = True
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": proxy,
            "ftpProxy": proxy,
            "sslProxy": proxy
        }

        driver = webdriver.Firefox(capabilities=firefox_capabilities,options=options)
        
        print(f"Proxy-{k}, pass: {google_passer}")
        try:
            driver.get(self.url)

            time.sleep(10)
            file_url = (self.url).replace("/","_").replace(":","_").replace(".","_")
            driver.save_screenshot(f"{file_url}_proxy{k}.png")
            all_text = driver.page_source
            soup = BeautifulSoup(all_text, 'html.parser')

            c=0
            for i in soup.find_all(True):
                c+=1
            print(f"Executed Proxy{k}.png")
            print(c)
            driver.quit()
            

        except Exception as e:
            print(e)
            driver.quit()


    def proxy_location_filter(self,location):
        k=0
        for i in range(0,len(self.proxy_country)):
            if self.proxy_country[i] == location and self.proxy_ssl[i] == True:
                k+=1
                self.proxies_matching_loc.append(self.proxy_host[i]+":"+self.proxy_port[i])
                self.choose_proxy(self.proxy_host[i]+":"+self.proxy_port[i],k,self.proxy_google_pass[i])
                # if k==7:
                #     break
                

    def tor_initialize(self):
        tor = launch_tor_with_config(config = {'SocksPort': '7000', 'ExitNodes': 'E8562C7CFBEB6501F2E02DA00203F958E8B1685C'}, tor_cmd=tor_path, take_ownership=True,timeout=120)
        try:
            data = requests.get('https://ipinfo.io/country', 
                proxies={'https': 'SOCKS5://127.0.0.1:7000'})
            # print("After Tor:", data.text)
            s = data.text
            print(s)

            options = Options()
            options.headless = True

            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = True
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.socks', '127.0.0.1')
            profile.set_preference('network.proxy.socks_port', 7000)

            browser = webdriver.Firefox(profile,options=options)
            
            browser.get(self.url)
            time.sleep(10)
            file_url = (self.url).replace("/","_").replace(":","_").replace(".","_")
            browser.save_screenshot(f"{file_url}_Tor.png")

            all_text = browser.page_source
            soup = BeautifulSoup(all_text, 'html.parser')

            c=0
            for i in soup.find_all(True):
                c+=1
            print("Tor")
            print(c)
            browser.quit()
        except Exception as e:
            print(e)
            browser.quit()
        
        self.proxy_location_filter(s.strip())
        tor.terminate()
    


url_arr = ["https://www.google.com/search?q=tor","https://cloudflare.com"]

for i in url_arr:
    a = Proxy(i)
    a.no_proxy()
    a.get_proxy_details()
    a.tor_initialize()
    print(a.proxies_matching_loc)

