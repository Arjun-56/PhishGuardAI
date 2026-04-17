"""
Brand Detection Module
Detects brand impersonation and lookalike domains
"""

import re
from urllib.parse import urlparse
import Levenshtein


class BrandDetector:
    """Detect brand impersonation in URLs"""
    
    def __init__(self):
        self.known_brands = {
            'paypal': ['paypal.com', 'paypal.co.uk', 'paypal.de'],
            'apple': ['apple.com', 'icloud.com', 'me.com'],
            'microsoft': ['microsoft.com', 'outlook.com', 'live.com', 'hotmail.com', 'msn.com'],
            'amazon': ['amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.in', 'amazon.ca'],
            'google': ['google.com', 'gmail.com', 'youtube.com', 'drive.google.com'],
            'facebook': ['facebook.com', 'fb.com', 'instagram.com', 'whatsapp.com'],
            'netflix': ['netflix.com'],
            'chase': ['chase.com'],
            'wellsfargo': ['wellsfargo.com'],
            'bankofamerica': ['bankofamerica.com', 'bofa.com'],
            'citi': ['citi.com', 'citibank.com'],
            'amex': ['americanexpress.com', 'amex.com'],
            'visa': ['visa.com'],
            'mastercard': ['mastercard.com'],
            'yahoo': ['yahoo.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'snapchat': ['snapchat.com'],
            'telegram': ['telegram.org', 't.me'],
            'dropbox': ['dropbox.com'],
            'github': ['github.com'],
            'spotify': ['spotify.com'],
            'adobe': ['adobe.com'],
        }
        
        self.suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'gq', 'top', 'xyz', 'click', 'link']
    
    def check_url(self, url):
        """
        Check if URL is attempting to impersonate a brand
        Returns dict with detection results
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        result = {
            'is_suspicious': False,
            'matched_brand': None,
            'similarity': 0.0,
            'reason': None,
            'indicators': []
        }
        
        # Check 1: Direct brand name in domain with suspicious TLD
        for brand, official_domains in self.known_brands.items():
            if brand in domain:
                # Check if it's the official domain
                is_official = any(official in domain for official in official_domains)
                
                if not is_official:
                    result['is_suspicious'] = True
                    result['matched_brand'] = brand.title()
                    result['reason'] = f"Brand name '{brand}' found in non-official domain"
                    result['indicators'].append('brand_in_domain')
                    
                    # Check for suspicious TLD
                    tld = domain.split('.')[-1] if '.' in domain else ''
                    if tld in self.suspicious_tlds:
                        result['indicators'].append('suspicious_tld')
                        result['reason'] += f" with suspicious TLD (.{tld})"
                    
                    # Calculate similarity with official domains
                    max_similarity = max(
                        self._domain_similarity(domain, official)
                        for official in official_domains
                    )
                    result['similarity'] = max_similarity
                    
                    return result
        
        # Check 2: Lookalike domains (typosquatting)
        for brand, official_domains in self.known_brands.items():
            for official in official_domains:
                similarity = self._domain_similarity(domain, official)
                
                # High similarity but not exact match = potential typosquatting
                if 0.7 < similarity < 1.0:
                    result['is_suspicious'] = True
                    result['matched_brand'] = brand.title()
                    result['similarity'] = similarity
                    result['reason'] = f"Domain similar to {brand}'s official domain ({similarity*100:.0f}% match)"
                    result['indicators'].append('lookalike_domain')
                    return result
        
        # Check 3: Brand name in subdomain of suspicious domain
        if parsed.hostname:
            parts = parsed.hostname.lower().split('.')
            if len(parts) > 2:  # Has subdomain
                for brand in self.known_brands.keys():
                    if brand in parts[0]:
                        result['is_suspicious'] = True
                        result['matched_brand'] = brand.title()
                        result['reason'] = f"Brand name '{brand}' in subdomain of unknown domain"
                        result['indicators'].append('brand_in_subdomain')
                        return result
        
        return result
    
    def _domain_similarity(self, domain1, domain2):
        """Calculate similarity between two domains using Levenshtein distance"""
        # Remove TLD for comparison
        d1 = domain1.split('.')[0] if '.' in domain1 else domain1
        d2 = domain2.split('.')[0] if '.' in domain2 else domain2
        
        if not d1 or not d2:
            return 0.0
        
        distance = Levenshtein.distance(d1, d2)
        max_len = max(len(d1), len(d2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return max(0.0, similarity)
    
    def get_brand_list(self):
        """Return list of all known brands"""
        return list(self.known_brands.keys())
