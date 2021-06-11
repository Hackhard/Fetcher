import os,json,time,shutil,secrets
from stem.process import launch_tor_with_config
import requests
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.keys import Keys
from stem.util import term

def print_boo_lines(line):
        if "Bootstrapped " in line:
            print(term.format(line, term.Color.BLUE))

class Analyser:
    # https://api.myip.com/
    def __init__(self,url,exit_node):
        self.display = Display(visible=0, size=(1920,1080))
        self.display.start()
        self.profile = FirefoxProfile()
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
        self.gdpr_word_list = ["Souhlasím","Alle akzeptieren","Jag godkänner","Ich stimme zu","Ik ga akkoord","Egyetértek","J\'accepte","I agree","Acceptați tot","Accept all","Accept"]

    def save_in_folder(self):
        print("Creating Folder...")
        self.abs_path = os.path.abspath("")+"/"+self.url.replace("/","_")
        try:
            os.mkdir(self.abs_path)
        except FileExistsError as e:
            print("Deleting the folder...")
            shutil.rmtree(self.abs_path)
            os.mkdir(self.abs_path)
        
    def remove_GDPR_popups(self,driver,st):
        clas = ""
        driver_ = driver
        soup_t = BeautifulSoup(driver_.page_source, 'html.parser')  
        for tag in soup_t.find_all(True):
            sear = tag.get_text()
            if sear in self.gdpr_word_list:
                clas = tag.text

        if(len(clas)>0):
            print("Removing GDPR: ",clas)
            driver_.save_screenshot(self.abs_path+f"/GDPR{st}.png")
            ele = driver_.find_element_by_xpath('//*[text()="'+clas+'"]').click()
            driver_.save_screenshot(self.abs_path+f"/GDPR_{st}.png")
            

        driver_.refresh()
        driver_.implicitly_wait(10)
        driver_.save_screenshot(self.abs_path+f"/GDPR__{st}.png")
        return driver_.page_source
        # self.tor_page_source_sel = self.tor_driver.page_source

    
    def setup_tor(self):
        
        # Assume socksport to be 7000 and exitnode as '4D2A4831BB67853A6FA01517A61B810D4480AE2F'
        tor = launch_tor_with_config(config = {'SocksPort': self.port,'ExitNodes': self.exitnode} ,tor_cmd=self.tor_path, take_ownership=True,timeout=120,init_msg_handler=print_boo_lines)
        try:
            self.tor_data = requests.get(self.url,proxies={'https': f'SOCKS5://127.0.0.1:{self.port}'})
            print("Status code (Tor):", self.tor_data.status_code)
            self.tor_status_code = self.tor_data.status_code
            options = {
                'proxy': {
                    'http': 'socks5h://127.0.0.1:7000',
                    'https': 'socks5h://127.0.0.1:7000',
                    'connection_timeout': 10
                }
            }

            self.tor_driver = webdriver.Firefox(firefox_profile=self.profile,seleniumwire_options = options)
            self.tor_driver.install_addon(self.path, temporary=True)
            self.tor_driver.get(self.url)
            self.tor_driver.implicitly_wait(10)
            self.tor_driver.save_screenshot(self.abs_path+"/Tor.png")
            self.tor_page_source_sel = self.tor_driver.page_source
            # self.remove_GDPR_popups()
            

        except Exception as e:
            print(e)
        
        tor.terminate()

    def setup_non_tor(self):
        self.non_tor_data = requests.get(self.url)
        print("Status code (Non-Tor):", self.non_tor_data.status_code)
        self.non_tor_status_code = self.non_tor_data.status_code

        self.non_tor_driver = webdriver.Firefox(firefox_profile=self.profile)
        self.non_tor_driver.install_addon(self.path, temporary=True)
        self.non_tor_driver.get(self.url)
        time.sleep(1.5)
        self.non_tor_driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL+Keys.SHIFT+'E')
        self.non_tor_driver.implicitly_wait(10)

        self.non_tor_page_source_sel = self.non_tor_driver.page_source
        self.non_tor_driver.save_screenshot(self.abs_path+"/Non_Tor.png")

        try:
            har_dict = driver.execute_async_script(
                """
                var callback = arguments[arguments.length - 1];
                HAR.triggerExport().then((harLog) => { callback(harLog) });
                """
            )
            print(json.dumps({"log": har_dict}))
            # dic_har = driver.execute_async_script("HAR;")
            # print(dic_har)
        except Exception as e:
            print(e)

    def status_checker(self):
        if self.non_tor_status_code != self.tor_status_code:
            if self.tor_status_code > 399:
                print("Error")
            elif self.tor_status_code > 299:
                # Check for redirection of website
                # Requires selenium wire to see the full HAR structure
                print("Redirected to another website")
        else:
            # Remove GDPR Popups 
            # self.remove_GDPR_popups()
            # Additional Tests DOM Check
            # Calculate change in percentage
            # For now using Beautiful soup, later will switch to selenium wire

            soup_tB = BeautifulSoup(self.tor_data.content, 'html.parser')
            soup_nB = BeautifulSoup(self.non_tor_data.content, 'html.parser')

            soup_t = BeautifulSoup(self.tor_page_source_sel, 'html.parser')
            soup_n = BeautifulSoup(self.non_tor_page_source_sel, 'html.parser')

            f = open(self.abs_path+"/tor.html", "w")
            f.write(soup_t.prettify())
            f.close()

            f = open(self.abs_path+"/non-tor.html", "w")
            f.write(soup_n.prettify())
            f.close()

            # f = open(self.abs_path+"/tor(B).html", "w")
            # f.write(soup_tB.prettify())
            # f.close()

            # f = open(self.abs_path+"/non-tor(B).html", "w")
            # f.write(soup_nB.prettify())
            # f.close()

            # Create files to contain nodes information
            count_t = 0; count_n = 0

            # f = open(self.abs_path+"/tor.node", "w")
            for tag in soup_t.find_all(True):
                count_t += 1
                # print(i, " -- ", tag.name)  # Print the names of DOM nodes
            #     f.write("{}--->{}\n".format(count_t, tag.name))
            # f.write("\nTotal Number of Tor Nodes: {}\n".format(count_t))
            # f.close()
            

            # f = open(self.abs_path+"/non-tor.node", "w")
            for tag_ in soup_n.find_all(True):
                count_n += 1
            #     f.write("{}--->{}\n".format(count_n, tag.name))
            # f.write("\nTotal Number of Tor Nodes: {}\n".format(count_t))
            # f.close()
            
            print("Nodes by tor and non-tor:")
            print(count_t,"-----",count_n)

            dom_score = 100*((count_n-count_t)/count_t)
            print("Dom Score: ", dom_score)

            soup_t = str(soup_t).lower()
            soup_n = str(soup_n).lower()

            if(dom_score != 0):
                # Remove GDPR
                """
                This step is done because there might be few cases where GDPR might arise:
                + For Both Tor and Non-Tor Browser (No need to remove GDPR for just Tor)
                + Might be a case, when Non-Tor receives a GDPR popup and Tor might not! 
                    for example Tor connects to an exitnode other than Europe, and the user is from Europe
                + Also a case when both don't get any popups or rather get blocked in the status code thing (No need to check)
                """
                
                # Remove GDPR for Tor
                page_source_tor = self.remove_GDPR_popups(self.tor_driver,"t")
                # Remove GDPR for non Tor
                page_source_non_tor = self.remove_GDPR_popups(self.non_tor_driver,"n")
                
                soup_t = BeautifulSoup(page_source_tor,'html.parser')
                soup_n = BeautifulSoup(page_source_non_tor,'html.parser')
                
                count_t = 0; count_n = 0

                f = open(self.abs_path+"/tor.node", "w")
                for tag in soup_t.find_all(True):
                    count_t += 1
                    # print(i, " -- ", tag.name)  # Print the names of DOM nodes

                for tag_ in soup_n.find_all(True):
                    count_n += 1
                
                print("After GDPR removal Nodes by tor and non-tor:")
                print(count_t,"-----",count_n)

                dom_score = 100*((count_n-count_t)/count_t)
                print("Dom Score (new): ", dom_score)

                if(dom_score > 0):
                    if( dom_score > self.max_k):   
                        #   Random value to check the performance. 
                        #   Might need some more experiments to come back with the correct value
                        print("Tor most probably returns Errors!") #  or it hasn't been loaded fully (increase loading time)")
                    elif(dom_score < self.min_k):
                        #   Random value to check the performance. 
                        #   Might need some more experiments to come back with the correct value
                        #   checks for keywords to help in this case
                        print("Resembles same...")
                        if "captcha" in soup_t and "captcha" not in soup_n:
                            print("Captcha present: checklist")
                        else:
                            print("Same..")
                    else:
                        print("Doubtful case!!")
                        print("checks for keywords...")
                        #   checks for keywords to help in this case     
                        for _ in self.match_list:
                            if _ in soup_t and _ not in soup_n:
                                print("Tor blocked : checklist")

                        if "captcha" in soup_t and "captcha" not in soup_n:
                            print("Captcha present: checklist")
                        else:
                            print("Same..")
                else:
                    print("Denotes cookie-popups (if difference is not much)")
            else: 
                print("Same Resemblance :D")
            

website_list = ["https://google.com/"]

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
]

i=0
for url in website_list:
    i+=1
    exit_node = secrets.choice(exit_relays)
    print(url," : ",exit_node)
    we = Analyser((url),exit_node)
    we.save_in_folder()
    we.setup_tor()
    we.setup_non_tor()
    we.status_checker()
    time.sleep(10)
    if i==10:
        break
