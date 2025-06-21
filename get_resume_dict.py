from pymongo import MongoClient
from datetime import datetime

def get_resume_dictionary():
    """
    Get all resume information as a comprehensive dictionary structure
    Returns: dict - Complete resume data structure
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["resume_ranking_db"]
    collection = db["form_extractions"]
    
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
    
    for doc in docs:
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

def get_resume_by_id(resume_id):
    """
    Get a specific resume by its ID
    Args:
        resume_id (str): The resume ID to search for
    Returns:
        dict: Resume data or None if not found
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["resume_ranking_db"]
    collection = db["form_extractions"]
    
    from bson import ObjectId
    try:
        doc = collection.find_one({"_id": ObjectId(resume_id)})
        if doc:
            return {
                "resume_id": str(doc.get("_id")),
                "jd_id": str(doc.get("jd_id")) if doc.get("jd_id") else None,
                "submitted_at": doc.get("submitted_at").isoformat() if doc.get("submitted_at") else None,
                "resume_filepath": doc.get("resume_filepath"),
                "personal_details": doc.get("personal_details", {}),
                "education": doc.get("education", []),
                "experience": doc.get("experience", []),
                "skills": doc.get("skills", []),
                "projects": doc.get("projects", []),
                "links": doc.get("links", {})
            }
        return None
    except:
        return None

def get_resumes_by_jd_id(jd_id):
    """
    Get all resumes for a specific JD
    Args:
        jd_id (str): The JD ID to search for
    Returns:
        list: List of resume dictionaries
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["resume_ranking_db"]
    collection = db["form_extractions"]
    
    from bson import ObjectId
    try:
        docs = list(collection.find({"jd_id": ObjectId(jd_id)}))
        resumes = []
        
        for doc in docs:
            resume_dict = {
                "resume_id": str(doc.get("_id")),
                "jd_id": str(doc.get("jd_id")) if doc.get("jd_id") else None,
                "submitted_at": doc.get("submitted_at").isoformat() if doc.get("submitted_at") else None,
                "resume_filepath": doc.get("resume_filepath"),
                "personal_details": doc.get("personal_details", {}),
                "education": doc.get("education", []),
                "experience": doc.get("experience", []),
                "skills": doc.get("skills", []),
                "projects": doc.get("projects", []),
                "links": doc.get("links", {})
            }
            resumes.append(resume_dict)
        
        return resumes
    except:
        return []

# Example usage
if __name__ == "__main__":
    # Get all resumes
    all_resumes = get_resume_dictionary()
    print(f"📊 Total resumes found: {all_resumes['metadata']['total_resumes']}")
    
    # Example: Get first resume details
    if all_resumes['resumes']:
        first_resume = all_resumes['resumes'][0]
        print(f"\n📋 First resume:")
        print(f"  Name: {first_resume['personal_details']['name']}")
        print(f"  Email: {first_resume['personal_details']['email']}")
        print(f"  Skills: {len(first_resume['skills'])} skills")
        print(f"  Projects: {len(first_resume['projects'])} projects")
    
    # Example: Get resumes for a specific JD
    if all_resumes['resumes']:
        jd_id = all_resumes['resumes'][0]['jd_id']
        if jd_id:
            jd_resumes = get_resumes_by_jd_id(jd_id)
            print(f"\n🎯 Resumes for JD {jd_id}: {len(jd_resumes)} found") 