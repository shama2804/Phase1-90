import re

def extract_experience(text):
    lines = text.split('\n')
    experience = {
        "total_experience": "",
        "job_title": "",
        "current_company": "",
        "employment_type": "",
        "employment_duration": "",
        "job_responsibilities": "",
        "previous_employers": [],
        "achievements": ""
    }

    # Step 1: Find the 'Experience' section
    start_idx = -1
    for i, line in enumerate(lines):
        if re.search(r'\b(experience|work experience|internship experience|professional experience|employment history)\b', line.lower()):
            start_idx = i
            break

    if start_idx == -1:
        return experience  # No experience section found

    # Only process lines under 'Experience' section
    section_lines = lines[start_idx + 1:]

    # Step 2: Extract details
    for i, line in enumerate(section_lines):
        lower = line.lower().strip()
        clean_line = line.strip()

        # Duration extraction with better patterns
        duration_patterns = [
            r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,-]*\d{4})\s*(?:–|to|-|until)\s*(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,-]*\d{4}|\b(?:present|current|now))',
            r'(\d{4})\s*(?:–|to|-)\s*(\d{4}|present|current)',
            r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4})\s*(?:–|to|-)\s*(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|\b(?:present|current))'
        ]
        
        for pattern in duration_patterns:
            duration_match = re.search(pattern, lower)
            if duration_match:
                experience["employment_duration"] = duration_match.group(0).title()
                break

        # Job title extraction with more comprehensive patterns
        if not experience["job_title"]:
            title_patterns = [
                r'\b(intern|assistant|developer|engineer|analyst|consultant|researcher|manager|coordinator|lead|architect|designer|specialist|officer|executive|associate|senior|junior|principal|head|director|vp|ceo|cto|founder|co-founder)\b',
                r'\b(software|web|frontend|backend|fullstack|data|machine learning|ai|devops|cloud|mobile|ui|ux|product|project|business|marketing|sales|hr|finance|operations|quality|test|qa|support|admin|system|network|security|database|bi|analytics)\b'
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, lower)
                if title_match:
                    # Get more context for the title
                    words = clean_line.split()
                    title_words = []
                    for word in words:
                        if re.search(pattern, word.lower()):
                            title_words.append(word)
                        elif title_words and len(title_words) < 4:  # Add adjacent words
                            title_words.append(word)
                    if title_words:
                        experience["job_title"] = ' '.join(title_words).title()
                        break

        # Employment type detection
        if "intern" in lower or "internship" in lower:
            experience["employment_type"] = "Internship"
        elif "full-time" in lower or "full time" in lower:
            experience["employment_type"] = "Full-time"
        elif "part-time" in lower or "part time" in lower:
            experience["employment_type"] = "Part-time"
        elif "contract" in lower:
            experience["employment_type"] = "Contract"
        elif "freelance" in lower:
            experience["employment_type"] = "Freelance"

        # Company extraction with better patterns
        if not experience["current_company"]:
            company_patterns = [
                r'(?:at|for|with)\s+([A-Z][A-Za-z0-9&.\s-]{3,})',
                r'([A-Z][A-Za-z0-9&.\s-]{3,})\s+(?:inc|corp|llc|ltd|company|corporation)',
                r'([A-Z][A-Za-z0-9&.\s-]{3,})\s*[-–]\s*[A-Za-z\s]+'  # Company - Location format
            ]
            
            for pattern in company_patterns:
                company_match = re.search(pattern, clean_line)
                if company_match:
                    company_name = company_match.group(1).strip()
                    # Clean up company name
                    company_name = re.sub(r'\s+', ' ', company_name)  # Remove extra spaces
                    experience["current_company"] = company_name
                    break

        # Responsibilities extraction
        if any(keyword in lower for keyword in ["responsibilities", "key contributions", "roles", "duties", "achievements", "key responsibilities"]):
            resp_lines = []
            # Collect lines until we hit another section or empty line
            for j in range(i + 1, len(section_lines)):
                next_line = section_lines[j].strip()
                if not next_line:
                    break
                # Stop if we hit another section header
                if re.match(r'^[A-Z][A-Z\s:]{3,}$', next_line):
                    break
                resp_lines.append(next_line)
            
            if resp_lines:
                experience["job_responsibilities"] = " ".join(resp_lines)
                break

    # If no specific job title found, try to infer from context
    if not experience["job_title"]:
        # Look for common job title patterns in the entire text
        for line in lines:
            lower = line.lower()
            if any(keyword in lower for keyword in ["software engineer", "developer", "analyst", "manager", "intern"]):
                words = line.split()
                for i, word in enumerate(words):
                    if any(keyword in word.lower() for keyword in ["engineer", "developer", "analyst", "manager", "intern"]):
                        # Get 2-3 words around this keyword
                        start = max(0, i - 1)
                        end = min(len(words), i + 2)
                        experience["job_title"] = ' '.join(words[start:end]).title()
                        break
                if experience["job_title"]:
                    break

    return experience
