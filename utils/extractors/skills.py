import re

# Comprehensive TECH_KEYWORDS
TECH_KEYWORDS = [
    # Programming & Languages
    "python", "java", "c++", "c#", "html", "css", "javascript", "typescript", "r", "sql", "bash", "shell", "powershell",
    "php", "ruby", "go", "rust", "swift", "kotlin", "scala", "perl", "matlab", "sas", "stata", "spss",

    # Web Dev & Frameworks
    "react", "angular", "vue", "node.js", "express", "flask", "django", "fastapi", "spring", "laravel", "asp.net",
    "bootstrap", "tailwind", "sass", "less", "webpack", "babel", "npm", "yarn", "jquery", "ajax",

    # Data Science & ML
    "pandas", "numpy", "scipy", "sklearn", "scikit-learn", "matplotlib", "seaborn", "plotly", "tensorflow", "keras", "pytorch",
    "openai", "huggingface", "nltk", "spacy", "gensim", "xgboost", "lightgbm", "catboost", "mlflow", "optuna",
    "jupyter", "colab", "databricks", "spark", "hadoop", "hive", "pig", "kafka", "airflow", "dbt",

    # Tools & IDEs
    "git", "github", "gitlab", "bitbucket", "vscode", "intellij", "eclipse", "sublime", "vim", "emacs",
    "postman", "insomnia", "swagger", "docker", "kubernetes", "jenkins", "travis", "circleci", "gitlab ci",

    # BI & Analytics
    "excel", "power bi", "tableau", "looker", "qlikview", "qliksense", "superset", "metabase", "grafana",
    "alteryx", "knime", "orange", "rapidminer", "weka", "sas", "spss", "stata", "r studio",

    # UI/UX & Design
    "figma", "canva", "photoshop", "illustrator", "sketch", "xd", "adobe xd", "invision", "zeplin", "framer",
    "webflow", "wix", "wordpress", "elementor", "brizy", "oxygen builder", "shopify", "woocommerce",

    # Databases
    "mysql", "postgresql", "mongodb", "firebase", "sqlite", "oracle", "sql server", "db2", "redis", "elasticsearch",
    "snowflake", "redshift", "bigquery", "dynamodb", "cassandra", "neo4j", "influxdb",

    # DevOps & Cloud
    "aws", "azure", "gcp", "terraform", "ansible", "chef", "puppet", "prometheus", "grafana", "elk", "logstash",
    "nginx", "apache", "tomcat", "iis", "load balancer", "cdn", "vpc", "ec2", "s3", "lambda",

    # Embedded & Electronics
    "arduino", "raspberry pi", "iot", "esp32", "verilog", "vhdl", "proteus", "multisim", "keil", "blynk",
    "gsm", "mqtt", "bluetooth", "wifi", "zigbee", "lora", "rfid", "sensors", "actuators",

    # CAD & Mechanical
    "autocad", "solidworks", "catia", "ansys", "fusion 360", "creo", "hypermesh", "nx", "inventor",
    "matlab", "simulink", "adams", "abaqus", "nastran", "cfd", "fea", "cam", "cnc",

    # Civil & Architecture
    "revit", "staad pro", "etabs", "autocad civil", "arcgis", "qgis", "primavera", "sketchup", "v ray", "lumion",
    "civil 3d", "plaxis", "ms project", "tekla", "safe", "survey", "gps", "gis",

    # Finance & Business
    "tally", "sap", "quickbooks", "xero", "oracle financials", "zoho books", "excel macros", "vba",
    "financial modeling", "equity research", "npv", "irr", "ratio analysis", "stock market", "trading",

    # Healthcare / Life Sciences
    "lims", "bioconductor", "labguru", "meditech", "epic", "cerner", "genbank", "biopython", "pubmed",
    "emr", "ehr", "microscopy", "cytoscape", "pcr", "elisa", "flow cytometry", "genomics",

    # Education & Humanities
    "moodle", "blackboard", "canvas", "turnitin", "mathtype", "latex", "ms teams", "zoom", "google classroom",
    "padlet", "kahoot", "nearpod", "slido", "edmodo", "mentimeter", "socrative", "peardeck",

    # Law & Legal
    "lexisnexis", "manupatra", "case mine", "air", "scconline", "live law", "indiakanoon", "case tracking",
    "legal docs", "contract management", "compliance", "due diligence", "arbitration",

    # Marketing & Content
    "mailchimp", "hootsuite", "buffer", "semrush", "ahrefs", "google ads", "facebook ads", "linkedin ads",
    "canva", "premiere pro", "after effects", "audacity", "obs", "notion", "trello", "asana",

    # Soft Skills & Languages
    "leadership", "team management", "project management", "agile", "scrum", "kanban", "lean", "six sigma",
    "communication", "presentation", "negotiation", "problem solving", "critical thinking", "analytical skills",
    "english", "spanish", "french", "german", "chinese", "japanese", "hindi", "arabic"
]

def extract_skills(text):
    text_lower = text.lower()
    found_skills = set()

    # Extract technical skills
    for kw in TECH_KEYWORDS:
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
            found_skills.add(kw.title())

    # Extract skills from common patterns
    skill_patterns = [
        r'skills?[:\s]+([^.\n]+)',  # "Skills: Python, Java, SQL"
        r'technologies?[:\s]+([^.\n]+)',  # "Technologies: React, Node.js"
        r'tools?[:\s]+([^.\n]+)',  # "Tools: Git, Docker"
        r'languages?[:\s]+([^.\n]+)',  # "Languages: Python, JavaScript"
        r'frameworks?[:\s]+([^.\n]+)',  # "Frameworks: Django, React"
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            # Split by common delimiters
            skills = re.split(r'[,;|•\-\n]', match)
            for skill in skills:
                skill = skill.strip()
                if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
                    # Clean up the skill
                    skill = re.sub(r'[^\w\s\-\.\+#]', '', skill).strip()
                    if skill:
                        found_skills.add(skill.title())

    # Extract skills from bullet points
    bullet_pattern = r'[•\-\*]\s*([^.\n]+)'
    bullet_matches = re.findall(bullet_pattern, text)
    for match in bullet_matches:
        # Check if bullet point contains skill keywords
        for kw in TECH_KEYWORDS:
            if kw.lower() in match.lower():
                found_skills.add(kw.title())

    # Remove duplicates and sort
    return sorted(list(found_skills))
