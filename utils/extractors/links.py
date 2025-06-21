import re
import fitz  # PyMuPDF

def extract_links(text, pdf_path=None):
    linkedin = ""
    website = ""
    social = []

    # 1. Extract visible links from text with better patterns
    url_patterns = [
        r'https?://[^\s)>\]}]+',  # Standard URLs
        r'www\.[^\s)>\]}]+',      # URLs starting with www
        r'linkedin\.com/in/[^\s)>\]}]+',  # LinkedIn profiles
        r'github\.com/[^\s)>\]}]+',       # GitHub profiles
    ]
    
    for pattern in url_patterns:
        urls = re.findall(pattern, text)
        for url in urls:
            url = url.strip().rstrip('.,)')
            
            # Add protocol if missing
            if url.startswith('www.'):
                url = 'https://' + url
            
            if "linkedin.com" in url:
                linkedin = url
            elif "github.com" in url:
                if not website:  # Use GitHub as website if no other website found
                    website = url
                social.append(url)
            elif any(domain in url for domain in [
                "twitter.com", "instagram.com", "facebook.com",
                "behance.net", "dribbble.com", "medium.com", "youtube.com",
                "stackoverflow.com", "dev.to", "hashnode.dev"
            ]):
                social.append(url)
            else:
                if not website and not any(domain in url for domain in ["linkedin.com", "github.com"]):
                    website = url

    # 2. Extract LinkedIn from text patterns
    if not linkedin:
        linkedin_patterns = [
            r'linkedin\.com/in/([^\s)>\]}]+)',
            r'linkedin:?\s*([^\s\n]+)',
            r'linkedin profile:?\s*([^\s\n]+)',
        ]
        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                linkedin_url = match.group(1)
                if not linkedin_url.startswith('http'):
                    linkedin_url = 'https://linkedin.com/in/' + linkedin_url
                linkedin = linkedin_url
                break

    # 3. Extract GitHub from text patterns
    if not website:
        github_patterns = [
            r'github\.com/([^\s)>\]}]+)',
            r'github:?\s*([^\s\n]+)',
            r'github profile:?\s*([^\s\n]+)',
        ]
        for pattern in github_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                github_url = match.group(1)
                if not github_url.startswith('http'):
                    github_url = 'https://github.com/' + github_url
                website = github_url
                break

    # 4. Extract portfolio/website from text patterns
    if not website:
        website_patterns = [
            r'portfolio:?\s*([^\s\n]+)',
            r'website:?\s*([^\s\n]+)',
            r'personal website:?\s*([^\s\n]+)',
            r'portfolio website:?\s*([^\s\n]+)',
        ]
        for pattern in website_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                website_url = match.group(1)
                if not website_url.startswith('http'):
                    website_url = 'https://' + website_url
                website = website_url
                break

    # 5. Extract embedded links from PDF (if file path is provided)
    if pdf_path:
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    for link in page.get_links():
                        if "uri" in link:
                            uri = link["uri"]
                            if uri.startswith("http"):
                                if "linkedin.com" in uri and not linkedin:
                                    linkedin = uri
                                elif "github.com" in uri and not website:
                                    website = uri
                                elif any(domain in uri for domain in [
                                    "portfolio", "notion.so", "behance.net", "dribbble.com"
                                ]) and not website:
                                    website = uri
                                elif any(s in uri for s in ["twitter", "facebook", "instagram", "youtube", "medium"]):
                                    if uri not in social:
                                        social.append(uri)
        except Exception as e:
            print("Error reading embedded links:", e)

    # 6. Clean up URLs
    def clean_url(url):
        if not url:
            return ""
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?')
        # Ensure proper protocol
        if url.startswith('www.'):
            url = 'https://' + url
        elif not url.startswith('http'):
            url = 'https://' + url
        return url

    linkedin = clean_url(linkedin)
    website = clean_url(website)
    social = [clean_url(url) for url in social if url]

    return {
        "linkedin": linkedin,
        "website": website,
        "social": social
    }
