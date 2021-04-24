# Fetcher


There are currently 2 versions of the code :

- Version 1.0 :

The `exp.py` is the fetcher code. Inside it there is a list named web_list containing websites, to be fetched, each url creates a folder named by it's url which then consists of the html code fetched by the Tor Brower, the html code fetched by Normal Brower and the screenshots from the different browsers for now.

There's a txt file for every folders. For eg: In Non-Cookie there's a file named: [site_info_nodes.txt]() which contains the details of all the DOM nodes of the websites and also the length of html to see the stats. Currently there are three folders :

   + cookie
   + Non-Cookie
   + Error_websites

Cookie: Contains the non-timeout website from Top 50 Alexa sites. This folder reuses the cookie generated from the Normal Browser and adds to the Tor Browser to check the behaviour.

Non-Cookie : Contains the non-timeout websites from [The Top 50 Alexa sites](https://www.alexa.com/topsites/). This folder doesn't use cookies from the normal browser.

Error_websites: The folder contains few of the known [websites](https://gitlab.torproject.org/tpo/team/-/wikis/List-of-services-blocking-Tor#list-of-services-blocking-tor-1) that returns error or similar.

-------------------------------------------

- Version 2.0 : 

Like version 1.0 here the exp.py file is the code that fetches websites. The changes I've done is earlier, site_info_nodes.txt was a separate file containing all details of the websites in a single file.
Which was a bit difficult to see and debug, so I updated it to the different website folders, with 2 files, one for tor and the other for non-tor, so that diff checking could be easier.
For few websites which I had the cookie based approach (consent pages) didn't work as intended so I haven't added the cookie results. The `disp.txt` contains the scores and different information related to each site.
