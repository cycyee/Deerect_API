from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent



ua = UserAgent()

def scrape_posts(input_search):
    if isinstance(input_search, str):
        input_search = input_search.replace(' ', '+')
    
    url = f'https://www.taxliens.com/listing/search.html?q={input_search}'
    print(url)
    headers = {
        'User-Agent': ua.random,
        "authority": "www.taxliens.com",
        "method": "GET",
        "path": f"/listing/search.html?q={input_search}",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,fr;q=0.8",
        "cache-control": "max-age=0",
        "cookie": "partner=20775; listingsPerPageNew=10; _access_e2dcec174364='2024-09-25T23:36:28.353664346'; latestSearch='q=94901'; searchQuery='q=94901'; recently_viewed_listingids=62480246|62473326|62621015; __gads=ID=b4196d39eb2f0ea5:T=1722026553:RT=1729367783:S=ALNI_MafC75I3oDv5qLwjuHiPDqb_pYXgQ; __gpi=UID=00000e8a1d69898e:T=1722026553:RT=1729367783:S=ALNI_MZHnBqbIGxtq7BnKEZIe-1skKlATQ; __eoi=ID=a8344afbd2f248e4:T=1722026553:RT=1729367783:S=AA-AfjZa_ZVFiZhoVZPHh8dDgAtZ; JSESSIONID=443A9B55F2392FD1716692BF68B860E7; _gcl_au=1.1.1540189244.1730514164; _gid=GA1.2.1534464984.1730514164; currentLocation='locCity=SAN RAFAEL:locState=CA:locCounty=MARIN:locZipcode=94901'; _ga=GA1.1.470886793.1722026496; _ga_S8EQR9B85D=GS1.1.1730514163.27.1.1730514243.60.0.0",
        "if-none-match": 'W/"012d1198fb429868de88006330a20c2f7"',
        "priority": "u=0, i",
        "referer": "https://www.taxliens.com/?q=94901",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    proxies = {
        "http": "http://your_proxy_ip:port",
        "https": "http://your_proxy_ip:port",
    }

    response = requests.get(url, headers= headers, proxies= proxies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        odd_listings = soup.find_all('div', class_='odd row rowResults')
        even_listings = soup.find_all('div', class_='even row rowResults')
        listings = odd_listings + even_listings
        listings_data = []

        for listing in listings:
            listing_data = {}
            div1 = listing.find('div')
            Div2 = div1.find('div')
            info = Div2.find('div', class_='listingInfo')
            conInfo = info.find('div',class_ ='conListingInfo')
            # print("coninfo found \n")
            script = conInfo.find('script', type='application/ld+json')
            if script:
                # Extract the JSON content
                # print("script found")
                json_text = script.string
                if json_text:
                    try:
                        # Parse the JSON content
                        json_data = json.loads(json_text)
                        #print(json.dumps(json_data, indent=4))  # Pretty print JSON data
                        listings_data.append(json_data)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        return None
                else:
                    print("Script tag is empty.")
                    return None
            else:
                print("Script tag with type 'application/ld+json' not found.")
                return None
        

        # with open('listings.json', 'w') as json_file:
        #     json.dump(listings_data, json_file, indent=4)
        #     print("Data successfully scraped and saved to listings.json")
        return listings_data
            #get address here
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")



def scrape_protected_content(search_url):
    # Start a session to persist cookies
    load_dotenv()
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.taxliens.com/login.html',
        'Origin': 'https://www.taxliens.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    username = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')
    # Login URL and payload
    login_url = 'https://www.taxliens.com/login.html'
    login_payload = {
        'key': f'{username}',
        'password': f'{password}',
        'referralUrl': 'https://www.taxliens.com/',
        'serviceProviderName': 'fdc',
        'oldLegacyDomainName': 'www.foreclosurefreesearch.com',
        'loginMethod': 'username_password'
    }
    
    # Send login request
    login_response = session.post(login_url, data=login_payload, headers= headers)
    # Check login
    if login_response.status_code == 200:
        print('Logged in successfully!')
        #example url - will be gotten from listings.json links
        response = session.get(search_url, headers=headers)
        
        if response.status_code == 200:
            paid_data={}
            soup = BeautifulSoup(response.content, 'html.parser')
            div1 = soup.find('div', class_= 'container mt-4')
            div2 = div1.find('div', class_ = 'row')
            div3 = div2.find('div', class_= 'col-lg-12')
            div4 = div3.find('div', id= 'bootstrap-details')
            div5 = div4.find('div', class_= 'row')
            div6 = div5.find('div', class_= 'col-md-8')
            div7 = div6.find('div', id= 'additional_info')
            div8 = div7.find('ul', class_ = 'list-unstyled attributegroup two-column')
            li_elements = div8.find_all('li')
            for li in li_elements:
                spans = li.find_all('span')
                if len(spans) == 0:
                    continue
                label_text = spans[0].get_text(strip=True)  # First span is the label
                value_text = spans[-1].get_text(strip=True)  # Second span is the value
                paid_data[label_text] = value_text
            
            #print(paid_data)
            with open('paid.json', 'w') as json_file:
                return (paid_data)
                #json.dump(paid_data, json_file, indent=4)
                print("Data successfully scraped and saved to paid.json")
        else:
            print(f"Failed to retrieve search page. Status code: {response.status_code}")
    else:
        print(f"Failed to login. Status code: {login_response.status_code}")




app = Flask(__name__)
@app.route('/api_scrape', methods=['GET'])

def api_scrape():
    input_search = request.args.get('q')
    app.logger.debug(f"Received query: {input_search}")
    if not input_search:
        return jsonify({"error": "Please provide a search query (q parameter)."}), 400
    try:
        scraped_data = scrape_posts(input_search)
        app.logger.debug(f"Scraped data: {scraped_data}")
        #print (scraped_data)

        # for item in scraped_data:
        #     url = item.get('url')
        #     if url:
        #         paid_data =  scrape_protected_content(url)
        #         item.update(paid_data)
        return jsonify(scraped_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5000)

