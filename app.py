from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from werkzeug.utils import secure_filename
import os
import datetime
from pymongo import MongoClient
from bson import ObjectId, errors
from bson.objectid import ObjectId, InvalidId
from utils.resume_parser import parse_resume
from backend.extract_resume import extract_full_resume
from backend.db_handler import save_to_db
from routes import hr_bp  # Import the HR blueprint

# Flask app setup
flask_app = Flask(__name__)
flask_app.config['UPLOAD_FOLDER'] = 'uploads/'

# Register the HR blueprint
flask_app.register_blueprint(hr_bp, url_prefix='/hr')

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["resume_ranking_db"]
collection = db["form_extractions"]

# Home route (empty form)
@flask_app.route('/')
def index():
    return render_template('form.html', prefill={}, resume_filename="")

# Upload resume and auto-fill form
@flask_app.route('/upload', methods=['POST'])
def upload_resume():
    # Check if resume file was uploaded
    if 'resume' not in request.files:
        return render_template('form.html', form_data={}, resume_filename="", jd_id="", error_msg="Please upload a resume file.")
    
    file = request.files['resume']
    
    # Check if file was selected
    if file.filename == '':
        return render_template('form.html', form_data={}, resume_filename="", jd_id="", error_msg="Please select a resume file.")
    
    jd_id = request.form.get("jd_id")
    filename = secure_filename(file.filename)
    filepath = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    parsed_data = parse_resume(filepath)
    
    # Map parsed data to form fields
    form_prefill = map_parsed_data_to_form(parsed_data)
    
    print("📥 From /upload, sending jd_id to form:", jd_id)
    print("📥 Parsed data mapped to form:", form_prefill)

    return render_template(
        'form.html',
        form_data=form_prefill,
        resume_filename=filename,
        jd_id=jd_id
    )

def map_parsed_data_to_form(parsed_data):
    """Map parsed resume data to form field names"""
    form_data = {}
    
    # Personal details mapping - flat structure
    personal = parsed_data.get('personal_details', {})
    form_data['name'] = personal.get('name', '')
    form_data['email'] = personal.get('email', '')
    form_data['phone'] = personal.get('phone', '')
    form_data['location'] = personal.get('location', '')
    
    # Education mapping - combine into text
    education_list = parsed_data.get('education', [])
    if education_list:
        education_texts = []
        for edu in education_list:
            edu_parts = []
            if edu.get('degree'):
                edu_parts.append(edu['degree'])
            if edu.get('college'):
                edu_parts.append(edu['college'])
            if edu.get('graduation'):
                edu_parts.append(f"Graduated: {edu['graduation']}")
            if edu.get('cgpa'):
                edu_parts.append(f"CGPA: {edu['cgpa']}")
            if edu_parts:
                education_texts.append(' - '.join(edu_parts))
        form_data['education'] = '\n'.join(education_texts)
    else:
        form_data['education'] = ''
    
    # Experience mapping - combine into text
    experience = parsed_data.get('experience', {})
    experience_parts = []
    if experience.get('job_title'):
        experience_parts.append(f"Job Title: {experience['job_title']}")
    if experience.get('current_company'):
        experience_parts.append(f"Company: {experience['current_company']}")
    if experience.get('employment_duration'):
        experience_parts.append(f"Duration: {experience['employment_duration']}")
    if experience.get('job_responsibilities'):
        experience_parts.append(f"Responsibilities: {experience['job_responsibilities']}")
    
    # Add previous employers if available
    previous_employers = experience.get('previous_employers', [])
    if previous_employers:
        for emp in previous_employers:
            emp_parts = []
            if emp.get('company'):
                emp_parts.append(emp['company'])
            if emp.get('duration'):
                emp_parts.append(emp['duration'])
            if emp_parts:
                experience_parts.append(f"Previous: {' - '.join(emp_parts)}")
    
    form_data['experience'] = '\n'.join(experience_parts)
    
    # Skills mapping - convert list to text
    skills_list = parsed_data.get('skills', [])
    form_data['skills'] = ', '.join(skills_list) if skills_list else ''
    
    # Projects mapping - convert list to text
    projects_list = parsed_data.get('projects', [])
    if projects_list:
        project_texts = []
        for proj in projects_list:
            proj_parts = []
            if proj.get('title'):
                proj_parts.append(f"Title: {proj['title']}")
            if proj.get('description'):
                proj_parts.append(f"Description: {proj['description']}")
            if proj.get('tech_stack'):
                proj_parts.append(f"Tech: {proj['tech_stack']}")
            if proj_parts:
                project_texts.append(' | '.join(proj_parts))
        form_data['projects'] = '\n\n'.join(project_texts)
    else:
        form_data['projects'] = ''
    
    # Links mapping - flat structure
    links = parsed_data.get('links', {})
    form_data['linkedin'] = links.get('linkedin', '')
    form_data['github'] = links.get('github', '')
    form_data['portfolio'] = links.get('website', '')
    
    return form_data

# Apply via JD link (GET or POST)
@flask_app.route("/apply/<jd_id>", methods=["GET", "POST"])
def upload_for_jd(jd_id):
    print("🧭 Accessed form via /apply, JD ID is:", jd_id)

    if request.method == 'POST':
        # Check if resume file was uploaded
        if 'resume' not in request.files:
            return render_template('form.html', jd_id=jd_id, prefill={}, error_msg="Please upload a resume file before submitting.")
        
        file = request.files['resume']
        
        # Check if file was selected
        if file.filename == '':
            return render_template('form.html', jd_id=jd_id, prefill={}, error_msg="Please select a resume file before submitting.")
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        parsed_data = parse_resume(filepath)

        final_data = {
            **parsed_data,
            "resume_filepath": filepath,  # ✅ This line is important!
            "jd_id": ObjectId(jd_id),     # ✅ Convert JD ID to ObjectId
            "submitted_at": datetime.datetime.utcnow()
        }

        doc_id = save_to_db(final_data)

        return jsonify({"message": "✅ Resume submitted", "doc_id": str(doc_id)})

    return render_template("form.html", jd_id=jd_id, prefill={})

# Full form submission
@flask_app.route("/submit", methods=["POST"])
def submit():
    jd_id = request.form.get("jd_id")
    print("📌 JD ID received in /submit:", jd_id)

    # ✅ Validate JD ID
    try:
        jd_id = jd_id.strip()
        if len(jd_id) != 24:
            raise InvalidId("❌ JD ID must be exactly 24 characters long")
        jd_object_id = ObjectId(jd_id)
    except Exception as e:
        print("❌ JD ID error:", e)
        return jsonify({"error": "❌ Invalid JD ID"}), 400

    # 📁 Get resume filepath from hidden input
    filename = request.form.get("resume_filename")
    if not filename:
        return render_template('form.html', prefill=request.form, resume_filename="", jd_id=jd_id, error_msg="Resume upload is required. Please upload your resume before submitting.")
    filepath = f"uploads/{filename}" if filename else None
    extracted_info = extract_full_resume(filepath) if filepath else {}
    print("📁 Filename from form:", filename)
    print("📁 Final filepath:", filepath)


    # 📦 Collect final form data
    final_data = {
        "personal_details": {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
        },
        "education": [ {
            "degree": request.form.get("degree"),
            "college": request.form.get("college"),
            "graduation": request.form.get("graduation"),
            "cgpa": request.form.get("cgpa"),
        }],
        "experience": [ {
            "job_title": request.form.get("experience[0][job_title]"),
            "current_company": request.form.get("experience[0][current_company]"),
            "employment_duration": request.form.get("experience[0][employment_duration]"),
            "job_responsibilities": request.form.get("experience[0][job_responsibilities]"),
        }],
        "skills": request.form.getlist("skills[]"),
        "projects": [],
        "links": {
            "linkedin": request.form.get("linkedin"),
            "website": request.form.get("website")
        },
        "resume_filepath": filepath,
        "jd_id": jd_object_id,
        "submitted_at": datetime.datetime.utcnow()
    }

    # 📚 Loop through dynamic projects
    i = 0
    while f"projects[{i}][title]" in request.form:
        final_data["projects"].append({
            "title": request.form.get(f"projects[{i}][title]"),
            "tech_stack": request.form.get(f"projects[{i}][tech_stack]"),
            "description": request.form.get(f"projects[{i}][description]"),
            "duration": request.form.get(f"projects[{i}][duration]")
        })
        i += 1

    # 💾 Save to MongoDB
    doc_id = save_to_db(final_data)
    return jsonify({"message": "✅ Application stored", "doc_id": str(doc_id)})

# Serve uploaded files
@flask_app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory('uploads', filename)

# Serve PDF files
@flask_app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory('pdfs', filename)

# Redirect /jd_form to /hr/jd_form for convenience
@flask_app.route('/jd_form')
def redirect_jd_form():
    return redirect('/hr/jd_form')

# Redirect /hr_dashboard to /hr/hr_dashboard for convenience
@flask_app.route('/hr_dashboard')
def redirect_hr_dashboard():
    return redirect('/hr/hr_dashboard')

__all__ = ['flask_app']

if __name__ == "__main__":
    flask_app.run(debug=True)
