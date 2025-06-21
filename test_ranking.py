import os
from pymongo import MongoClient
from bson import ObjectId
from utils.resume_text_utils import extract_text_from_pdf, clean_text
from utils.ranking_utils import rank_resumes

def test_ranking():
    """Test the basic ranking system"""
    print("🧪 Testing Basic Ranking System")
    print("=" * 40)
    
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
            
            # Use basic ranking
            score = rank_resumes(jd_text, clean_resume)
            
            results.append({
                "name": name,
                "email": email,
                "filepath": filepath,
                "score": score
            })
            
            print(f"   ✅ Score: {score}")
            print(f"   📄 File: {filepath}")
            print()
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        print("🏆 FINAL RANKINGS:")
        print("=" * 30)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - Score: {result['score']}")
            print(f"   Email: {result['email']}")
            print()
        
        print(f"✅ Basic ranking completed for JD {test_jd_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ranking() 