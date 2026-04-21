"""
URL Feature Extractor Module
Extracts features from URLs for phishing detection
"""

import re
import math
from urllib.parse import urlparse
import tldextract
import numpy as np
from collections import Counter


class URLFeatureExtractor:
    """Extract features from URLs for machine learning"""
    
    def __init__(self):
        self.suspicious_keywords = [
            'login', 'signin', 'verify', 'account', 'update', 'secure', 'banking',
            'password', 'credential', 'confirm', 'security', 'authentication',
            'login-secure', 'signin-verification', 'account-update', 'secure-verify'
        ]
        
        self.brand_names = [
            'paypal', 'apple', 'microsoft', 'amazon', 'google', 'facebook',
            'netflix', 'bank', 'chase', 'wellsfargo', 'citi', 'amex', 'visa',
            'mastercard', 'icloud', 'outlook', 'gmail', 'yahoo', 'instagram',
            'twitter', 'linkedin', 'snapchat', 'whatsapp', 'telegram'
        ]
        
        self.shortening_services = [
            'bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'buff.ly',
            'is.gd', 'short.link', 'rebrand.ly', 'cutt.ly'
        ]
    
    def extract_single(self, url):
        """Extract features from a single URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
        except (ValueError, Exception) as e:
            # Skip invalid URLs (e.g., invalid IPv6 URLs)
            print(f"Skipping invalid URL: {url} - Error: {e}")
            return None
        
        domain = f"{extracted.domain}.{extracted.suffix}"
        subdomain = extracted.subdomain
        full_domain = f"{subdomain}.{domain}" if subdomain else domain
        
        features = {
            # URL structure features
            'url_length': len(url),
            'domain_length': len(domain),
            'subdomain_count': len(subdomain.split('.')) if subdomain else 0,
            'path_length': len(parsed.path),
            'path_depth': len([x for x in parsed.path.split('/') if x]),
            'query_length': len(parsed.query),
            'has_query': 1 if parsed.query else 0,
            'has_fragment': 1 if parsed.fragment else 0,
            
            # Special character counts
            'dot_count': url.count('.'),
            'hyphen_count': url.count('-'),
            'underscore_count': url.count('_'),
            'slash_count': url.count('/'),
            'question_count': url.count('?'),
            'equals_count': url.count('='),
            'ampersand_count': url.count('&'),
            'at_count': url.count('@'),
            'percent_count': url.count('%'),
            'plus_count': url.count('+'),
            'digit_count': sum(c.isdigit() for c in url),
            'letter_count': sum(c.isalpha() for c in url),
            
            # Security indicators
            'has_https': 1 if url.startswith('https://') else 0,
            'has_http': 1 if url.startswith('http://') else 0,
            'suspicious_keywords': sum(1 for kw in self.suspicious_keywords if kw in url.lower()),
            'has_ip_address': 1 if self._has_ip_address(url) else 0,
            'is_shortened': 1 if any(svc in url.lower() for svc in self.shortening_services) else 0,
            
            # Domain features
            'has_brand_name': sum(1 for brand in self.brand_names if brand in url.lower()),
            'has_suspicious_tld': 1 if extracted.suffix in ['tk', 'ml', 'ga', 'cf', 'gq'] else 0,
            'domain_digit_count': sum(c.isdigit() for c in domain),
            'domain_letter_count': sum(c.isalpha() for c in domain),
            
            # Entropy (randomness indicator)
            'entropy': self._calculate_entropy(domain),
            
            # Subdomain features
            'subdomain_length': len(subdomain) if subdomain else 0,
            'has_www': 1 if 'www' in subdomain.lower() else 0,
        }
        
        return features
    
    def extract_batch(self, urls):
        """Extract features from a list of URLs"""
        return [self.extract_single(url) for url in urls]
    
    def _has_ip_address(self, url):
        """Check if URL contains IP address"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return bool(re.search(ip_pattern, url))
    
    def _calculate_entropy(self, text):
        """Calculate Shannon entropy of text"""
        if not text:
            return 0
        
        freq = Counter(text)
        length = len(text)
        entropy = -sum((count/length) * math.log2(count/length) for count in freq.values())
        return entropy
