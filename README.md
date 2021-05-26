# Fetcher

## The scripts and data in here are kept here for ananlysis and experimental purpose.

As of now there are currently 2 versions of the code and many more to be added later :

**- Version 1.0 :**

The `exp.py` is the fetcher code. Inside it there is a list named web_list containing websites, to be fetched, each url creates a folder named by it's url which then consists of the html code fetched by the Tor Brower, the html code fetched by Normal Brower and the screenshots from the different browsers for now.

There's a txt file for every folders. For eg: In Non-Cookie there's a file named: [site_info_nodes.txt](https://github.com/Hackhard/Fetcher/blob/main/1.0/Non-cookie/site_info_nodes.txt) which contains the details of all the DOM nodes of the websites and also the length of html to see the stats. Currently there are three folders :

   + cookie
   + Non-Cookie
   + Error_websites

Cookie: Contains the non-timeout website from [The Top 50 Alexa sites](https://www.alexa.com/topsites/). This folder reuses the cookie generated from the Normal Browser and adds to the Tor Browser to check the behaviour.

Non-Cookie : Contains the non-timeout websites from [The Top 50 Alexa sites](https://www.alexa.com/topsites/). This folder doesn't use cookies from the normal browser.

Error_websites: The folder contains few of the known [websites](https://gitlab.torproject.org/tpo/team/-/wikis/List-of-services-blocking-Tor#list-of-services-blocking-tor-1) that returns error or similar.

-------------------------------------------

**- Version 2.0 :**

Like version 1.0 here the `exp.py` file is the code that fetches different websites. The changes I've done is earlier, `site_info_nodes.txt` was a separate file containing all details of the websites in a single file which was a bit difficult to see and debug.

So I updated it to the different website folders, with 2 files, one for tor (tor_<website>_DOM_nodes.txt) and the other for non-tor (non_tor_<website>_DOM_nodes.txt), so that diff checking could be easier.
   
For few websites which I had the cookie based approach (consent pages) didn't work as intended or has some flaws so I haven't added the cookie results. The `disp.txt` contains the scores and different information related to each site.

## Status code Version 
   
   Used to fetch websites and find differences in the status codes returned from Tor and Non-Tor clients. Contains response path as well as status codes for each path generated. The `test_run` was to contain just the basic idea, `test_run2` contains updated code and implements the marked cases from https://hackhard.github.io/my-blog/Community-Bonding-I-24-05.
