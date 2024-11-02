from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv



def scrape_posts(input_search):
    if isinstance(input_search, str):
        input_search = input_search.replace(' ', '+')
    
    url = f'https://www.taxliens.com/listing/search.html?q={input_search}'
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers = headers)
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
    if not input_search:
        return jsonify({"error": "Please provide a search query (q parameter)."}), 400
    try:
        scraped_data = scrape_posts(input_search)
        #print (scraped_data)

        # for item in scraped_data:
        #     url = item.get('url')
        #     if url:
        #         paid_data =  scrape_protected_content(url)
        #         item.update(paid_data)
        return jsonify(scraped_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', debug=True, port=5000)

