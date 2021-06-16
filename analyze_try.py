import os,json,time,shutil,secrets
from stem.process import launch_tor_with_config
import requests
from bs4 import BeautifulSoup
#from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from stem.util import term


def print_lines(line):
    if "Bootstraped" in line:
        print(term.format(line, term.Color.BLUE))

class Analyser:
    # https://api.myip.com/
    def __init__(self,url,exit_node):
 	    # self.display = Display(visible=0, size=(1920,1080))
    	# self.display.start()
        # this.profile = FirefoxProfile()
        # self.url = url
        self.url = url
        self.path = os.path.abspath("har_export_trigger-0.6.1-an+fx.xpi")
        self.port = '7000'
        # self.exitnode = 'E44364879BA8634C46127084B2AF573F9B4B82A0'
        self.exitnode = exit_node
        self.tor_path = "/usr/bin/tor"
        self.tor_status_code = 0
        self.non_tor_status_code = 0
        self.non_tor_data = ""
        self.tor_data = ""
        self.max_k = 150
        # Min percentage error that can be omitted 
        self.min_k = 20 
        self.match_list = ["error","forbidden","tor","denied","sorry"]
        self.tor_page_source_sel = ""
        self.non_tor_page_source_sel = ""
        self.tor_driver = None
        self.non_tor_driver = None
        self.abs_path = ""
        self.gdpr_word_list = ["Souhlasím","Alle akzeptieren","Jag godkänner","Ich stimme zu","Ik ga akkoord","Egyetértek","J\'accepte","I agree","Accepta?i tot","Accept all","Accept"]
        self.tor_page_source_sel_after_gdpr_removal = ""
        self.non_tor_page_source_sel_after_gdpr_removal = ""
        self.tor_HAR = {}
        self.non_tor_HAR = {}
        self.count_t = 0
        self.count_n = 0
        self.soup_n = BeautifulSoup()
        self.soup_t = BeautifulSoup()
        self.non_store = {} 
        self.tor_store = {}


    def save_in_folder(self):
        self.abs_path = os.path.abspath("")+"/"+self.url.replace("/","_")
        try:
            os.mkdir(self.abs_path)
            print("Creating Folder...")
        except FileExistsError as e:
            print("Deleting the folder...")
            shutil.rmtree(self.abs_path)
            os.mkdir(self.abs_path)
            print("Creating Folder...")
        

    def setup_tor(self):
        
        # Assume socksport to be 7000 and exitnode as '4D2A4831BB67853A6FA01517A61B810D4480AE2F'
        tor = launch_tor_with_config(config = {'SocksPort': self.port,'ExitNodes': self.exitnode} ,tor_cmd=self.tor_path, take_ownership=True,timeout=120,init_msg_handler=print_lines)
        # try:
        self.tor_data = requests.get(self.url,proxies={'https': f'SOCKS5://127.0.0.1:{self.port}'})
        print("Status code (Tor):", self.tor_data.status_code)
        self.tor_status_code = self.tor_data.status_code

        profile = FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", '127.0.0.1')
        profile.set_preference("network.proxy.socks_port", int(self.port))
        profile.set_preference("network.proxy.socks_remote_dns", False)

        profile.add_extension(self.path)
        # profile.set_preference("extensions.torbutton.local_tor_check", False)
        # profile.set_preference("extensions.torbutton.use_nontor_proxy", True)
        profile.set_preference("dom.webdriver.enabled", False)

        #Enable the automation without having a new HAR file created for every loaded page.
        profile.set_preference("extensions.netmonitor.har.enableAutomation", True)
        # #Set to a token that is consequently passed into all HAR API calls to verify the user.
        profile.set_preference("extensions.netmonitor.har.contentAPIToken", "test")
        # #Set if you want to have the HAR object available without the developer toolbox being open.
        profile.set_preference("extensions.netmonitor.har.autoConnect", True)

        profile.set_preference("devtools.netmonitor.enabled",True)
        profile.set_preference("devtools.toolbox.selectedTool", "netmonitor")
        profile.set_preference("devtools.netmonitor.har.compress", False)
        profile.set_preference(
            "devtools.netmonitor.har.includeResponseBodies", False
        )
        profile.set_preference("devtools.netmonitor.har.jsonp", False)
        profile.set_preference("devtools.netmonitor.har.jsonpCallback", False)
        profile.set_preference("devtools.netmonitor.har.forceExport", False)
        profile.set_preference(
            "devtools.netmonitor.har.enableAutoExportToFile", False
        )
        profile.set_preference("devtools.netmonitor.har.pageLoadedTimeout", "2500")

        profile.update_preferences()

        options_ = FirefoxOptions()
        options_.ensure_clean_session = True

        options_.add_argument("--devtools")

        self.tor_driver = webdriver.Firefox(firefox_profile=profile,options=options_)

        self.tor_driver.get(url)

        time.sleep(10)
        self.tor_driver.page_source

        f = open(self.abs_path+"/tor(before).html", "w")
        f.write(BeautifulSoup(self.tor_driver.page_source,"html.parser").prettify())
        f.close()
        self.tor_driver.save_screenshot(self.abs_path+"/Tor(before).png")

        self.tor_driver.execute_script(
            """ 
            arr = ["Souhlasím","Alle akzeptieren","Jag godkänner","Ich stimme zu","Ik ga akkoord","Godta alle","Egyetértek","J\'accepte","I agree","Accepta?i tot","Accept all","Accept"]
            for(var i=0;i<arr.length;i++)
            {
                if(document.documentElement.innerHTML.includes(arr[i]))
                {
                    s = (arr[i]);
                    path = "//*[contains(., '"+s+"')]";
                    console.log(path);
                    x = document.evaluate(path,document,null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null); 
                    for(var i=0;i<x.snapshotLength;i++) x.snapshotItem(i).click();
                }
            }
            """
        )

        time.sleep(30)
        
        try:
            har_dict = self.tor_driver.execute_async_script(
                """
                var callback = arguments[arguments.length - 1];
                HAR.triggerExport().then((harLog) => { callback(harLog) });
                """
            )
            js = json.dumps({"log": har_dict})
            print("Tor Dumps")
            dic = json.loads(js)
            
            f = open(self.abs_path+"/tor_exportHTTP.status", "w")

            # tor_HAR = {};c={}

            for i in range(len(dic['log']['entries'])):
                self.tor_HAR[dic['log']['entries'][i]['request']['url']] = dic['log']['entries'][i]['response']['status']
                if(dic['log']['entries'][i]['response']['status'] != 0):
                    self.tor_store[dic['log']['entries'][i]['request']['url']] = dic['log']['entries'][i]['response']['status']

            print(term.format("1st Har stats (TOR)",term.Color.YELLOW))   
            f.write(str(dic))
            # print(self.tor_HAR)
            print(next(iter(self.tor_store)), " ", self.tor_store[next(iter(self.tor_store))])
            f.close()

        except Exception as e:
            print(e)

        self.tor_page_source_sel = self.tor_driver.page_source
        self.soup_t = BeautifulSoup(self.tor_page_source_sel, 'html.parser')

        f = open(self.abs_path+"/tor(after).html", "w")
        f.write(self.soup_t.prettify())
        f.close()

        self.tor_driver.save_screenshot(self.abs_path+"/Tor(after).png")
        
        f = open(self.abs_path+"/tor.node", "w")
        for tag in self.soup_t.find_all(True):
            self.count_t += 1
            # print(i, " -- ", tag.name)  # Print the names of DOM nodes
            f.write("{}--->{}\n".format(self.count_t, tag.name))
        f.write("\nTotal Number of Tor Nodes: {}\n".format(self.count_t))
        f.close()            

        # except Exception as e:
        #     print(e)
        
        tor.terminate()
        self.tor_driver.quit()

    def setup_non_tor(self):
        self.non_tor_data = requests.get(self.url)
        print("Status code (Non-Tor):", self.non_tor_data.status_code)
        self.non_tor_status_code = self.non_tor_data.status_code

        profile = FirefoxProfile()
        options = FirefoxOptions()
        options.add_argument("--devtools")
        profile.add_extension(self.path)
        
        #Enable the automation without having a new HAR file created for every loaded page.
        profile.set_preference("extensions.netmonitor.har.enableAutomation", True)
        #Set to a token that is consequently passed into all HAR API calls to verify the user.
        profile.set_preference("extensions.netmonitor.har.contentAPIToken", "test")
        #Set if you want to have the HAR object available without the developer toolbox being open.
        profile.set_preference("extensions.netmonitor.har.autoConnect", True)

        profile.set_preference("devtools.netmonitor.enabled",True)
        profile.set_preference("devtools.toolbox.selectedTool", "netmonitor")
        profile.set_preference("devtools.netmonitor.har.compress", False)
        profile.set_preference(
            "devtools.netmonitor.har.includeResponseBodies", False
        )
        profile.set_preference("devtools.netmonitor.har.jsonp", False)
        profile.set_preference("devtools.netmonitor.har.jsonpCallback", False)
        profile.set_preference("devtools.netmonitor.har.forceExport", False)
        profile.set_preference(
            "devtools.netmonitor.har.enableAutoExportToFile", False
        )
        profile.set_preference("devtools.netmonitor.har.pageLoadedTimeout", "2500")
        
        self.non_tor_driver = webdriver.Firefox(firefox_profile=profile,options=options)
        # self.non_tor_driver.install_addon(self.path, temporary=True)
        self.non_tor_driver.get(self.url)
        time.sleep(1.5)
        # print(profile)
        
        # self.non_tor_driver.find_element_by_tag_name('html').send_keys(Keys.CONTROL+Keys.SHIFT+'E')

        self.non_tor_page_source_sel = self.non_tor_driver.page_source
        self.non_tor_driver.save_screenshot(self.abs_path+"/Non_Tor.png")

        self.non_tor_driver.execute_script(
            """ 
            arr = ["Souhlasím","Alle akzeptieren","Jag godkänner","Ich stimme zu","Ik ga akkoord","Godta alle","Egyetértek","J\'accepte","I agree","Accepta?i tot","Accept all","Accept"]
            for(var i=0;i<arr.length;i++)
            {
                if(document.documentElement.innerHTML.includes(arr[i]))
                {
                    s = (arr[i]);
                    path = "//*[contains(., '"+s+"')]";
                    console.log(path);
                    x = document.evaluate(path,document,null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null); 
                    for(var i=0;i<x.snapshotLength;i++) x.snapshotItem(i).click();
                }
            }
            """
        )


        time.sleep(30)
        self.non_tor_driver.save_screenshot(self.abs_path+"/Non_Tor(after).png")
        try:
            
            self.non_tor_driver.implicitly_wait(10)
            har_dict = self.non_tor_driver.execute_async_script(
                """
                var callback = arguments[arguments.length - 1];
                HAR.triggerExport().then((harLog) => { callback(harLog) });
                """
            )
            js = json.dumps({"log": har_dict})
            dic = json.loads(js)
            print("Non Tor Dumps")

            for i in range(len(dic['log']['entries'])):
                self.non_tor_HAR[dic['log']['entries'][i]['request']['url']] = dic['log']['entries'][i]['response']['status']
                if(dic['log']['entries'][i]['response']['status'] != 0):
                    self.non_store[dic['log']['entries'][i]['request']['url']] = dic['log']['entries'][i]['response']['status']

            print(term.format("1st Har stats (NON TOR)",term.Color.YELLOW))   

            f = open(self.abs_path+"/non-tor_exportHTTP.status", "w")
            f.write(str(dic))
            f.close()
            # print(tor_HAR)
            print(next(iter(self.non_store)), " ", self.non_store[next(iter(self.non_store))])

            self.soup_n = BeautifulSoup(self.non_tor_page_source_sel, 'html.parser')
            f = open(self.abs_path+"/non-tor.html", "w")
            f.write(self.soup_n.prettify())
            f.close()

            f = open(self.abs_path+"/non-tor.node", "w")
            for tag_ in self.soup_n.find_all(True):
                self.count_n += 1
                f.write("{}--->{}\n".format(self.count_n, tag_.name))
            f.write("\nTotal Number of Tor Nodes: {}\n".format(self.count_n))
            f.close()
            # dic_har = driver.execute_async_script("HAR;")
            # print(dic_har)
        except Exception as e:
            print(e)
        self.non_tor_driver.quit()

    def status_checker(self):
        # Check if request library on non-tor fails or not:
        status_url = next(iter(self.non_store))
        sc = self.non_store[str(status_url)]
        if self.non_tor_status_code > 399:
            # Use HAR instead , because sometimes without being blocked, CDNs seem to block request 
            if sc == self.non_tor_status_code or (int(sc) > 399 and self.non_tor_status_code > 399):
                # HAR and request library features same code(Hence website blocked)
                print(term.format("Website blocked on client side\n",term.Attr.BOLD))
            else:
                self.non_tor_status_code = sc

        # Check if request library on tor fails or not:
        status_url_t = next(iter(self.tor_store))
        sc_t = self.tor_store[str(status_url_t)]
        if self.tor_status_code > 399:
            if sc_t == self.tor_status_code or (int(sc_t)>299 and self.tor_status_code>399): #adding the reloading check for websites like (mastercard) where it routes to another page.
                print(term.format("Website blocked on tor side\n",term.Color.RED))
            elif int(sc) != 0:
                # Could later Check for captcha and warnings
                pass
            else:
                self.tor_status_code = sc_t

        if self.non_tor_status_code != self.tor_status_code:
            if self.tor_status_code > 399:
                # print("Error")
                print(term.format("ERROR!!\n",term.Color.RED))
            elif self.tor_status_code > 299:
                # Check for redirection of website
                # Requires selenium wire to see the full HAR structure
                print(term.format("Redirected to another site\n",term.Color.YELLOW))
        else:            
            print("Nodes by tor and non-tor:")
            print(self.count_t,"-----",self.count_n)
            try:
                dom_score = 100*((self.count_n-self.count_t)/self.count_t)
            except ZeroDivisionError as e:
                print("Zero Error, check tor Dom")
                
            print("Dom Score: ", dom_score)

            self.soup_t = str(self.soup_t).lower()
            self.soup_n = str(self.soup_n).lower()

            if(abs(dom_score) > 0):
                if( abs(dom_score) > self.max_k):   
                    #   Random value to check the performance. 
                    #   Might need some more experiments to come back with the correct value
                    #   or it hasn't been loaded fully (increase loading time)")
                    print(term.format("Tor most probably Errors!!\n",term.Color.RED))
                elif(abs(dom_score) < self.min_k):
                    #   Random value to check the performance. 
                    #   Might need some more experiments to come back with the correct value
                    #   checks for keywords to help in this case
                    #   Captcha Checker...
                    print(term.format("Resembles same",term.Color.BLUE))
                    # Assuming no captcha
                    tor = 0
                    # If captcha in html of tor:
                    if "captcha" in self.soup_t and "captcha" not in self.soup_n:
                        tor = 1
                        print(term.format("Captcha present: checklist",term.Color.RED))
                    # If captcha in both, tor_html and non_tor html, or not anywhere:
                    else:
                        s_ = str(status_url)
                        if s_ in self.tor_HAR.keys():
                            if "captcha" in s_:
                                tor = 1
                                print(term.format("Captcha in tor from HAR",term.Color.YELLOW))
                        if s_ in self.non_tor_HAR.keys():
                            if "captcha" in s_:
                                tor = 0
                                print("Captcha in Non-Tor too")
                    if tor == 0:
                        print(term.format("Same...",term.Color.BLUE))
                    else:
                        print("Captcha")
                else:
                    print(term.format("Doubtful case!!",term.Color.MAGENTA))
                    print("checking for keywords...")
                    #   checks for keywords to help in this case     
                    for _ in self.match_list:
                        if _ in self.soup_t and _ not in self.soup_n:
                            # print("Tor blocked : checklist")
                            print(term.format("Tor blocked : checklist!!",term.BgColor.RED))

                    if "captcha" in self.soup_t and "captcha" not in self.soup_n:
                        print(term.format("Captcha present : checklist!!",term.BgColor.YELLOW))
                    else:
                        print(term.format("Same!!",term.Color.CYAN))
            else:
                print(term.format("Same Resemblance!!",term.Color.CYAN))
    
        
        self.non_tor_driver.quit()
        self.tor_driver.quit() 

website_list = [
    # "https://mastercard.de",
    # "https://santander.de",
    # "https://tdbank.com",
    # "https://allmodern.com/",
    # "https://autozone.com/",
    # "https://baskinrobbins.com/",
    # "https://benjerry.com/",
    # "https://bestbuy.com/",
    # "https://breyers.com/",
    # "https://delta.com/",
    # "https://dunkindonuts.com/",
    # "https://hyatt.com/",
    # "https://immonet.de/",
    # "https://kohls.com/",
    # "https://lowes.com/",
    # "https://lufthansa.com/",
    # "https://lg.com/",
    # "https://samsung.com/",
    # "https://staples.com/",
    # "https://tacobell.com/",
    # "https://olx.com/",
    # "https://nvidia.com/",
    # "https://nasa.gov",
    # "https://www.netflix.com/",
    "https://google.com/search?q=tor",
    # "https://discord.com",
    # "https://yahoo.com/",
    # "https://google.com",
    # "https://dan.me.uk",
    # "https://lloydsbank.com",
    # "https://bitstamp.net",
    # "https://sc.com",
    # "https://rankexploits.com",
    # "https://dominos.com",
    # "https://palemoon.org",
    # "http://adsabs.harvard.edu",
    # "https://montypython.net",
    # "https://go4go.net"
    # 'https://google.com',
    # 'https://apple.com',
    # 'https://youtube.com',
    # 'https://support.google.com',
    'https://cloudflare.com',
    'https://play.google.com',
    'https://blogger.com',
    'https://microsoft.com',
    'https://mozilla.org',
    'https://docs.google.com',
    'https://wordpress.org',
    'https://maps.google.com',
    'https://linkedin.com',
    'https://youtu.be',
    'https://en.wikipedia.org',
    'https://accounts.google.com',
    'https://europa.eu',
    'https://adobe.com',
    'https://plus.google.com',
    'https://sites.google.com',
    'https://vimeo.com',
    'https://drive.google.com',
    'https://googleusercontent.com',
    'https://amazon.com',
    'https://bbc.co.uk',
    'https://bp.blogspot.com',
    'https://istockphoto.com',
    'https://github.com',
    'https://cnn.com',
    'https://uol.com.br',
    'https://pt.wikipedia.org',
    'https://facebook.com',
    'https://vk.com',
    'https://es.wikipedia.org',
    'https://opera.com',
    'https://bbc.com',
    'https://gstatic.com',
    'https://nytimes.com',
    'https://msn.com',
    'https://slideshare.net',
    'https://issuu.com',
    'https://google.com.br',
    'https://fr.wikipedia.org',
    'https://dailymotion.com',
    'https://google.co.jp',
    'https://hugedomains.com',
    'https://t.me',
    'https://google.es',
    'https://forbes.com',
    'https://jimdofree.com',
    'https://dropbox.com',
    'https://brandbucket.com',
    'https://feedburner.com',
    'https://creativecommons.org',
    'https://mail.google.com',
    'https://weebly.com',
    'https://wikimedia.org',
    'https://w3.org',
    'https://myspace.com',
    'https://reuters.com',
    'https://medium.com',
    'https://abril.com.br',
    'https://theguardian.com',
    'https://policies.google.com',
    'https://google.de',
    'https://developers.google.com',
    'https://live.com',
    'https://get.google.com',
    'https://whatsapp.com',
    'https://nih.gov',
    'https://news.google.com',
    'https://yahoo.com',
    'https://mail.ru',
    'https://globo.com',
    'https://imdb.com',
    'https://line.me',
    'https://paypal.com',
    'https://de.wikipedia.org',
    'https://latimes.com',
    'https://steampowered.com',
    'https://bit.ly',
    'https://who.int',
    'https://news.yahoo.com',
    'https://pinterest.com',
    'https://telegraph.co.uk',
    'https://wired.com',
    'https://un.org',
    'https://hatena.ne.jp',
    'https://apache.org',
    'https://thesun.co.uk',
    'https://google.co.uk',
    'https://translate.google.com',
    'https://android.com',
    'https://fandom.com',
    'https://google.it',
    'https://fb.com',
    'https://webmd.com',
    'https://aol.com',
    'https://picasaweb.google.com',
    'https://dailymail.co.uk',
    'https://nasa.gov',
    'https://telegram.me',
    'https://gov.uk',
    'https://independent.co.uk',
    'https://cdc.gov',
    'https://wikia.com',
    'https://terra.com.br',
    'https://cpanel.com',
    'https://twitter.com',
    'https://books.google.com',
    'https://aboutads.info',
    'https://time.com',
    'https://abcnews.go.com',
    'https://it.wikipedia.org',
    'https://washingtonpost.com',
    'https://draft.blogger.com',
    'https://rakuten.co.jp',
    'https://tools.google.com',
    'https://buydomains.com',
    'https://change.org',
    'https://booking.com',
    'https://google.fr',
    'https://files.wordpress.com',
    'https://mediafire.com',
    'https://elpais.com',
    'https://myaccount.google.com',
    'https://youronlinechoices.com',
    'https://ebay.com',
    'https://samsung.com',
    'https://networkadvertising.org',
    'https://gravatar.com',
    'https://marketingplatform.google.com',
    'https://plesk.com',
    'https://amazon.co.jp',
    'https://namecheap.com',
    'https://id.wikipedia.org',
    'https://dan.com',
    'https://cpanel.net',
    'https://goo.gl',
    'https://scribd.com',
    'https://archive.org',
    'https://usatoday.com',
    'https://huffingtonpost.com',
    'https://wsj.com',
    'https://huffpost.com',
    'https://cnet.com',
    'https://lefigaro.fr',
    'https://office.com',
    'https://ig.com.br',
    'https://google.pl',
    'https://wa.me',
    'https://businessinsider.com',
    'https://4shared.com',
    'https://bloomberg.com',
    'https://ok.ru',
    'https://amazon.de',
    'https://search.google.com',
    'https://amazon.co.uk',
    'https://photos.google.com',
    'https://aliexpress.com',
    'https://harvard.edu',
    'https://foxnews.com',
    'https://tinyurl.com',
    'https://google.ru',
    'https://twitch.tv',
    'https://academia.edu',
    'https://rambler.ru',
    'https://stanford.edu',
    'https://wikihow.com',
    'https://eventbrite.com',
    'https://disney.com',
    'https://surveymonkey.com',
    'https://welt.de',
    'https://newyorker.com',
    'https://pl.wikipedia.org',
    'https://wiley.com',
    'https://indiatimes.com',
    'https://nginx.com',
    'https://cbc.ca',
    'https://wikipedia.org',
    'https://deezer.com',
    'https://soundcloud.com',
    'https://alibaba.com',
    'https://mega.nz',
    'https://usnews.com',
    'https://enable-javascript.com',
    'https://spotify.com',
    'https://picasa.google.com',
    'https://lemonde.fr',
    'https://themeforest.net',
    'https://imageshack.com',
    'https://xbox.com',
    'https://icann.org',
    'https://netflix.com',
    'https://storage.googleapis.com',
    'https://ziddu.com',
    'https://sfgate.com',
    'https://imageshack.us',
    'https://sciencemag.org',
    'https://php.net',
    'https://loc.gov',
    'https://disqus.com',
    'https://news.com.au',
    'https://sedo.com',
    'https://repubblica.it',
    'https://ca.gov',
    'https://adssettings.google.com',
    'https://forms.gle',
    'https://sciencedaily.com',
    'https://sputniknews.com',
    'https://thetimes.co.uk',
    'https://trustpilot.com',
    'https://biglobe.ne.jp',
    'https://hollywoodreporter.com',
    'https://clickbank.net',
    'https://washington.edu',
    'https://mirror.co.uk',
    'https://theatlantic.com',
    'https://abc.net.au',
    'https://ign.com',
    'https://walmart.com',
    'https://gmail.com',
    'https://bandcamp.com',
    'https://m.wikipedia.org',
    'https://goodreads.com',
    'https://depositfiles.com',
    'https://wp.com',
    'https://stackoverflow.com',
    'https://oup.com',
    'https://amazon.es',
    'https://bund.de',
    'https://ietf.org',
    'https://hp.com',
    'https://secureserver.net',
    'https://mashable.com',
    'https://techcrunch.com',
    'https://buzzfeed.com',
    'https://britannica.com',
    'https://yahoo.co.jp',
    'https://nationalgeographic.com',
    'https://photobucket.com',
    'https://lycos.com',
    'https://qq.com',
    'https://spiegel.de',
    'https://npr.org',
    'https://kickstarter.com',
    'https://ikea.com',
    'https://columbia.edu',
    'https://google.nl',
    'https://ea.com',
    'https://cambridge.org',
    'https://my.yahoo.com',
    'https://allaboutcookies.org',
    'https://urbandictionary.com',
    'https://bloglovin.com',
    'https://ipv4.google.com',
    'https://umich.edu',
    'https://chicagotribune.com',
    'https://nikkei.com',
    'https://metro.co.uk',
    'https://cornell.edu',
    'https://gofundme.com',
    'https://ft.com',
    'https://alexa.com',
    'https://privacyshield.gov',
    'https://ggpht.com',
    'https://pixabay.com',
    'https://yandex.ru',
    'https://dw.com',
    'https://addtoany.com',
    'https://code.google.com',
    'https://ytimg.com',
    'https://quora.com',
    'https://gizmodo.com',
    'https://discord.com',
    'https://abc.es',
    'https://weibo.com',
    'https://nypost.com',
    'https://rottentomatoes.com',
    'https://shutterstock.com',
    'https://mozilla.com',
    'https://noaa.gov',
    'https://unesco.org',
    'https://nydailynews.com',
    'https://google.co.in',
    'https://rapidshare.com',
    'https://e-monsite.com',
    'https://sapo.pt',
    'https://nbcnews.com',
    'https://finance.yahoo.com',
    'https://elmundo.es',
    'https://mysql.com',
    'https://instagram.com',
    'https://ovh.co.uk',
    'https://ru.wikipedia.org',
    'https://over-blog.com',
    'https://researchgate.net',
    'https://google.com.tw',
    'https://list-manage.com',
    'https://ted.com',
    'https://asus.com',
    'https://playstation.com',
    'https://psychologytoday.com',
    'https://ovh.com',
    'https://groups.google.com',
    'https://instructables.com',
    'https://espn.com',
    'https://doubleclick.net',
    'https://naver.com',
    'https://google.co.id',
    'https://shopify.com',
    'https://huawei.com',
    'https://netvibes.com',
    'https://economist.com',
    'https://t.co',
    'https://mit.edu',
    'https://ovh.net',
    'https://tripadvisor.com',
    'https://sciencedirect.com',
    'https://newsweek.com',
    'https://engadget.com',
    'https://yadi.sk',
    'https://oracle.com',
    'https://ibm.com',
    'https://fda.gov',
    'https://bing.com',
    'https://smh.com.au',
    'https://hm.com',
    'https://addthis.com',
    'https://blackberry.com',
    'https://nginx.org',
    'https://guardian.co.uk',
    'https://berkeley.edu',
    'https://ria.ru',
    'https://gnu.org',
    'https://afternic.com',
    'https://cbsnews.com',
    'https://akamaihd.net',
    'https://whitehouse.gov',
    'https://wix.com',
    'https://google.ca',
    'https://yelp.com',
    'https://box.com',
    'https://amazon.fr',
    'https://detik.com',
    'https://discord.gg',
    'https://rt.com',
    'https://ja.wikipedia.org',
    'https://nature.com',
    'https://cnbc.com',
    'https://godaddy.com',
    'https://sendspace.com',
    'https://theverge.com',
    'https://about.com',
    'https://express.co.uk',
    'https://variety.com',
    'https://digg.com',
    'https://zendesk.com',
    'https://bitly.com',
    'https://googleblog.com',
    'https://pbs.org',
    'https://arxiv.org',
    'https://livejournal.com',
    'https://khanacademy.org',
    'https://sina.com.cn',
    'https://parallels.com',
    'https://hbr.org',
    'https://corriere.it',
    'https://axs.com',
    'https://airbnb.com',
    'https://princeton.edu',
    'https://billboard.com',
    'https://psu.edu',
    'https://thoughtco.com',
    'https://fortune.com',
    'https://orange.fr',
    'https://fb.me',
    'https://skype.com',
    'https://scientificamerican.com',
    'https://vkontakte.ru',
    'https://utexas.edu',
    'https://pcmag.com',
    'https://cmu.edu',
    'https://groups.yahoo.com',
    'https://so-net.ne.jp',
    'https://iso.org',
    'https://merriam-webster.com',
    'https://wn.com',
    'https://techradar.com',
    'https://imgur.com',
    'https://google.com.au',
    'https://nvidia.com',
    'https://orkut.com.br',
    'https://prestashop.com',
    'https://dot.tk',
    'https://si.edu',
    'https://ubuntu.com',
    'https://20minutos.es',
    'https://thefreedictionary.com',
    'https://cia.gov',
    'https://thenextweb.com',
    'https://politico.com',
    'https://dreniq.com',
    'https://rediff.com',
    'https://espn.go.com',
    'https://answers.yahoo.com',
    'https://pexels.com',
    'https://soratemplates.com',
    'https://oreilly.com',
    'https://cointernet.com.co',
    'https://answers.com',
    'https://tabelog.com',
    'https://zdnet.com',
    'https://debian.org',
    'https://feedproxy.google.com',
    'https://evernote.com',
    'https://teamviewer.com',
    'https://statista.com',
    'https://xing.com',
    'https://nicovideo.jp',
    'https://windows.net',
    'https://thedailybeast.com',
    'https://archives.gov',
    'https://ap.org',
    'https://wiktionary.org',
    'https://dribbble.com',
    'https://iubenda.com',
    'https://mail.yahoo.com',
    'https://target.com',
    'https://biblegateway.com',
    'https://greenpeace.org',
    'https://oecd.org',
    'https://udemy.com',
    'https://ndtv.com',
    'https://vice.com',
    'https://searchenginejournal.com',
    'https://behance.net',
    'https://rollingstone.com',
    'https://house.gov',
    'https://inc.com',
    'https://dell.com',
    'https://weforum.org',
    'https://softpedia.com',
    'https://unicef.org',
    'https://channel4.com',
    'https://a8.net',
    'https://usgs.gov',
    'https://amazon.it',
    'https://thehill.com',
    'https://last.fm',
    'https://ftc.gov',
    'https://amazon.ca',
    'https://salon.com',
    'https://insider.com',
    'https://kotaku.com',
    'https://thestar.com',
    'https://cbslocal.com',
    'https://slate.com',
    'https://ads.google.com',
    'https://foursquare.com',
    'https://fifa.com',
    'https://zeit.de',
    'https://undeveloped.com',
    'https://intel.com',
    'https://bp1.blogger.com',
    'https://worldbank.org',
    'https://upenn.edu',
    'https://dreamstime.com',
    'https://netlify.app',
    'https://xinhuanet.com',
    'https://wisc.edu',
    'https://ebay.co.uk',
    'https://doi.org',
    'https://allrecipes.com',
    'https://ox.ac.uk',
    'https://en.wordpress.com',
    'https://boston.com',
    'https://megaupload.com',
    'https://vox.com',
    'https://nba.com',
    'https://ameblo.jp',
    'https://canalblog.com',
    'https://marketwatch.com',
    'https://video.google.com',
    'https://canada.ca',
    'https://irs.gov',
    'https://asahi.com',
    'https://epa.gov',
    'https://businesswire.com',
    'https://elsevier.com',
    'https://sony.com',
    'https://springer.com',
    'https://prezi.com',
    'https://snapchat.com',
    'https://offset.com',
    'https://viglink.com',
    'https://yale.edu',
    'https://sakura.ne.jp',
    'https://storage.canalblog.com',
    'https://daum.net'
]

exit_relays = [
    "E44364879BA8634C46127084B2AF573F9B4B82A0",
    "0111BA9B604669E636FFD5B503F382A4B7AD6E80",
    "01181B31BE5860C7D66DA88F88AD522C06470FD9",
    "01729F10A81DDD8A92D770B2133082EB56C75E26",
    "01CB2E297A8F586DBBCF98F028A3D1A49B0AB7BA",
    "01CFCC2545234EEE523D33ED25EF1E79807A18A7",
    "01FDC8E92D3280847D856DA1F9BFC2B4CD2C2EE8",
    "02758CD398E3F842EF82478078AAAE0273770DB2",
    "027E75C92F1231AE5F7BD4E1536696FE3040C460",
    "0325B91D3C32D3A24C863D5DFBED00564FAD5C64",
    "038C30D2AD053147C91EFB1291527ED621D7D1B1",
    "530277866466A1425F43A73DBFCB5FC7410C9852",
    "B6320E44A230302C7BF9319E67597A9B87882241",
    "A9B28E4D4FB6A26B5B6D3EDED2655D836BBD4E57",
    "DE847D94E78B2E560AB87D272DC90192D3144F17",
    "9B47A5B7C108F22D1AFF544E70D22ED8997B96A3",
    "76959901386E8C908F50235D9894007886B67C2E",
    "939126EA4D25CB212A79746C133194F8A24C435B",
    "B65CC2B45CE9C934D1E1254736166D6AB64C2ABC",
    "06ABFC513FA71C7EE423DCC6ABF80F6B4A2FC1AC",
    "81B75D534F91BFB7C57AB67DA10BCEF622582AE8",
    "183C8C6727E2137AF278B3850AD5D9C2304B98C9",
    "ACF38D2A79A4AE47A6CCD8011EBB729BF66482AB",
    "D1F1F5AA5BCF5DAB44C444DEF82821B8BEC66148",
    "8C25BA134D579B8AAF420E01215EB2CF06AAE907",
    "B06F093A3D4DFAD3E923F4F28A74901BD4F74EB1",
    "E43244684E0C924EC082B8ECC735FAF2F8CF1C45",
    "0E5522CB4F79E36C0BB263BABC861CFC686929AE",
    "6BCB964AB74E23F8986BDA905697D3A6BE08AF28",
    "578E007E5E4535FBFEF7758D8587B07B4C8C5D06",
    "4A3B874F0187F2CF0DA3C8F76063B070F9F7A14F",
    "255CF8CC68137449DEBD443797AB3D851E3065B2",
    "2ED4D25766973713EB8C56A290BF07E06B85BF12",
    "76AB50C3EC0472A63AFB9A833A535FA6BD691478",
    "65E6EB676633328ADE3BD3168A59134CDDD21E19",
    "229D865D7AC084D30E5F5016CE5A8C21740F74F4",
    "DD8BD7307017407FCC36F8D04A688F74A0774C02",
    "F01E382DA524A57F2BFB3C4FF270A23D5CD3311D",
    "F6A358DD367B3282D6EF5824C9D45E1A19C7E815",
    "1228111A6D4AFC619ED3A70079A3A0B678476A43",
    "E51620B90DCB310138ED89EDEDD0A5C361AAE24E",
    "88AE3BC088396F1D3FCC4F2F588C0DC837599D20",
    "81EDFBC8F6F5C7CF0ADD5F8E08BC8FABA04089C6",
    "6CE3DDFAA9E56F56890235CC9C2385B2DD93E146",
    "50825758CC2DA41DEEF6AE29CB20A803BDCC6F79",
    "1DC6E52ADB9FE4346CEFC05C6916D8B8F7F66D1C",
    "EFAE44728264982224445E96214C15F9075DEE1D",
    "975DF2CA6288228044A9162FF0D38B3EE15298CD",
    "47A3D00525F041F382B398BF95BC58E0EC23276B",
    "E41B16F7DDF52EBB1DB4268AB2FE340B37AD8904",
    "A14F90953AE9462CF3A862C4CA95F73BF94A6F8B",
    "6A642CAF73BDBEC64DD9A44B9B973C70B3E74707",
    "348439F4A3D959E6D1481070DA81A135343419CB",
    "EC1997D51892E4607C68E800549A1E7E4694005A",
    "DB5FF6E8806A6674E27BF69D1E1EBF308D9A87A9",
    "6781471814DF164C2A6F17CD1F2584923FDE2101",
    "424BF86927E80D916589BB12248BD468BB470684",
    "CDE4C5DC9D639E915B99B461EE243044FCA264B6",
    "3BB47BFF2788B534A5BACA37879C48EEBE5E8800",
    "84640625221A4E96309AFE0810B38646BC60F458",
    "742C45F2D9004AADE0077E528A4418A6A81BC2BA",
    "E006EA04C696BBD6E35407538131305FF3CB8C16",
    "C5A6FEE5BC3BE19F5B9EB086CA95DAD393D8A4F6",
    "4488EEA8CA1674020D9FCC2A176E1FDB9606F0B3",
    "C59E079437340E3AD14E6785C0A91A5B6F328566",
    "74FB777F25E7F80BA6BF8B808DF873A1708821A7",
    "A2F580F93FA3D0DA373769614BD9B0C8A6C4623E",
    "6E94866ED8CA098BACDFD36D4E8E2B459B8A734E",
    "7BE9E2EF2BB41BB662D9A3CD68289B9E3DBF8A08",
    "E379A6CACEFAFE1B8EA68503BFCFF1215BF1EE7F",
    "2AB0B91CCF12664D5D95083A6A7B871918C8CF9C",
    "3DE567C1350C0E858C6147AECB06EA9B3EAF3261",
    "0ED4CA8A8E6CE2D28D6D23B20815AE3982646FCB",
    "97AEE1EEFBCBB6FF8FA482029830E8E10A961883",
    "BE0AC3B6692085308CA766F9E03736D1CAAED6F3",
    "D8B99A7556B3A546910F505F374F55D2417EEE12",
    "2B76A914CAF3B121D14EF8A28327CAEE127994A4",
    "E321D0118DAD44BBC74A5C26FE7CFDBAAF3DA077",
    "B2D07EABB8F071FF29947B7886281DF1E255BADA",
    "5C4B505FCFCE0E340A86D0E7960B24A13ED5677C",
    "58B44B5591A96EC08114B041CC6B1BB1521DF2BE",
    "0FF233C8D78A17B8DB7C8257D2E05CD5AA7C6B88",
    "F4594608272C82407E9D137F1AE89A408CCFD285",
    "6372CADE2B9A608E5114002A7A825AF0D11B449A",
    "456F6E4998EB17B975DB5A19273607868E5F8AFA",
    "AD1359B9D74D526FEF3F58AF41105C623A3A8C18",
    "1B605B2751279B152CA098ED76B1EBCC9ADCA239",
    "C74469EC04787CC458FB1DCDF456C5092CF08B19",
    "7F7BE7926AF718D6A3DED24D694D94C1D5FACF28",
    "C8F6F6C1834454F1E927A4A05E8E54EB623D4B73",
    "470BC5C6A8BD1D9FDBB55689FB3030310181EAE2",
    "AF022F351A4B6F2514A09F9245F9FF5ACA729735",
    "902E21BC05A7B1EC8CE85D78C47C3D8EAD5EFE6F",
    "F8AEA2825629E4383599FD2A4BD5740CD1322CBC",
    "4C07CB3365CF3E06A56FD2DC8ECA4E97A6521983",
    "0A4ED4C74020740A904F3A9936030B7A4C6170BB",
    "05F5BB75DA007361CE03770393033D4D52836D8A",
    "50A0CFB654D39F420F52D362B1DF50A12B33D5A0",
    "B36006D88E2CCEF2E1EF0826C7F1B0EDC8DE6C06",
    "FDBF608F9A2ECD0C600CAF96398A7D5B08D46CA9",
    "8F16229D5425774DCA566D7737596178153DB838",
    "BC38744FD82618B37EE6A5A61BBCCE8788D55E3D",
    "5B9BB7A543C2C035A423A6B411780E50645782C0",
    "FB8796036069BB4787D639F92681ECC2FD7AEB22",
    "9664A7EFB405F555F3C0079FA7618B2EE6CE6D2A",
    "520C85ABE6E731CECC28B1055854053FAA28061B",
    "644DECC5A1879C0FE23DE927DD7049F58BBDF349",
    "4AD0B40B0FC679CC300F398BCEBE9D000833F62C",
    "E8562C7CFBEB6501F2E02DA00203F958E8B1685C",
    "BFC4734342209C8D172AACC283750116F74359C6",
    "9446EE28342A8B4502B4DA24DA18851BC9E516E0",
    "2785C4A65FE9ADC5C75E79F0B034ECDE3700F820",
    "EB6A879331A20D3D39874960E1076A8421F5A44C",
    "7E77CC94D94C08609D70B517FF938CC61C9F8232",
    "5D84900DBE6D6365684A9675B81A68ACE9577A68",
    "6B263B45B33B8E2C73AB80F9B0D73538B44BD75D",
    "A87D19DD1A89327B8DB878DC2793426752799B5C",
    "4B2E97CA3BAC3A2B14879F109E9965A0C20316C2",
    "B7A115C65ED1AA30C15E11A19A68EB5AAE7ED0C4",
    "A6AAFAEABBBACC74CEB15BE9CE69F3B3A4087841",
    "A9860C42EF532379E846087802646B5D4BCB17BE",
    "D762D707FC56ED169D74C7844516B46213E19DE2",
    "6A50621E0976044854C0DF372558757A5FBEDAEE",
    "287E1041DFC3A03E1650A61ADF580EA1C6BF3649"
    ]

i=0

for url in website_list:
    i+=1
    exit_node = secrets.choice(exit_relays)
    print(url," : ",exit_node)
    we = Analyser(url,exit_node)
    we.save_in_folder()
    we.setup_tor()
    we.setup_non_tor()
    we.status_checker()
    time.sleep(5)
    print()
    if(i==1):
        break