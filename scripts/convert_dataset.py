"""
Convert malicious_phish.csv format to urls.csv format
"""

import pandas as pd
from pathlib import Path

def convert_dataset(input_file='data/raw/malicious_phish.csv', output_file='data/raw/urls.csv'):
    """Convert dataset from (url, type) to (url, label) format"""
    print(f"Loading {input_file}...")
    
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} URLs")
    print(f"Types: {df['type'].value_counts()}")
    
    # Convert type to label
    label_map = {
        'phishing': 1,
        'benign': 0,
        'defacement': 1  # Treat defacement as phishing
    }
    
    df['label'] = df['type'].map(label_map)
    
    # Drop type column
    df = df[['url', 'label']]
    
    # Remove rows with missing labels
    df = df.dropna(subset=['label'])
    
    # Ensure label is integer
    df['label'] = df['label'].astype(int)
    
    print(f"After conversion: {len(df)} URLs")
    print(f"Labels: {df['label'].value_counts()}")
    
    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save
    df.to_csv(output_file, index=False)
    print(f"✅ Saved to {output_file}")

if __name__ == '__main__':
    convert_dataset()
