import re

def extract_personal(text):
    lines = text.split('\n')
    
    # Email extraction with better regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else ""
    
    # Phone extraction with better regex (handles various formats)
    phone_patterns = [
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
        r'\+?[0-9]{1,4}[-.\s]?[0-9]{6,14}',  # International format
        r'[0-9]{10,15}',  # Simple numeric
    ]
    
    phone = ""
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group(0)
            break
    
    # Name extraction - improved logic
    name = ""
    
    # Method 1: Look for lines that look like names (2-4 words, no special chars)
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not line:
            continue
            
        # Skip if line contains email or phone
        if email and email in line:
            continue
        if phone and phone in line:
            continue
            
        # Skip if line has too many words or special characters
        words = line.split()
        if len(words) < 2 or len(words) > 4:
            continue
            
        # Check if line looks like a name (no numbers, limited special chars)
        if re.match(r'^[A-Za-z\s\.\-]+$', line) and len(line) > 3:
            # Skip common non-name words
            skip_words = ['resume', 'cv', 'curriculum vitae', 'profile', 'portfolio', 'objective', 'summary']
            if not any(skip_word in line.lower() for skip_word in skip_words):
                name = line
                break
    
    # Method 2: If no name found, look for capitalized lines
    if not name:
        for line in lines[:15]:
            line = line.strip()
            if not line:
                continue
                
            # Skip if line contains email or phone
            if email and email in line:
                continue
            if phone and phone in line:
                continue
                
            # Look for properly capitalized names
            if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', line) and 3 < len(line) < 50:
                skip_words = ['resume', 'cv', 'curriculum vitae', 'profile', 'portfolio']
                if not any(skip_word in line.lower() for skip_word in skip_words):
                    name = line
                    break
    
    # Method 3: Extract from email if available
    if not name and email:
        email_parts = email.split('@')[0]
        # Convert email username to name format
        name_parts = email_parts.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        name = ' '.join(word.capitalize() for word in name_parts.split())
    
    return {
        "name": name,
        "email": email,
        "phone": phone
    }
