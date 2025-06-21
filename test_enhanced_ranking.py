import os
from pymongo import MongoClient
from bson import ObjectId
from utils.resume_text_utils import extract_text_from_pdf, clean_text
from utils.ranking_utils import rank_resumes_with_reasoning

def test_enhanced_ranking():
    """Test the enhanced ranking system"""
    print("🧪 Testing Enhanced Ranking System")
    print("=" * 50)
    
    # MongoDB setup
    client = MongoClient("mongodb://localhost:27017")
    db = client["resume_ranking_db"]
    collection = db["form_extractions"]
    
    # Test JD ID - replace with actual JD ID from your database
    test_jd_id = "6856ec25ac1437f92281ec1c"  # Replace with actual JD ID
    
    # JD PDF path
    jd_path = f"pdfs/JD_{test_jd_id}_internal.pdf"
    
    if not os.path.exists(jd_path):
        print(f"❌ JD PDF not found: {jd_path}")
        return
    
    # Extract JD text
    jd_text = clean_text(extract_text_from_pdf(jd_path))
    print(f"📄 JD Text Length: {len(jd_text)} characters")
    print(f"📄 JD Preview: {jd_text[:200]}...")
    print()
    
    # Get resumes for this JD
    try:
        resumes = list(collection.find({"jd_id": ObjectId(test_jd_id)}))
        print(f"📊 Found {len(resumes)} resumes for JD {test_jd_id}")
        print()
        
        if not resumes:
            print("❌ No resumes found for this JD")
            return
        
        # Rank each resume
        results = []
        for i, resume in enumerate(resumes, 1):
            name = resume.get("personal_details", {}).get("name", "Unnamed")
            email = resume.get("personal_details", {}).get("email", "")
            filepath = resume.get("resume_filepath")
            
            print(f"👤 {i}. {name} ({email})")
            
            if not filepath or not os.path.exists(filepath):
                print(f"   ❌ Resume file not found: {filepath}")
                continue
            
            # Extract and rank resume
            resume_text = extract_text_from_pdf(filepath)
            clean_resume = clean_text(resume_text)
            
            # Use enhanced ranking
            ranking_result = rank_resumes_with_reasoning(jd_text, clean_resume)
            
            results.append({
                "name": name,
                "email": email,
                "filepath": filepath,
                "score": ranking_result["score"],
                "reasoning": ranking_result["reasoning"],
                "highlights": ranking_result["highlights"]
            })
            
            print(f"   ✅ Score: {ranking_result['score']}")
            print(f"   📄 File: {filepath}")
            print(f"   🧠 Reasoning: {ranking_result['reasoning'][:100]}...")
            print(f"   💡 Highlights: {len(ranking_result['highlights'])} found")
            print()
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        print("🏆 FINAL RANKINGS:")
        print("=" * 40)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - Score: {result['score']}")
            print(f"   Email: {result['email']}")
            print(f"   File: {result['filepath']}")
            print()
        
        print(f"✅ Enhanced ranking completed for JD {test_jd_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_ranking() 