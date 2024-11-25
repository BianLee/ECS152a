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

#this code is a refined version of my original code after referencing GPT's generation.
#I refactored some of my code through use of functions instead of having no organization.

browsermob_binary_path = "/Users/work/Desktop/ECS152a/Project2/browsermob-proxy-2.1.4/bin/browsermob-proxy"
directory_to_save = "har_file_directory"



def create_directory(directory):
    if not os.path.exists(directory): os.makedirs(directory)


def start_proxy_server(binary_path, retries):
    for attempt in range(retries):
        try:
            server = Server(binary_path)
            server.start()
            proxy = server.create_proxy(params={'timeout': 30})
            return server, proxy
        except Exception as e:
            print(f"Proxy start attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise Exception("Failed to start proxy server after maximum retries")
            time.sleep(2)


def initialize_driver(proxy_address):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f'--proxy-server={proxy_address}')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def read_sites_from_file(file_path, limit):
    sites = []
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if i >= limit:
                break
            parts = line.strip().split(',')
            sites.append(parts[1])
    return sites


def collect_har(proxy, driver, site, save_path, retries):
    for attempt in range(retries):
        try:
            proxy.new_har(site, options={'captureHeaders': True})
            try:
                driver.get(f"http://{site}")
            except TimeoutException:
                print(f"Page load timeout for {site}")
            time.sleep(10)
            with open(save_path, 'w') as file:
                file.write(json.dumps(proxy.har))
            print(f"{site}'s HAR is collected")

            return
        except (socket.timeout, urllib3.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print(f"{attempt + 1} attempt failed for {site}: {e}")
            if attempt == retries - 1:
                print(f"Max retries reached for {site}, moving on")
        except Exception as e:
            print(f"Unexpected error for {site}: {e}")
            break


def main():
    create_directory(directory_to_save)

    server, proxy = start_proxy_server(browsermob_binary_path, 3)
    driver = initialize_driver(proxy.proxy)
    
    sites = read_sites_from_file('top-1m.csv', 1000)

    for site in sites:
        save_path = os.path.join(directory_to_save, f"{site.replace('/', '_')}.har")
        if os.path.exists(save_path):
            continue
        print(f"Collecting HAR from: {site}")
        collect_har(proxy, driver, site, save_path, 3)


    driver.quit()
    server.stop()


if __name__ == "__main__":
    main()
