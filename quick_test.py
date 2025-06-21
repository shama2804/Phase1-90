import os
from pymongo import MongoClient
from bson import ObjectId

def quick_test():
    """Quick test to check database and files"""
    print("🔍 Quick Test - Database and Files")
    print("=" * 40)
    
    # Test MongoDB connection
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["resume_ranking_db"]
        collection = db["form_extractions"]
        
        # Count documents
        total_docs = collection.count_documents({})
        print(f"📊 Total documents in database: {total_docs}")
        
        # Get unique JD IDs
        jd_ids = collection.distinct("jd_id")
        print(f"📋 Unique JD IDs: {len(jd_ids)}")
        
        for jd_id in jd_ids:
            jd_id_str = str(jd_id)
            print(f"   - {jd_id_str}")
            
            # Count resumes for this JD
            resume_count = collection.count_documents({"jd_id": jd_id})
            print(f"     Resumes: {resume_count}")
            
            # Check if JD PDF exists
            jd_path = f"pdfs/JD_{jd_id_str}_internal.pdf"
            if os.path.exists(jd_path):
                print(f"     ✅ JD PDF: {jd_path}")
            else:
                print(f"     ❌ JD PDF missing: {jd_path}")
        
        # Check resume files
        print("\n📄 Resume Files Check:")
        resumes = list(collection.find({}))
        for resume in resumes:
            filepath = resume.get("resume_filepath")
            name = resume.get("personal_details", {}).get("name", "Unnamed")
            
            if filepath and os.path.exists(filepath):
                print(f"   ✅ {name}: {filepath}")
            else:
                print(f"   ❌ {name}: {filepath} (missing)")
        
        print(f"\n✅ Quick test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test() 