import os
from urllib.parse import urlparse

import json
def get_domain(url):
    try:
        full_domain = urlparse(url).netloc
        if not full_domain: return ""
            
        domain_parts = full_domain.split('.')
        
        if len(domain_parts) == 2: # already full domain (no other subdomains, etc)
            return full_domain
    
        return domain_parts[-2]+ '.' + domain_parts[-1]
    except:
        return ""



domains,cookies =dict(),dict()


for file in os.listdir("har_file_directory"):
    path = os.path.join("har_file_directory", file)
    with open(path) as f:
        data = json.load(f)
        
        page_domain = get_domain(data['log']['pages'][0]['title'])
    
        for entry in data['log']['entries']:
            requested_domain = get_domain(entry['request']['url'])
            
            if requested_domain != page_domain:
                if requested_domain in domains:
                    domains[requested_domain] += 1
                else:
                    domains[requested_domain] = 1
                
                for header in entry['request']['headers']:
                    if header['name'].lower() == 'cookie':
                        cookie_string = header['value']
                        cookie_list = cookie_string.split(';')
                        
                        for cookie in cookie_list:
                            cookie_name = cookie.split('=')[0].strip()
                            
                            if cookie_name in cookies:
                                cookies[cookie_name] += 1
                            else:
                                cookies[cookie_name] = 1

# sort by second value
sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True) 
sorted_cookies = sorted(cookies.items(), key=lambda x: x[1], reverse=True)

for domain, count in sorted_domains[:10]:
    print(f"{domain} {count}")

print("\n") #for formatting purposes

for cookie, count in sorted_cookies[:10]:
    print(f"{cookie} {count}")