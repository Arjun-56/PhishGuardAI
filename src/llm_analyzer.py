import os
from groq import Groq
import json

class LLMAnalyzer:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )
        self.model = "llama3-8b-8192"
    
    def analyze_url(self, url):
        prompt = f"""
        Analyze this URL for phishing: {url}
        
        Consider:
        - Domain structure and legitimacy
        - Brand impersonation
        - Suspicious keywords
        - TLD reputation
        - Overall trustworthiness
        
        Return JSON with:
        {{
            "risk_score": 0-100,
            "status": "safe" or "suspicious" or "phishing",
            "reason": "brief explanation",
            "key_factors": ["factor1", "factor2", "factor3"]
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert specializing in phishing detection. Be accurate and conservative - legitimate URLs should get low risk scores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
