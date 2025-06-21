from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import pdfkit
import os

# Blueprint setup
hr_bp = Blueprint("hr", __name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["resume_ranking_db"]
jd_collection = db["jd_extractions"]

# Route: Root test
@hr_bp.route("/hr_test", methods=["GET"])
def root():
    return "🏠 HR Blueprint is working!"


# Route: Show JD form
@hr_bp.route("/jd_form", methods=["GET"])
def jd_form():
    return render_template("jd_form.html")

# Route: View JD preview
@hr_bp.route("/view_jd/<jd_id>", methods=["GET"])
def view_jd(jd_id):
    jd_data = jd_collection.find_one({"_id": ObjectId(jd_id)})
    return render_template("jd_template_internal.html", jd=jd_data)

@hr_bp.route("/submit_jd", methods=["POST"])
def submit_jd():
    # Collect all form data
    data = {
        "job_title": request.form.get("job_title"),
        "employment_type": request.form.get("employment_type"),
        "company_name": request.form.get("company_name"),
        "qualification": request.form.get("qualification"),
        "location": request.form.get("location"),
        "work_mode": request.form.get("work_mode"),
        "about_company": request.form.get("about_company"),
        "job_summary": request.form.get("job_summary"),
        "responsibilities": request.form.get("responsibilities"),
        "experience_skills": request.form.get("experience_skills"),
        "nice_to_have_skills": request.form.get("nice_to_have_skills"),
        "what_to_offer": request.form.get("what_to_offer"),
        "gender": request.form.get("gender"),
        "no_of_candidates": request.form.get("no_of_candidates"),
        "github_required": bool(request.form.get("github_required")),
        "filter_by_reputed_colleges": bool(request.form.get("filter_by_reputed_colleges")),
    }

    if request.form.get("show_reporting_size"):
        data["reporting_size"] = request.form.get("reporting_size")
        data["show_reporting_size"] = True

    if request.form.get("show_stipend"):
        data["stipend"] = request.form.get("stipend")
        data["show_stipend"] = True

    if request.form.get("show_openings"):
        data["no_of_openings"] = request.form.get("no_of_openings")
        data["show_openings"] = True

    if request.form.get("show_certification"):
        data["show_certification"] = True

    # ✅ Save to DB and generate PDFs
    inserted = jd_collection.insert_one(data)
    inserted_id = inserted.inserted_id
    print("✅ JD ID:", str(inserted_id))
    jd_data = jd_collection.find_one({"_id": inserted_id})

    internal_html = render_template("jd_template_internal.html", jd=jd_data)
    public_html = render_template("jd_template_public.html", jd=jd_data)

    internal_path = f"pdfs/JD_{inserted_id}_internal.pdf"
    public_path = f"pdfs/JD_{inserted_id}_public.pdf"

    pdfkit.from_string(internal_html, internal_path)
    pdfkit.from_string(public_html, public_path)

    return f"""
    ✅ JD saved successfully!<br><br>
    🔒 <a href='/pdfs/JD_{inserted_id}_internal.pdf' target='_blank'>Download Internal JD PDF</a><br>
    🌐 <a href='/pdfs/JD_{inserted_id}_public.pdf' target='_blank'>Download Public JD PDF</a><br><br>
    🔍 <a href='{url_for("hr.view_jd", jd_id=inserted_id)}' target='_blank'>Preview JD</a>
    """

@hr_bp.route("/view_resumes/<jd_id>")
def view_resumes(jd_id):
    from app import collection  # Import the resume collection from your main app

    try:
        jd_object_id = ObjectId(jd_id)
    except:
        return "Invalid JD ID", 400

    # ✅ Correctly query by ObjectId
    resumes = list(collection.find({"jd_id": jd_object_id}))
    total_resumes = len(resumes)

    return render_template("submitted_resumes.html", resumes=resumes, jd_id=jd_id, total_resumes=total_resumes)

@hr_bp.route("/rank_resumes/<jd_id>")
def rank_resumes_for_jd(jd_id):
    from app import collection
    import os
    from bson import ObjectId
    from utils.resume_text_utils import extract_text_from_pdf, clean_text
    from utils.ranking_utils import rank_resumes_with_reasoning

    jd_path = f"pdfs/JD_{jd_id}_internal.pdf"

    if not os.path.exists(jd_path):
        return "JD PDF not found", 404

    jd_text = clean_text(extract_text_from_pdf(jd_path))

    resumes = list(collection.find({"jd_id": ObjectId(jd_id)}))
    results = []

    for resume in resumes:
        filepath = resume.get("resume_filepath")
        if not filepath or not os.path.exists(filepath):
            continue

        resume_text = clean_text(extract_text_from_pdf(filepath))
        ranking_result = rank_resumes_with_reasoning(jd_text, resume_text)

        results.append({
            "name": resume.get("personal_details", {}).get("name", "Unnamed"),
            "email": resume.get("personal_details", {}).get("email", ""),
            "filepath": filepath,
            "score": ranking_result["score"],
            "reasoning": ranking_result["reasoning"],
            "highlights": ranking_result["highlights"]
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return render_template("ranked_resumes.html", results=results, jd_id=jd_id)

@hr_bp.route("/hr_dashboard")
def hr_dashboard():
    from app import db
    jd_collection = db["jd_extractions"]
    jds = list(jd_collection.find())
    return render_template("hr_dashboard.html", jds=jds)