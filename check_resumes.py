import os
from pymongo import MongoClient
from bson import ObjectId

def check_resumes():
    """Check all resumes in the database"""
    print("🔍 Checking All Resumes")
    print("=" * 40)
    
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["resume_ranking_db"]
        collection = db["form_extractions"]
        
        # Get all resumes
        resumes = list(collection.find({}))
        print(f"📊 Total resumes found: {len(resumes)}")
        print()
        
        for i, resume in enumerate(resumes, 1):
            print(f"👤 Resume {i}:")
            
            # Basic info
            name = resume.get("personal_details", {}).get("name", "Unnamed")
            email = resume.get("personal_details", {}).get("email", "")
            phone = resume.get("personal_details", {}).get("phone", "")
            jd_id = resume.get("jd_id")
            
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   JD ID: {jd_id}")
            
            # File info
            filepath = resume.get("resume_filepath")
            if filepath:
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"   ✅ File: {filepath} ({file_size} bytes)")
                else:
                    print(f"   ❌ File missing: {filepath}")
            else:
                print(f"   ❌ No filepath stored")
            
            # Check extracted data
            personal = resume.get("personal_details", {})
            education = resume.get("education", [])
            experience = resume.get("experience", [])
            skills = resume.get("skills", [])
            projects = resume.get("projects", [])
            links = resume.get("links", {})
            
            print(f"   📝 Extracted Data:")
            print(f"      - Personal: {len(personal)} fields")
            print(f"      - Education: {len(education)} entries")
            print(f"      - Experience: {len(experience)} entries")
            print(f"      - Skills: {len(skills)} skills")
            print(f"      - Projects: {len(projects)} projects")
            print(f"      - Links: {len(links)} links")
            
            print()
        
        # Summary
        print("📈 SUMMARY:")
        print("-" * 20)
        
        # Count by JD
        jd_counts = {}
        for resume in resumes:
            jd_id = resume.get("jd_id")
            if jd_id:
                jd_str = str(jd_id)
                jd_counts[jd_str] = jd_counts.get(jd_str, 0) + 1
        
        for jd_id, count in jd_counts.items():
            print(f"   JD {jd_id}: {count} resumes")
        
        # File status
        files_exist = sum(1 for r in resumes if r.get("resume_filepath") and os.path.exists(r.get("resume_filepath")))
        files_missing = len(resumes) - files_exist
        
        print(f"   Files exist: {files_exist}")
        print(f"   Files missing: {files_missing}")
        
        print(f"\n✅ Resume check completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_resumes() 