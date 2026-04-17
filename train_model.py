import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.features import URLFeatureExtractor
from src.model import PhishingModel

def main():
    print("=" * 60)
    print("Phishing Detection Model Training Pipeline")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading dataset...")
    data_path = 'data/raw/urls.csv'
    
    if not Path(data_path).exists():
        print(f"[ERROR] Dataset not found at {data_path}")
        print("Please run: python scripts/download_data.py")
        return
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} URLs")
    print(f"Phishing: {(df['label']==1).sum()}, Benign: {(df['label']==0).sum()}")
    
    # Extract features
    print("\n2. Extracting features...")
    extractor = URLFeatureExtractor()
    features_list = []
    
    for idx, url in enumerate(df['url']):
        if idx % 1000 == 0:
            print(f"Processed {idx}/{len(df)} URLs...")
        features = extractor.extract_single(url)
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    print(f"Extracted {len(features_df.columns)} features")
    
    # Save processed data
    features_df.to_csv('data/processed/features.csv', index=False)
    df['label'].to_csv('data/processed/labels.csv', index=False)
    print("Features saved to data/processed/")
    
    # Train model
    print("\n3. Training model...")
    model = PhishingModel()
    results = model.train(features_df, df['label'])
    
    # Save model
    print("\n4. Saving model...")
    model.save()
    
    print("\n" + "=" * 60)
    print("[OK] Training Complete!")
    print("=" * 60)
    print(f"ROC-AUC: {results['roc_auc']:.4f}")
    print(f"PR-AUC: {results['pr_auc']:.4f}")
    print("\nRun the app: streamlit run app.py")

if __name__ == '__main__':
    main()