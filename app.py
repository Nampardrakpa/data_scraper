from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_links_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        return [loc.text for loc in soup.find_all('loc')]
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return []
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        return []

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for element in soup(['script', 'style', 'svg', 'noscript']):
            element.decompose()

        return soup.get_text(separator=' ', strip=True)
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return ""
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return ""

def scrape_website_text(base_sitemap_url):
    content_dict = {}
    
    sitemap_urls = get_links_from_sitemap(base_sitemap_url)
    
    for sitemap_url in sitemap_urls:
        print(f"Extracting links from: {sitemap_url}")
        
        page_urls = get_links_from_sitemap(sitemap_url)
        
        for page_url in page_urls:
            if any(exclusion in page_url.lower() for exclusion in ['.jpg', '.svg', 'wp-content']):
                print(f"Skipping URL: {page_url}")
                continue
            
            print(f"Extracting text from: {page_url}")
            content = extract_text_from_url(page_url)
            if content:
                content_dict[page_url] = content
            else:
                print(f"Failed to extract content from: {page_url}")
    
    return content_dict

@app.route('/scrape/<path:sitemap_url>', methods=['GET'])
def scrape_website(sitemap_url):
    try:
        website_content = scrape_website_text(sitemap_url)
        
        if not website_content:
            return jsonify({'error': 'Failed to scrape content from the provided sitemap URL'}), 500
        
        return jsonify(website_content), 200
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
