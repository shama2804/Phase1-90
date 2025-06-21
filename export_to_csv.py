from pymongo import MongoClient
import pandas as pd
import json
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["resume_ranking_db"]
collection = db["form_extractions"]

def create_comprehensive_resume_dict():
    """
    Create a comprehensive dictionary structure with all resume information
    """
    print("🔍 Creating comprehensive resume dictionary...")
    
    # Get all documents from the database
    docs = list(collection.find())
    
    if not docs:
        print("❌ No documents found in form_extractions collection")
        return {}
    
    comprehensive_data = {
        "metadata": {
            "total_resumes": len(docs),
            "export_date": datetime.now().isoformat(),
            "database": "resume_ranking_db",
            "collection": "form_extractions"
        },
        "resumes": []
    }
    
    for i, doc in enumerate(docs):
        resume_dict = {
            "resume_id": str(doc.get("_id")),
            "jd_id": str(doc.get("jd_id")) if doc.get("jd_id") else None,
            "submitted_at": doc.get("submitted_at").isoformat() if doc.get("submitted_at") else None,
            "resume_filepath": doc.get("resume_filepath"),
            
            # Personal Details
            "personal_details": {
                "name": doc.get("personal_details", {}).get("name", ""),
                "email": doc.get("personal_details", {}).get("email", ""),
                "phone": doc.get("personal_details", {}).get("phone", "")
            },
            
            # Education
            "education": doc.get("education", []),
            
            # Experience
            "experience": doc.get("experience", []),
            
            # Skills
            "skills": doc.get("skills", []),
            
            # Projects
            "projects": doc.get("projects", []),
            
            # Links
            "links": doc.get("links", {}),
            
            # Raw extracted data (if available)
            "raw_extracted_data": {
                "personal_details": doc.get("personal_details", {}),
                "education": doc.get("education", []),
                "experience": doc.get("experience", []),
                "skills": doc.get("skills", []),
                "projects": doc.get("projects", []),
                "links": doc.get("links", {})
            }
        }
        
        comprehensive_data["resumes"].append(resume_dict)
    
    return comprehensive_data

def save_as_json(data, filename="resume_data.json"):
    """Save the comprehensive data as JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ Comprehensive data saved to {filename}")

def save_as_csv(data, filename="comprehensive_resumes.csv"):
    """Save the comprehensive data as CSV"""
    if not data.get("resumes"):
        print("❌ No resume data to export")
        return
    
    # Flatten the data for CSV export
    flattened_data = []
    for resume in data["resumes"]:
        row = {
            "resume_id": resume["resume_id"],
            "jd_id": resume["jd_id"],
            "submitted_at": resume["submitted_at"],
            "resume_filepath": resume["resume_filepath"],
            
            # Personal details
            "name": resume["personal_details"]["name"],
            "email": resume["personal_details"]["email"],
            "phone": resume["personal_details"]["phone"],
            
            # Education (first entry)
            "degree": resume["education"][0].get("degree", "") if resume["education"] else "",
            "college": resume["education"][0].get("college", "") if resume["education"] else "",
            "graduation": resume["education"][0].get("graduation", "") if resume["education"] else "",
            "cgpa": resume["education"][0].get("cgpa", "") if resume["education"] else "",
            
            # Experience (first entry)
            "job_title": resume["experience"][0].get("job_title", "") if resume["experience"] else "",
            "current_company": resume["experience"][0].get("current_company", "") if resume["experience"] else "",
            "employment_duration": resume["experience"][0].get("employment_duration", "") if resume["experience"] else "",
            "job_responsibilities": resume["experience"][0].get("job_responsibilities", "") if resume["experience"] else "",
            
            # Skills (joined as string)
            "skills": ", ".join(resume["skills"]) if resume["skills"] else "",
            
            # Projects count
            "projects_count": len(resume["projects"]),
            
            # Links
            "linkedin": resume["links"].get("linkedin", ""),
            "website": resume["links"].get("website", "")
        }
        flattened_data.append(row)
    
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"✅ Flattened data saved to {filename}")

def print_summary(data):
    """Print a summary of the comprehensive data"""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE RESUME DATA SUMMARY")
    print("="*60)
    
    metadata = data.get("metadata", {})
    resumes = data.get("resumes", [])
    
    print(f"📈 Total Resumes: {metadata.get('total_resumes', 0)}")
    print(f"📅 Export Date: {metadata.get('export_date', 'N/A')}")
    
    if resumes:
        print(f"\n📋 Sample Resume Structure:")
        sample = resumes[0]
        print(f"  • Resume ID: {sample['resume_id']}")
        print(f"  • JD ID: {sample['jd_id']}")
        print(f"  • Name: {sample['personal_details']['name']}")
        print(f"  • Email: {sample['personal_details']['email']}")
        print(f"  • Education Entries: {len(sample['education'])}")
        print(f"  • Experience Entries: {len(sample['experience'])}")
        print(f"  • Skills Count: {len(sample['skills'])}")
        print(f"  • Projects Count: {len(sample['projects'])}")
        print(f"  • Resume File: {sample['resume_filepath']}")

def main():
    """Main function to create and save comprehensive resume data"""
    print("🚀 Starting comprehensive resume data export...")
    
    # Create comprehensive dictionary
    comprehensive_data = create_comprehensive_resume_dict()
    
    if not comprehensive_data.get("resumes"):
        print("❌ No data to export")
        return
    
    # Print summary
    print_summary(comprehensive_data)
    
    # Save as JSON (full structure)
    save_as_json(comprehensive_data, "comprehensive_resume_data.json")
    
    # Save as CSV (flattened for easy analysis)
    save_as_csv(comprehensive_data, "comprehensive_resumes.csv")
    
    print("\n✅ Export completed successfully!")
    print("📁 Files created:")
    print("   • comprehensive_resume_data.json (full structure)")
    print("   • comprehensive_resumes.csv (flattened for analysis)")

if __name__ == "__main__":
    main()
