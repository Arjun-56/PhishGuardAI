import requests
import pandas as pd
from pathlib import Path
import time

def download_openphish():
    """Download OpenPhish community feed"""
    print("Downloading OpenPhish feed...")
    url = "https://openphish.com/feed.txt"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        urls = response.text.strip().split('\n')
        df = pd.DataFrame({'url': urls, 'label': 1})  # 1 = phishing
        
        print(f"Downloaded {len(df)} phishing URLs from OpenPhish")
        return df
    except Exception as e:
        print(f"Error downloading OpenPhish: {e}")
        return pd.DataFrame()

def download_phishtank():
    """Download PhishTank data (requires manual download)"""
    print("\nPhishTank requires manual download:")
    print("1. Visit: https://www.phishtank.com/developer_info.php")
    print("2. Download the CSV file")
    print("3. Place it in data/raw/phishtank.csv")
    print("\nSkipping PhishTank for now...")
    return pd.DataFrame()

def download_benign_urls():
    """Download Tranco top domains as benign samples"""
    print("\nDownloading benign URLs from Tranco...")
    url = "https://tranco-list.eu/top-1m.csv.zip"
    
    try:
        df = pd.read_csv(url, compression='zip', header=None, names=['rank', 'domain'])
        # Take top 10000 domains
        df = df.head(10000)
        df['url'] = 'https://' + df['domain']
        df['label'] = 0  # 0 = benign
        df = df[['url', 'label']]
        
        print(f"Downloaded {len(df)} benign URLs from Tranco")
        return df
    except Exception as e:
        print(f"Error downloading Tranco: {e}")
        return pd.DataFrame()

def main():
    # Create directories
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    Path('models').mkdir(parents=True, exist_ok=True)
    
    # Download datasets
    phishing_df = download_openphish()
    benign_df = download_benign_urls()
    
    # Combine
    if not phishing_df.empty and not benign_df.empty:
        # Balance dataset
        min_size = min(len(phishing_df), len(benign_df))
        phishing_df = phishing_df.sample(n=min_size, random_state=42)
        benign_df = benign_df.sample(n=min_size, random_state=42)
        
        combined_df = pd.concat([phishing_df, benign_df], ignore_index=True)
        combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save
        output_path = 'data/raw/urls.csv'
        combined_df.to_csv(output_path, index=False)
        print(f"\n[OK] Dataset saved to {output_path}")
        print(f"Total URLs: {len(combined_df)}")
        print(f"Phishing: {(combined_df['label']==1).sum()}")
        print(f"Benign: {(combined_df['label']==0).sum()}")
    else:
        print("\n[FAIL] Failed to download datasets")

if __name__ == '__main__':
    main()