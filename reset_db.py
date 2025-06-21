from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["resume_ranking_db"]

# Delete all resumes
form_result = db["form_extractions"].delete_many({})
# Delete all JDs
jd_result = db["jd_extractions"].delete_many({})

print(f"✅ Deleted {form_result.deleted_count} resumes from form_extractions.")
print(f"✅ Deleted {jd_result.deleted_count} JDs from jd_extractions.")

# Delete export files
for fname in [
    "comprehensive_resume_data.json",
    "comprehensive_resumes.csv",
    "submissions.csv"
]:
    if os.path.exists(fname):
        os.remove(fname)
        print(f"🗑️ Deleted {fname}")
    else:
        print(f"Not found: {fname}") 