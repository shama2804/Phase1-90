import re

def extract_education(text):
    lines = text.split('\n')
    degree_keywords = [
        # Bachelor's Degrees
        "bachelor of arts", "bachelor of science", "bachelor of commerce", "bachelor of business administration", "bachelor of computer applications",
        "bachelor of fine arts", "bachelor of design", "bachelor of architecture", "bachelor of education", "bachelor of engineering", "bachelor of technology",
        "ba", "b.a", "bsc", "b.sc", "b.com", "bcom", "bba", "bbm", "bca", "bfa", "b.des", "b.arch", "b.ed", "b.e", "be", "b.tech", "btech",

        # Master's Degrees
        "master of arts", "master of science", "master of commerce", "master of business administration", "master of computer applications",
        "master of fine arts", "master of design", "master of engineering", "master of technology", "master of philosophy", "master of laws",
        "ma", "m.a", "msc", "m.sc", "m.com", "mcom", "mba", "mib", "mfa", "m.des", "m.e", "me", "m.tech", "mtech", "ms", "m.s", "mphil", "m.phil", "llm", "ll.m",

        # Doctoral Degrees
        "doctor of philosophy", "phd", "ph.d", "dphil", "dsc", "d.litt", "doctorate",

        # Medical Degrees
        "bachelor of medicine, bachelor of surgery", "mbbs", "bachelor of dental surgery", "bds", "bachelor of ayurvedic medicine and surgery", "bams",
        "bachelor of homeopathic medicine and surgery", "bhms", "doctor of medicine", "md", "master of surgery", "ms", "mds",

        # Pharmacy & Allied Health
        "bachelor of pharmacy", "b.pharm", "bpharm", "master of pharmacy", "m.pharm", "mpharm", "bachelor of physiotherapy", "bpt", "master of physiotherapy", "mpt",

        # Law Degrees
        "bachelor of laws", "llb", "b.l", "master of laws", "llm", "ll.m",

        # Education & Teacher Training
        "diploma in education", "d.ed", "bachelor of physical education", "bped", "master of physical education", "mped", "ttc", "b.ed", "m.ed",

        # Management and Postgrad Diplomas
        "pgdm", "post graduate diploma in management", "pgdba", "pgpm", "pgp", "pgpba", "pgdhrm", "mhrm",

        # Architecture & Planning
        "bachelor of planning", "b.plan", "master of planning", "m.plan",

        # Vocational & Certifications
        "diploma", "advanced diploma", "postgraduate diploma", "certificate course", "vocational course",

        # Finance & Accounting
        "chartered accountant", "ca", "icai", "company secretary", "cs", "cfa", "cpa", "acca", "icwa", "cma", "frm", "actuary",

        # Distance / MOOCs
        "nios", "iti", "polytechnic", "ignou", "iim", "iit", "nptel", "coursera", "edx", "udemy", "google certification"
    ]
    
    education_data = []
    
    # Find education section
    education_section_start = -1
    for i, line in enumerate(lines):
        if re.search(r'\b(education|academic|qualification|degree)\b', line.lower()):
            education_section_start = i
            break
    
    # If no education section found, search through entire text
    search_lines = lines[education_section_start:] if education_section_start != -1 else lines
    
    for i, line in enumerate(search_lines):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Check for degree keywords
        degree_found = None
        for keyword in degree_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', clean_line.lower()):
                degree_found = keyword.upper()
                break
        
        if degree_found:
            # Extract graduation year
            year_match = re.search(r'(20\d{2}|19\d{2})', clean_line)
            graduation_year = year_match.group(1) if year_match else ""
            
            # Look ahead for more year info
            if not graduation_year:
                lookahead = ' '.join([
                    search_lines[i + j].lower() for j in range(1, 4) if i + j < len(search_lines)
                ])
                year_match = re.search(r'(20\d{2}|19\d{2})', lookahead)
                graduation_year = year_match.group(1) if year_match else ""
            
            # Extract CGPA
            cgpa = ""
            # Search in current line and next few lines
            search_area = clean_line + " " + ' '.join([
                search_lines[i + j] for j in range(1, 3) if i + j < len(search_lines)
            ])
            
            # Multiple CGPA patterns
            cgpa_patterns = [
                r'(?:cgpa|gpa)[\s:–-]*([0-9]{1,2}(\.[0-9]+)?)',  # CGPA: 3.8
                r'([0-9]{1,2}(\.[0-9]+)?)\s*(?:cgpa|gpa)',      # 3.8 CGPA
                r'([0-9]{1,2}(\.[0-9]+)?)\s*/\s*[0-9]{1,2}',   # 3.8/4.0
                r'([0-9]{1,2}(\.[0-9]+)?)\s*out\s*of\s*[0-9]{1,2}',  # 3.8 out of 4.0
            ]
            
            for pattern in cgpa_patterns:
                match = re.search(pattern, search_area, re.IGNORECASE)
                if match:
                    cgpa = match.group(1)
                    break
            
            # Extract college/university name
            college = ""
            
            # Method 1: Look for "from" or "at" followed by college name
            college_match = re.search(r'(?:from|at)\s+([A-Z][A-Za-z\s,\.\-&()]{5,})', clean_line, re.IGNORECASE)
            if college_match:
                college = college_match.group(1).strip()
            
            # Method 2: Look at next line if it looks like a college name
            elif i + 1 < len(search_lines):
                next_line = search_lines[i + 1].strip()
                if (5 < len(next_line) < 80 and 
                    not any(d in next_line.lower() for d in degree_keywords) and
                    re.match(r'^[A-Z][A-Za-z\s,\.\-&()]+$', next_line)):
                    college = next_line.title()
            
            # Method 3: Look for common college indicators
            else:
                college_indicators = ['university', 'college', 'institute', 'school', 'academy']
                for indicator in college_indicators:
                    if indicator in clean_line.lower():
                        # Extract text around the indicator
                        parts = clean_line.split()
                        for j, word in enumerate(parts):
                            if indicator in word.lower():
                                # Get words before and after the indicator
                                start = max(0, j - 2)
                                end = min(len(parts), j + 3)
                                college = ' '.join(parts[start:end])
                                break
                        if college:
                            break
            
            # Clean up college name
            if college:
                college = re.sub(r'[^\w\s,\.\-&()]', '', college).strip()
                college = ' '.join(word.capitalize() for word in college.split())
            
            # Create education entry
            education_entry = {
                "degree": degree_found,
                "college": college,
                "graduation": graduation_year,
                "cgpa": cgpa
            }
            
            # Only add if we have meaningful data
            if degree_found and (college or graduation_year):
                education_data.append(education_entry)
    
    # If no education found, return empty list
    if not education_data:
        return []
    
    # Return the most recent/complete education entry
    return [education_data[0]]