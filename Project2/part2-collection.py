import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server

browsermob_path = "/Users/work/Desktop/ECS152a/Project2/browsermob-proxy-2.1.4/bin/browsermob-proxy"
directory_to_save = "har_file_directory"

# initializing browser_mob proxy
server_instance = Server(browsermob_path)
server_instance.start()
proxy = server_instance.create_proxy()

# initialiuzing chrome webdriver with certain options, such as routing traffic to proxy, and using headless, etc
webdriver_option_settings = Options()
webdriver_option_settings.add_argument('--headless')
webdriver_option_settings.add_argument('--ignore-certificate-errors')
webdriver_option_settings.add_argument(f'--proxy-server={proxy.proxy}')
driver = webdriver.Chrome(options=webdriver_option_settings)

if not os.path.exists(directory_to_save): os.makedirs(directory_to_save) #checking if /har_file_directory exists

try:
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

        #after this loop is done the list should look like [google.com, amazonaws.com, amazonaws.com, ...]


    # iterate over all the sites in the sites list
    for i in range(len(sites)):
        site = sites[i]
        print("Collecting from " + str(i+1) + "/" + str(len(sites)) + ": " + str(site))
        try:
            proxy.new_har(site)
            driver.get("http://" + site)
            time.sleep(5)  # give some time for the page to loads
            har_data_to_save = proxy.har # get the actual HAR data
            filename = os.path.join(directory_to_save, f"{site.replace('/', '_')}.har")
            with open(filename, 'w') as f:
                json.dump(har_data_to_save, f)

        except Exception:
            print("error while collecting")

        time.sleep(1)

except Exception as e:
    print("error")

if driver:
    driver.quit()
if server_instance:
    server_instance.stop()
