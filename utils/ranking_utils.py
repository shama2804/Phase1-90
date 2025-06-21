from sentence_transformers import SentenceTransformer, util
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize models
model = SentenceTransformer("all-MiniLM-L6-v2")

# Domain knowledge for semantic expansion
DOMAIN_KNOWLEDGE = {
    # Programming & Tech
    'python': ['programming', 'coding', 'development', 'scripting', 'automation'],
    'java': ['programming', 'object-oriented', 'enterprise', 'android'],
    'javascript': ['web development', 'frontend', 'react', 'node.js', 'typescript'],
    'react': ['frontend', 'ui', 'javascript', 'component-based', 'spa'],
    'angular': ['frontend', 'typescript', 'framework', 'spa'],
    'vue': ['frontend', 'javascript', 'progressive', 'framework'],
    'node.js': ['backend', 'javascript', 'server-side', 'express'],
    'express': ['backend', 'node.js', 'api', 'server'],
    'django': ['python', 'backend', 'web framework', 'mvc'],
    'flask': ['python', 'backend', 'microframework', 'api'],
    'spring': ['java', 'backend', 'enterprise', 'framework'],
    'sql': ['database', 'query', 'relational', 'mysql', 'postgresql'],
    'mongodb': ['database', 'nosql', 'document', 'json'],
    'postgresql': ['database', 'sql', 'relational', 'enterprise'],
    'mysql': ['database', 'sql', 'relational', 'open source'],
    'redis': ['database', 'cache', 'key-value', 'in-memory'],
    'docker': ['containerization', 'devops', 'deployment', 'kubernetes'],
    'kubernetes': ['containerization', 'orchestration', 'devops', 'docker'],
    'aws': ['cloud', 'amazon', 'infrastructure', 'devops'],
    'azure': ['cloud', 'microsoft', 'infrastructure', 'devops'],
    'gcp': ['cloud', 'google', 'infrastructure', 'devops'],
    'git': ['version control', 'github', 'gitlab', 'collaboration'],
    'github': ['git', 'version control', 'collaboration', 'open source'],
    'jenkins': ['ci/cd', 'automation', 'devops', 'pipeline'],
    'machine learning': ['ai', 'artificial intelligence', 'ml', 'data science'],
    'ai': ['artificial intelligence', 'machine learning', 'neural networks'],
    'data science': ['analytics', 'statistics', 'machine learning', 'python'],
    'analytics': ['data analysis', 'insights', 'business intelligence', 'reporting'],
    'api': ['rest', 'graphql', 'integration', 'web services'],
    'rest': ['api', 'http', 'web services', 'json'],
    'graphql': ['api', 'query language', 'schema', 'flexible'],
    'html': ['web', 'frontend', 'markup', 'css'],
    'css': ['styling', 'frontend', 'web', 'design'],
    'bootstrap': ['css', 'frontend', 'responsive', 'ui framework'],
    'tailwind': ['css', 'utility-first', 'frontend', 'responsive'],
    'typescript': ['javascript', 'typed', 'frontend', 'angular'],
    'php': ['backend', 'web', 'wordpress', 'laravel'],
    'c++': ['programming', 'system', 'performance', 'object-oriented'],
    'c#': ['programming', 'microsoft', '.net', 'object-oriented'],
    'scala': ['programming', 'jvm', 'functional', 'spark'],
    'go': ['programming', 'golang', 'concurrent', 'system'],
    'rust': ['programming', 'system', 'memory safety', 'performance'],
    'swift': ['programming', 'ios', 'apple', 'mobile'],
    'kotlin': ['programming', 'android', 'jvm', 'modern'],
    'android': ['mobile', 'kotlin', 'java', 'google'],
    'ios': ['mobile', 'swift', 'apple', 'iphone'],
    'flutter': ['mobile', 'cross-platform', 'dart', 'google'],
    'tensorflow': ['machine learning', 'deep learning', 'neural networks', 'ai'],
    'pytorch': ['machine learning', 'deep learning', 'neural networks', 'ai'],
    'scikit-learn': ['machine learning', 'python', 'sklearn', 'ml'],
    'pandas': ['data analysis', 'python', 'dataframe', 'manipulation'],
    'numpy': ['numerical computing', 'python', 'arrays', 'mathematics'],
    'matplotlib': ['visualization', 'plotting', 'python', 'charts'],
    'selenium': ['automation', 'testing', 'web scraping', 'browser'],
    'junit': ['testing', 'java', 'unit tests', 'tdd'],
    'pytest': ['testing', 'python', 'unit tests', 'tdd'],
    'maven': ['build tool', 'java', 'dependency management', 'gradle'],
    'gradle': ['build tool', 'java', 'dependency management', 'maven'],
    'npm': ['package manager', 'javascript', 'node.js', 'yarn'],
    'yarn': ['package manager', 'javascript', 'node.js', 'npm'],
    
    # Business & Management
    'project management': ['pmp', 'agile', 'scrum', 'leadership', 'planning'],
    'agile': ['scrum', 'kanban', 'iterative', 'sprint', 'project management'],
    'scrum': ['agile', 'sprint', 'product owner', 'scrum master', 'project management'],
    'kanban': ['agile', 'visual', 'workflow', 'lean', 'project management'],
    'lean': ['six sigma', 'process improvement', 'efficiency', 'waste reduction'],
    'six sigma': ['quality management', 'process improvement', 'statistics', 'lean'],
    'business analysis': ['requirements', 'stakeholder', 'process', 'strategy'],
    'strategy': ['planning', 'business', 'competitive', 'market analysis'],
    'marketing': ['digital marketing', 'branding', 'campaigns', 'customer acquisition'],
    'sales': ['business development', 'lead generation', 'customer relationship', 'revenue'],
    'finance': ['accounting', 'budgeting', 'financial analysis', 'investment'],
    'accounting': ['finance', 'bookkeeping', 'audit', 'tax', 'financial reporting'],
    'human resources': ['hr', 'recruitment', 'employee relations', 'talent management'],
    'hr': ['human resources', 'recruitment', 'employee relations', 'talent management'],
    'operations': ['process management', 'efficiency', 'logistics', 'supply chain'],
    'supply chain': ['logistics', 'procurement', 'inventory', 'operations'],
    'logistics': ['supply chain', 'transportation', 'warehousing', 'distribution'],
    'customer service': ['support', 'client relations', 'help desk', 'customer experience'],
    'business development': ['sales', 'partnerships', 'market expansion', 'growth'],
    'product management': ['product owner', 'roadmap', 'user experience', 'strategy'],
    
    # Healthcare & Medical
    'patient care': ['healthcare', 'medical', 'nursing', 'clinical', 'treatment'],
    'medical': ['healthcare', 'clinical', 'patient care', 'diagnosis', 'treatment'],
    'healthcare': ['medical', 'patient care', 'clinical', 'hospital', 'pharmacy'],
    'nursing': ['patient care', 'medical', 'clinical', 'healthcare', 'registered nurse'],
    'pharmacy': ['medication', 'prescription', 'clinical', 'healthcare', 'drug'],
    'clinical': ['medical', 'patient care', 'healthcare', 'diagnosis', 'treatment'],
    'diagnosis': ['medical', 'clinical', 'assessment', 'evaluation', 'healthcare'],
    'treatment': ['medical', 'clinical', 'patient care', 'therapy', 'healthcare'],
    'therapeutic': ['medical', 'treatment', 'clinical', 'therapy', 'healthcare'],
    'medical records': ['epic', 'ehr', 'electronic health records', 'healthcare', 'clinical'],
    'epic': ['medical records', 'ehr', 'healthcare', 'clinical', 'electronic health records'],
    
    # Education & Training
    'teaching': ['education', 'instruction', 'curriculum', 'learning', 'pedagogy'],
    'curriculum': ['education', 'teaching', 'instruction', 'learning', 'syllabus'],
    'instruction': ['teaching', 'education', 'learning', 'pedagogy', 'curriculum'],
    'assessment': ['evaluation', 'testing', 'education', 'learning', 'measurement'],
    'learning': ['education', 'training', 'instruction', 'development', 'knowledge'],
    'training': ['education', 'learning', 'workshop', 'development', 'instruction'],
    'workshop': ['training', 'education', 'learning', 'seminar', 'development'],
    'seminar': ['training', 'education', 'workshop', 'learning', 'presentation'],
    'course development': ['curriculum', 'education', 'instruction', 'learning', 'training'],
    
    # Creative & Design
    'design': ['graphic design', 'ui/ux', 'creative', 'visual', 'artistic'],
    'graphic design': ['design', 'visual', 'creative', 'adobe', 'illustration'],
    'ui/ux': ['user experience', 'user interface', 'design', 'wireframing', 'prototyping'],
    'user experience': ['ui/ux', 'design', 'usability', 'user research', 'wireframing'],
    'creative': ['design', 'artistic', 'visual', 'graphic design', 'innovation'],
    'illustration': ['graphic design', 'visual', 'creative', 'artistic', 'drawing'],
    'photography': ['visual', 'creative', 'camera', 'image editing', 'artistic'],
    'video editing': ['post-production', 'creative', 'visual', 'adobe premiere', 'final cut'],
    'animation': ['motion graphics', 'creative', 'visual', '3d', 'maya'],
    'branding': ['marketing', 'design', 'identity', 'logo', 'visual'],
    
    # Legal & Compliance
    'legal': ['law', 'compliance', 'regulatory', 'litigation', 'contract'],
    'compliance': ['regulatory', 'legal', 'policy', 'governance', 'risk'],
    'regulatory': ['compliance', 'legal', 'policy', 'government', 'standards'],
    'contract': ['legal', 'agreement', 'negotiation', 'terms', 'compliance'],
    'litigation': ['legal', 'court', 'dispute', 'law', 'trial'],
    'intellectual property': ['patent', 'trademark', 'copyright', 'legal', 'ip'],
    
    # Manufacturing & Engineering
    'manufacturing': ['production', 'quality control', 'industrial', 'engineering', 'operations'],
    'quality control': ['manufacturing', 'qc', 'inspection', 'standards', 'testing'],
    'cad': ['autocad', 'design', 'engineering', 'drafting', 'technical drawing'],
    'autocad': ['cad', 'design', 'engineering', 'drafting', 'technical drawing'],
    'solidworks': ['cad', '3d modeling', 'engineering', 'design', 'mechanical'],
    'mechanical engineering': ['engineering', 'mechanical', 'design', 'manufacturing', 'cad'],
    'electrical engineering': ['engineering', 'electrical', 'electronics', 'circuits', 'power'],
    'civil engineering': ['engineering', 'civil', 'construction', 'infrastructure', 'structural'],
    
    # Finance & Banking
    'banking': ['finance', 'financial services', 'investment', 'lending', 'credit'],
    'investment': ['finance', 'banking', 'trading', 'portfolio', 'wealth management'],
    'trading': ['investment', 'finance', 'markets', 'securities', 'trading desk'],
    'risk management': ['finance', 'risk assessment', 'compliance', 'banking', 'investment'],
    'financial analysis': ['finance', 'accounting', 'analysis', 'modeling', 'valuation'],
    'audit': ['accounting', 'finance', 'compliance', 'review', 'internal audit'],
    'tax': ['accounting', 'finance', 'compliance', 'taxation', 'irs'],
    'insurance': ['underwriting', 'claims', 'risk assessment', 'finance', 'actuarial'],
    'underwriting': ['insurance', 'risk assessment', 'finance', 'lending', 'credit'],
    
    # Marketing & Communications
    'digital marketing': ['online marketing', 'social media', 'seo', 'sem', 'content marketing'],
    'social media': ['digital marketing', 'facebook', 'instagram', 'linkedin', 'twitter'],
    'content creation': ['content marketing', 'writing', 'creative', 'digital marketing', 'seo'],
    'seo': ['search engine optimization', 'digital marketing', 'content', 'google', 'organic'],
    'sem': ['search engine marketing', 'ppc', 'google ads', 'digital marketing', 'paid'],
    'public relations': ['pr', 'communications', 'media relations', 'branding', 'marketing'],
    'communications': ['public relations', 'marketing', 'messaging', 'branding', 'pr'],
    'brand management': ['marketing', 'branding', 'identity', 'positioning', 'strategy'],
    
    # Research & Academia
    'research': ['analysis', 'methodology', 'investigation', 'study', 'academic'],
    'analysis': ['research', 'data analysis', 'statistics', 'methodology', 'investigation'],
    'methodology': ['research', 'analysis', 'study design', 'statistics', 'academic'],
    'statistics': ['analysis', 'research', 'data', 'mathematics', 'methodology'],
    'publication': ['research', 'academic', 'journal', 'paper', 'writing'],
    'peer review': ['academic', 'research', 'publication', 'evaluation', 'scholarly'],
    'grant writing': ['research', 'academic', 'funding', 'proposal', 'writing'],
    'academic writing': ['research', 'publication', 'scholarly', 'writing', 'academic']
}

def get_synonyms(word):
    """Get synonyms for a word using WordNet"""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def semantic_expansion(text, max_expansions=50):
    """Expand text with synonyms and domain knowledge"""
    expanded_terms = []
    words = word_tokenize(text.lower())
    
    for word in words:
        if len(word) < 3:
            continue
            
        # Add original word
        expanded_terms.append(word)
        
        # Add synonyms
        synonyms = get_synonyms(word)
        expanded_terms.extend(synonyms[:3])  # Limit synonyms per word
        
        # Add domain knowledge
        if word in DOMAIN_KNOWLEDGE:
            expanded_terms.extend(DOMAIN_KNOWLEDGE[word])
    
    # Remove duplicates and limit total expansions
    unique_terms = list(set(expanded_terms))
    return ' '.join(unique_terms[:max_expansions])

def extract_key_terms_enhanced(text):
    """Enhanced key term extraction with semantic expansion"""
    # Clean and preprocess text
    text_lower = text.lower()
    
    # Basic term extraction
    found_terms = []
    
    # Extract technical/domain-specific terms
    all_domain_terms = []
    for category_terms in DOMAIN_KNOWLEDGE.values():
        all_domain_terms.extend(category_terms)
    
    for term in all_domain_terms:
        if term in text_lower:
            found_terms.append(term)
    
    # Extract experience patterns
    experience_patterns = re.findall(r'(\d+[\+]?\s*(?:years?|yrs?))', text_lower)
    found_terms.extend(experience_patterns)
    
    # Extract education patterns
    education_patterns = re.findall(r'(bachelor|master|phd|b\.?tech|m\.?tech|b\.?e|m\.?e|mba|b\.?a|m\.?a)', text_lower)
    found_terms.extend(education_patterns)
    
    # Extract certifications
    cert_patterns = re.findall(r'(\w+\s+certification|\w+\s+license|\w+\s+certified)', text_lower)
    found_terms.extend(cert_patterns)
    
    # Extract important nouns using NLTK
    try:
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text_lower)
        important_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Find frequent important words
        word_freq = Counter(important_words)
        frequent_words = [word for word, count in word_freq.most_common(20) if count >= 2]
        found_terms.extend(frequent_words[:10])
        
    except Exception:
        pass
    
    # Extract industry-specific terms
    capitalized_terms = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text)
    common_words = {'The', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By', 'From', 'About', 'This', 'That', 'These', 'Those'}
    industry_terms = [term for term in capitalized_terms if term not in common_words and len(term) > 2]
    found_terms.extend(industry_terms[:5])
    
    return list(set(found_terms))

def compute_tfidf_similarity(text1, text2):
    """Compute TF-IDF similarity between two texts"""
    try:
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # Combine texts for fitting
        combined_texts = [text1, text2]
        tfidf_matrix = vectorizer.fit_transform(combined_texts)
        
        # Compute cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except Exception:
        return 0.0

def compute_semantic_similarity(text1, text2):
    """Compute semantic similarity using Sentence-BERT"""
    try:
        # Encode texts
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity = util.pytorch_cos_sim(embeddings1, embeddings2).item()
        return similarity
    except Exception:
        return 0.0

def scale_score(raw_score, min_val=0.0, max_val=0.4, power=1.2):
    # Clip to [min_val, max_val]
    clipped = max(min(raw_score, max_val), min_val)
    # Normalize to 0-1
    norm = (clipped - min_val) / (max_val - min_val) if max_val > min_val else 0.0
    # Nonlinear boost (power > 1 makes high scores higher)
    boosted = norm ** power
    # No shift: lowest is 0, highest is 1
    return round(boosted, 4)

def compute_enhanced_similarity(jd_text, resume_text):
    """Compute enhanced similarity using multiple approaches, with score scaling"""
    # 1. Semantic expansion
    jd_expanded = semantic_expansion(jd_text)
    resume_expanded = semantic_expansion(resume_text)
    # 2. TF-IDF similarity on expanded texts
    tfidf_score = compute_tfidf_similarity(jd_expanded, resume_expanded)
    # 3. Semantic similarity using Sentence-BERT
    semantic_score = compute_semantic_similarity(jd_text, resume_text)
    # 4. Key term overlap
    jd_terms = extract_key_terms_enhanced(jd_text)
    resume_terms = extract_key_terms_enhanced(resume_text)
    common_terms = set(jd_terms) & set(resume_terms)
    if len(jd_terms) > 0 and len(resume_terms) > 0:
        term_overlap_score = len(common_terms) / max(len(jd_terms), len(resume_terms))
    else:
        term_overlap_score = 0.0
    # 5. Weighted combination (raw)
    final_score_raw = (0.5 * semantic_score) + (0.3 * tfidf_score) + (0.2 * term_overlap_score)
    # 6. Scale all scores for more intuitive output
    final_score = scale_score(final_score_raw)
    semantic_score_scaled = scale_score(semantic_score)
    tfidf_score_scaled = scale_score(tfidf_score)
    term_overlap_score_scaled = scale_score(term_overlap_score, min_val=0.0, max_val=1.0, power=1.2)
    return {
        'final_score': final_score,
        'semantic_score': semantic_score_scaled,
        'tfidf_score': tfidf_score_scaled,
        'term_overlap_score': term_overlap_score_scaled,
        'common_terms': list(common_terms)
    }

def find_matching_highlights_enhanced(jd_text, resume_text):
    """Enhanced matching highlights with semantic expansion"""
    jd_terms = extract_key_terms_enhanced(jd_text)
    resume_terms = extract_key_terms_enhanced(resume_text)
    
    # Find common terms
    common_terms = list(set(jd_terms) & set(resume_terms))
    
    # Extract sentences containing matching terms
    highlights = []
    jd_sentences = sent_tokenize(jd_text)
    resume_sentences = sent_tokenize(resume_text)
    
    for term in common_terms[:10]:
        # Find JD sentences with this term
        jd_matches = [s.strip() for s in jd_sentences if term.lower() in s.lower() and len(s.strip()) > 20]
        # Find resume sentences with this term
        resume_matches = [s.strip() for s in resume_sentences if term.lower() in s.lower() and len(s.strip()) > 20]
        
        if jd_matches and resume_matches:
            highlights.append({
                'term': term,
                'jd_context': jd_matches[0][:150] + "..." if len(jd_matches[0]) > 150 else jd_matches[0],
                'resume_context': resume_matches[0][:150] + "..." if len(resume_matches[0]) > 150 else resume_matches[0]
            })
    
    return highlights[:5]

def generate_reasoning_enhanced(jd_text, resume_text, similarity_result):
    """Generate enhanced reasoning with detailed breakdown"""
    jd_terms = extract_key_terms_enhanced(jd_text)
    resume_terms = extract_key_terms_enhanced(resume_text)
    
    common_terms = similarity_result['common_terms']
    final_score = similarity_result['final_score']
    semantic_score = similarity_result['semantic_score']
    tfidf_score = similarity_result['tfidf_score']
    term_overlap_score = similarity_result['term_overlap_score']
    
    reasoning = []
    
    # Overall assessment
    if final_score >= 0.8:
        reasoning.append("Excellent semantic match with high conceptual alignment")
    elif final_score >= 0.6:
        reasoning.append("Strong semantic match with good domain relevance")
    elif final_score >= 0.4:
        reasoning.append("Moderate semantic match with some relevant overlap")
    else:
        reasoning.append("Low semantic match with limited conceptual alignment")
    
    # Detailed breakdown
    reasoning.append(f"Semantic similarity: {semantic_score:.3f} (SBERT embeddings)")
    reasoning.append(f"TF-IDF similarity: {tfidf_score:.3f} (expanded terms)")
    reasoning.append(f"Term overlap: {term_overlap_score:.3f} ({len(common_terms)} common terms)")
    
    if common_terms:
        top_matches = common_terms[:5]
        reasoning.append(f"Key matches: {', '.join(top_matches)}")
    
    # Industry insights
    if term_overlap_score > 0.5:
        reasoning.append("Strong domain knowledge alignment detected")
    elif term_overlap_score > 0.25:
        reasoning.append("Moderate domain relevance")
    else:
        reasoning.append("Limited domain overlap")
    
    return " | ".join(reasoning)

def rank_resumes_with_reasoning(jd_text, resume_text):
    """Enhanced ranking function with advanced semantic analysis"""
    if not jd_text or not resume_text:
        return {
            'score': 0.0,
            'reasoning': "Unable to process empty text",
            'highlights': []
        }
    
    # Compute enhanced similarity
    similarity_result = compute_enhanced_similarity(jd_text, resume_text)
    
    # Generate reasoning
    reasoning = generate_reasoning_enhanced(jd_text, resume_text, similarity_result)
    
    # Find highlights
    highlights = find_matching_highlights_enhanced(jd_text, resume_text)
    
    return {
        'score': similarity_result['final_score'],
        'reasoning': reasoning,
        'highlights': highlights,
        'detailed_scores': {
            'semantic': similarity_result['semantic_score'],
            'tfidf': similarity_result['tfidf_score'],
            'term_overlap': similarity_result['term_overlap_score']
        }
    }

# Keep original function for backward compatibility
def rank_resumes(jd_text, resume_text):
    """Original ranking function for backward compatibility"""
    if not jd_text or not resume_text:
        return 0.0
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    score = util.pytorch_cos_sim(jd_emb, resume_emb).item()
    return round(score, 4) 