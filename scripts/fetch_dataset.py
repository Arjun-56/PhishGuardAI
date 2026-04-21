"""
Fetch phishing URLs from OpenPhish and PhishTank
Fetch benign URLs from Tranco
"""

import requests
import pandas as pd
import time
from datetime import datetime
import os
from pathlib import Path

def fetch_openphish(limit=15000):
    """Fetch phishing URLs from OpenPhish"""
    print(f"Fetching {limit} URLs from OpenPhish...")
    urls = []
    
    try:
        response = requests.get('https://openphish.com/feed.txt', timeout=30)
        if response.status_code == 200:
            all_urls = response.text.strip().split('\n')
            urls = all_urls[:limit]
            print(f"✅ Fetched {len(urls)} URLs from OpenPhish")
    except Exception as e:
        print(f"❌ Error fetching OpenPhish: {e}")
    
    return urls

def fetch_phishtank(limit=15000):
    """Fetch phishing URLs from PhishTank"""
    print(f"Fetching {limit} URLs from PhishTank...")
    urls = []
    
    try:
        response = requests.get('https://data.phishtank.com/data/online-valid.csv.gz', timeout=60)
        if response.status_code == 200:
            import gzip
            import io
            
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            
            lines = content.split('\n')
            for line in lines[1:limit+1]:
                if line:
                    parts = line.split(',')
                    if len(parts) > 1:
                        urls.append(parts[1])
            
            print(f"✅ Fetched {len(urls)} URLs from PhishTank")
    except Exception as e:
        print(f"❌ Error fetching PhishTank: {e}")
    
    return urls

def fetch_urlhaus(limit=15000):
    """Fetch phishing URLs from URLHaus"""
    print(f"Fetching {limit} URLs from URLHaus...")
    urls = []
    
    try:
        response = requests.get('https://urlhaus.abuse.ch/downloads/csv_recent/', timeout=60)
        if response.status_code == 200:
            lines = response.text.split('\n')
            for line in lines[2:limit+2]:  # Skip header
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) > 2:
                        url = parts[2].strip('"')
                        if url.startswith('http'):
                            urls.append(url)
            
            print(f"✅ Fetched {len(urls)} URLs from URLHaus")
    except Exception as e:
        print(f"❌ Error fetching URLHaus: {e}")
    
    return urls

def fetch_tranco(limit=15000):
    """Fetch benign URLs from Tranco (top websites)"""
    print(f"Fetching {limit} benign URLs from Tranco...")
    urls = []
    
    try:
        response = requests.get('https://tranco-list.eu/top-1m.csv.zip', timeout=60)
        if response.status_code == 200:
            import zipfile
            import io
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                with z.open('top-1m.csv') as f:
                    content = f.read().decode('utf-8')
            
            lines = content.split('\n')
            for line in lines[1:limit+1]:
                if line:
                    parts = line.split(',')
                    if len(parts) > 0:
                        domain = parts[0]
                        urls.append(f"https://{domain}")
            
            print(f"✅ Fetched {len(urls)} benign URLs from Tranco")
    except Exception as e:
        print(f"❌ Error fetching Tranco: {e}")
    
    return urls

def create_dataset(phishing_urls, benign_urls, output_file='data/raw/urls.csv'):
    """Create balanced dataset"""
    print(f"Creating balanced dataset...")
    print(f"Phishing URLs: {len(phishing_urls)}")
    print(f"Benign URLs: {len(benign_urls)}")
    
    min_count = min(len(phishing_urls), len(benign_urls))
    phishing_urls = phishing_urls[:min_count]
    benign_urls = benign_urls[:min_count]
    
    data = []
    for url in phishing_urls:
        data.append({'url': url, 'label': 1})
    for url in benign_urls:
        data.append({'url': url, 'label': 0})
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Create directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f"✅ Dataset saved to {output_file}")
    print(f"Total URLs: {len(df)}")
    print(f"Phishing: {len(df[df['label'] == 1])}")
    print(f"Benign: {len(df[df['label'] == 0])}")

def main():
    print("=== Fetching Dataset ===")
    print(f"Started at: {datetime.now()}")
    
    openphish_urls = fetch_openphish(limit=15000)
    phishtank_urls = fetch_phishtank(limit=15000)
    urlhaus_urls = fetch_urlhaus(limit=15000)
    
    phishing_urls = openphish_urls + phishtank_urls + urlhaus_urls
    phishing_urls = list(set(phishing_urls))
    phishing_urls = phishing_urls[:15000]
    
    benign_urls = fetch_tranco(limit=15000)
    
    create_dataset(phishing_urls, benign_urls)
    
    print(f"Completed at: {datetime.now()}")

if __name__ == '__main__':
    main()
