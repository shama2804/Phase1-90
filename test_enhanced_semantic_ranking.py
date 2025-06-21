import os
from pymongo import MongoClient
from bson import ObjectId
from utils.resume_text_utils import extract_text_from_pdf, clean_text
from utils.ranking_utils import rank_resumes_with_reasoning

def test_enhanced_semantic_ranking():
    """Test the enhanced semantic ranking system"""
    print("🧪 Testing Enhanced Semantic Ranking System")
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
                "highlights": ranking_result["highlights"],
                "detailed_scores": ranking_result.get("detailed_scores", {})
            })
            
            print(f"   ✅ Score: {ranking_result['score']}")
            print(f"   📄 File: {filepath}")
            print(f"   🧠 Reasoning: {ranking_result['reasoning'][:100]}...")
            print(f"   💡 Highlights: {len(ranking_result['highlights'])} found")
            if ranking_result.get("detailed_scores"):
                scores = ranking_result["detailed_scores"]
                print(f"   📊 Detailed Scores:")
                print(f"      - Semantic: {scores.get('semantic', 0):.3f}")
                print(f"      - TF-IDF: {scores.get('tfidf', 0):.3f}")
                print(f"      - Term Overlap: {scores.get('term_overlap', 0):.3f}")
            print()
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        print("🏆 FINAL RANKINGS:")
        print("=" * 50)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - Score: {result['score']}")
            print(f"   Email: {result['email']}")
            print(f"   File: {result['filepath']}")
            print(f"   Reasoning: {result['reasoning'][:150]}...")
            print()
        
        print(f"✅ Enhanced semantic ranking completed for JD {test_jd_id}")
        
        # Test specific ranking components
        print("\n🔬 Testing Individual Ranking Components:")
        print("-" * 40)
        
        if results:
            test_resume = results[0]
            print(f"Testing with top resume: {test_resume['name']}")
            
            # Test semantic similarity
            from utils.ranking_utils import compute_semantic_similarity
            semantic_score = compute_semantic_similarity(jd_text, clean_resume)
            print(f"   Semantic Similarity: {semantic_score:.3f}")
            
            # Test TF-IDF similarity
            from utils.ranking_utils import compute_tfidf_similarity
            tfidf_score = compute_tfidf_similarity(jd_text, clean_resume)
            print(f"   TF-IDF Similarity: {tfidf_score:.3f}")
            
            # Test term overlap
            from utils.ranking_utils import compute_term_overlap
            overlap_score = compute_term_overlap(jd_text, clean_resume)
            print(f"   Term Overlap: {overlap_score:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_ranking_with_different_jds():
    """Test ranking with different JD types"""
    print("\n🧪 Testing Ranking with Different JD Types")
    print("=" * 50)
    
    # Test different JD IDs
    test_jds = [
        "6856ec25ac1437f92281ec1c",  # Replace with actual JD IDs
        # Add more JD IDs here
    ]
    
    for jd_id in test_jds:
        print(f"\n🎯 Testing JD: {jd_id}")
        print("-" * 30)
        
        jd_path = f"pdfs/JD_{jd_id}_internal.pdf"
        if os.path.exists(jd_path):
            jd_text = clean_text(extract_text_from_pdf(jd_path))
            print(f"   JD Type: {jd_text[:100]}...")
            
            # Get resumes for this JD
            client = MongoClient("mongodb://localhost:27017")
            db = client["resume_ranking_db"]
            collection = db["form_extractions"]
            
            resumes = list(collection.find({"jd_id": ObjectId(jd_id)}))
            print(f"   Resumes found: {len(resumes)}")
            
            if resumes:
                # Test ranking for first resume
                resume = resumes[0]
                filepath = resume.get("resume_filepath")
                if filepath and os.path.exists(filepath):
                    resume_text = clean_text(extract_text_from_pdf(filepath))
                    ranking_result = rank_resumes_with_reasoning(jd_text, resume_text)
                    print(f"   Top score: {ranking_result['score']}")
        else:
            print(f"   ❌ JD PDF not found")

if __name__ == "__main__":
    test_enhanced_semantic_ranking()
    test_ranking_with_different_jds() 