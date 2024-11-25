import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from browsermobproxy import Server
import requests.exceptions
import urllib3.exceptions
import socket

browsermob_binary_path = "/Users/work/Desktop/ECS152a/Project2/browsermob-proxy-2.1.4/bin/browsermob-proxy"
directory_to_save = "har_file_directory"

#note: 30 seconds is the page load timeout threshold

# create output directory if it doesn't exist
if not os.path.exists(directory_to_save): os.makedirs(directory_to_save)

# Start browsermob proxy with retries
retry_count = 0
server, proxy = None,None
while retry_count < 3:
    try:
        server = Server(browsermob_binary_path)
        server.start()
        proxy = server.create_proxy(params={'timeout': 30})
        break
    except Exception as e:
        retry_count += 1
        print(f"Proxy start attempt {retry_count} failed: {e}")
        if retry_count == 3:
            raise Exception("Failed to start proxy server after maximum retries")
        time.sleep(2)


#some configuration settings for the driver
driver_chrome_options = Options()
driver_chrome_options.add_argument('--headless')# bascically prevent the window popping up  
driver_chrome_options.add_argument('--ignore-certificate-errors')
driver_chrome_options.add_argument(f'--proxy-server={proxy.proxy}')

driver = webdriver.Chrome(options=driver_chrome_options)
driver.set_page_load_timeout(30)



sites = list()

with open('top-1m.csv', 'r') as file: #open the top-1m.csv file which contains the list of websites
        i=0
        for l in file:
            if i >= 1000: 
                break #stop when you have more than 1000 websites read from the file
            parts = l.strip().split(',')
            site_domain = parts[1] 
            sites.append(site_domain)
            i+=1 #increment
            # in this forloop parse only the domain part into the sites array


for i in range(len(sites)):
    site = sites[i]
    filename_to_save = os.path.join(directory_to_save, f"{site.replace('/', '_')}.har")
    
    if os.path.exists(filename_to_save): continue #already exists, so skip over

    print(f"Collecting HAR from: {site}")

    retry_count = 0
    while retry_count < 3: #3 is threshold
        try:
            proxy.new_har(site, options={'captureHeaders': True})
            try:
                driver.get("http://" + site) #actually access site
            except TimeoutException:
                print(f"Page load timeout")
            
            time.sleep(10) #giving some wait time
            
            #har_data = proxy.har
            with open(filename_to_save, 'w') as f:
                f.write(json.dumps(proxy.har))
                
            print(f"{site}'s HAR is collected")
            break

        except (socket.timeout, urllib3.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            time.sleep(3)
            retry_count+=1
            print(f"{retry_count} attempt failed for {site}")
            if retry_count == 3: #reached threshold for the retries, which is 3
                print(f"Max retry reached, moving on")
                break
            
        except Exception as e:
            print(f"Unexpected errors")
            break



driver.quit() #close webdriver
server.stop() #stop the proxy server
