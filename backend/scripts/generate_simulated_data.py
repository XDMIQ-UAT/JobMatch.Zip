#!/usr/bin/env python3
"""
Generate 1000 simulated job opportunities and candidate profiles for testing/demo.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Job titles by field
JOB_TITLES = {
    'it': [
        'Senior Software Engineer', 'Full Stack Developer', 'Backend Engineer', 'Frontend Developer',
        'DevOps Engineer', 'Cloud Architect', 'Data Engineer', 'Machine Learning Engineer',
        'AI Engineer', 'Cybersecurity Specialist', 'IT Support Specialist', 'Systems Administrator',
        'Database Administrator', 'QA Engineer', 'Mobile Developer', 'React Developer',
        'Python Developer', 'Node.js Developer', 'Java Developer', 'Go Developer'
    ],
    'healthcare': [
        'Registered Nurse', 'Physician Assistant', 'Physical Therapist', 'Occupational Therapist',
        'Medical Assistant', 'Pharmacy Technician', 'Radiology Technician', 'Lab Technician',
        'Healthcare Administrator', 'Medical Coder', 'Nurse Practitioner', 'Clinical Research Coordinator',
        'Health Information Manager', 'Medical Device Sales', 'Telehealth Coordinator'
    ],
    'education': [
        'Elementary School Teacher', 'High School Teacher', 'College Professor', 'Curriculum Developer',
        'Instructional Designer', 'Education Administrator', 'Tutor', 'Librarian',
        'School Counselor', 'Special Education Teacher', 'ESL Teacher', 'Training Specialist'
    ],
    'business': [
        'Business Analyst', 'Financial Analyst', 'Accountant', 'Project Manager',
        'Operations Manager', 'HR Manager', 'Marketing Manager', 'Sales Manager',
        'Product Manager', 'Business Consultant', 'Operations Analyst', 'Supply Chain Manager'
    ],
    'engineering': [
        'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer', 'Chemical Engineer',
        'Aerospace Engineer', 'Structural Engineer', 'Environmental Engineer', 'Industrial Engineer',
        'Biomedical Engineer', 'Software Engineer', 'Systems Engineer', 'Quality Engineer'
    ],
    'sales': [
        'Sales Representative', 'Account Executive', 'Business Development Manager', 'Sales Manager',
        'Inside Sales Representative', 'Outside Sales Representative', 'Territory Sales Manager',
        'Key Account Manager', 'Sales Engineer', 'Retail Sales Associate'
    ],
    'creative': [
        'Graphic Designer', 'UI/UX Designer', 'Web Designer', 'Product Designer',
        'Content Writer', 'Copywriter', 'Video Editor', 'Photographer', 'Illustrator',
        'Marketing Designer', 'Brand Designer', 'Motion Graphics Designer'
    ],
    'government': [
        'Policy Analyst', 'Program Manager', 'Administrative Assistant', 'Compliance Officer',
        'Grant Writer', 'Public Relations Specialist', 'City Planner', 'Budget Analyst',
        'Human Resources Specialist', 'IT Specialist', 'Data Analyst', 'Research Analyst'
    ],
    'legal': [
        'Attorney', 'Paralegal', 'Legal Assistant', 'Compliance Specialist',
        'Contract Administrator', 'Legal Researcher', 'Court Reporter', 'Legal Secretary'
    ],
    'science': [
        'Research Scientist', 'Lab Technician', 'Data Scientist', 'Biostatistician',
        'Environmental Scientist', 'Chemist', 'Biologist', 'Research Analyst',
        'Quality Control Analyst', 'Clinical Research Associate'
    ],
    'service': [
        'Customer Service Representative', 'Restaurant Manager', 'Hotel Manager',
        'Retail Store Manager', 'Food Service Worker', 'Event Coordinator',
        'Hospitality Manager', 'Concierge', 'Server', 'Barista'
    ]
}

# Companies
COMPANIES = [
    'TechCorp', 'DataSystems Inc', 'CloudVentures', 'InnovateLabs', 'Digital Solutions',
    'CodeCrafters', 'NextGen Technologies', 'FutureWorks', 'SmartSystems', 'AgileDev',
    'HealthTech Solutions', 'MedCare Systems', 'Wellness Corp', 'CarePlus', 'HealthFirst',
    'EduTech Innovations', 'LearnSmart', 'KnowledgeBase', 'Academy Plus', 'EduConnect',
    'Business Partners', 'Strategy Group', 'Consulting Pro', 'Growth Partners', 'Business Solutions',
    'Engineering Works', 'BuildCorp', 'DesignBuild', 'Structural Solutions', 'Engineering Pro',
    'SalesForce Inc', 'Revenue Partners', 'Growth Co', 'Sales Solutions', 'Market Leaders',
    'Creative Studio', 'Design House', 'Artisan Works', 'Creative Agency', 'Design Lab',
    'Public Services', 'Government Solutions', 'Civic Tech', 'Public Works', 'Community Services',
    'Legal Partners', 'Law Group', 'Legal Solutions', 'Justice Works', 'Legal Services',
    'Research Labs', 'Science Corp', 'Lab Systems', 'Research Institute', 'Science Works',
    'Service Pro', 'Hospitality Group', 'Service Solutions', 'Customer Care', 'Service Excellence'
]

# Locations
LOCATIONS = [
    'San Francisco, CA', 'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Seattle, WA',
    'Austin, TX', 'Boston, MA', 'Denver, CO', 'Atlanta, GA', 'Miami, FL',
    'Portland, OR', 'Nashville, TN', 'Phoenix, AZ', 'Dallas, TX', 'Houston, TX',
    'Remote', 'Remote (US)', 'Remote (Global)', 'Hybrid - San Francisco', 'Hybrid - New York',
    'Hybrid - Los Angeles', 'Hybrid - Chicago', 'Hybrid - Seattle', 'Hybrid - Austin'
]

# Skills pool
ALL_SKILLS = [
    # IT Skills
    'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++', 'C#', 'Ruby',
    'React', 'Vue.js', 'Angular', 'Node.js', 'Express', 'FastAPI', 'Django', 'Flask',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
    'Git', 'CI/CD', 'Terraform', 'Ansible', 'Linux', 'Bash', 'PowerShell',
    'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Science', 'SQL', 'Pandas', 'NumPy',
    'Cybersecurity', 'Network Security', 'Penetration Testing', 'SIEM', 'Firewall',
    # Healthcare Skills
    'Patient Care', 'EHR Systems', 'HIPAA Compliance', 'Medical Coding', 'Telemedicine',
    'Clinical Research', 'Pharmacy', 'Nursing', 'Physical Therapy', 'Medical Records',
    # Education Skills
    'Curriculum Design', 'Instructional Design', 'LMS', 'E-Learning', 'Teaching',
    'Student Assessment', 'Classroom Management', 'Educational Technology',
    # Business Skills
    'Project Management', 'Agile', 'Scrum', 'Business Analysis', 'Financial Analysis',
    'Excel', 'PowerPoint', 'Data Analysis', 'Stakeholder Management', 'Process Improvement',
    # Engineering Skills
    'CAD', 'AutoCAD', 'SolidWorks', 'MATLAB', 'Structural Analysis', 'Project Planning',
    'Quality Control', 'Safety Management', 'Blueprint Reading',
    # Sales Skills
    'Sales', 'CRM', 'Salesforce', 'Lead Generation', 'Negotiation', 'Account Management',
    # Creative Skills
    'Figma', 'Adobe Creative Suite', 'UI Design', 'UX Design', 'Graphic Design',
    'Content Writing', 'Copywriting', 'Video Editing', 'Photography',
    # General Skills
    'Communication', 'Problem Solving', 'Teamwork', 'Leadership', 'Time Management',
    'Critical Thinking', 'Adaptability', 'Collaboration', 'Presentation Skills'
]

# Employment types
EMPLOYMENT_TYPES = ['Full-time', 'Part-time', 'Contract', 'Temporary', 'Internship']

# Job descriptions templates
DESCRIPTION_TEMPLATES = {
    'it': [
        "We're looking for a {title} to join our growing team. You'll work on {project_type} using modern technologies like {tech_stack}. This role offers {benefits}.",
        "Join our {company_type} team as a {title}. You'll be responsible for {responsibilities}. We value {values} and offer {benefits}.",
        "Seeking an experienced {title} to help build {project_type}. The ideal candidate has {years} years of experience with {tech_stack}."
    ],
    'healthcare': [
        "We're seeking a {title} to provide {care_type} to our patients. This role requires {certifications} and offers {benefits}.",
        "Join our healthcare team as a {title}. You'll work in a {setting} environment providing {care_type}. We offer {benefits}."
    ],
    'education': [
        "We're looking for a {title} to {teaching_type} students. This role involves {responsibilities} and offers {benefits}.",
        "Join our educational institution as a {title}. You'll be responsible for {responsibilities} in a {environment} setting."
    ]
}

def generate_job_opportunity(field: str, index: int) -> Dict[str, Any]:
    """Generate a single job opportunity."""
    job_titles = JOB_TITLES.get(field, JOB_TITLES['it'])
    title = random.choice(job_titles)
    company = random.choice(COMPANIES)
    location = random.choice(LOCATIONS)
    is_remote = location.startswith('Remote') or location.startswith('Hybrid')
    
    # Generate skills (3-8 skills per job)
    num_skills = random.randint(3, 8)
    skills = random.sample(ALL_SKILLS, num_skills)
    
    # Generate salary range based on field
    base_salaries = {
        'it': (80000, 200000),
        'healthcare': (50000, 150000),
        'education': (40000, 100000),
        'business': (60000, 180000),
        'engineering': (70000, 160000),
        'sales': (40000, 120000),
        'creative': (45000, 130000),
        'government': (50000, 140000),
        'legal': (60000, 200000),
        'science': (55000, 150000),
        'service': (30000, 80000)
    }
    min_sal, max_sal = base_salaries.get(field, (50000, 120000))
    salary_min = random.randint(min_sal, max_sal - 20000)
    salary_max = salary_min + random.randint(20000, 50000)
    
    # Generate description
    description = f"We are seeking a {title} to join our team at {company}. "
    description += f"This position is located in {location}. "
    description += f"The ideal candidate will have experience with {', '.join(skills[:3])}. "
    description += f"Responsibilities include working on challenging projects, collaborating with cross-functional teams, "
    description += f"and contributing to our mission of excellence. "
    description += f"We offer competitive compensation ({salary_min:,}-{salary_max:,}), comprehensive benefits, "
    description += f"and opportunities for professional growth."
    
    # Generate posted date (within last 90 days)
    days_ago = random.randint(0, 90)
    posted_date = datetime.now() - timedelta(days=days_ago)
    
    return {
        'id': str(uuid.uuid4()),
        'title': title,
        'company': company,
        'location': location,
        'isRemote': is_remote,
        'description': description,
        'skills': skills,
        'requirements': skills[:5],  # Top 5 as requirements
        'salaryMin': salary_min,
        'salaryMax': salary_max,
        'employmentType': random.choice(EMPLOYMENT_TYPES),
        'postedDate': posted_date.isoformat(),
        'createdAt': posted_date.isoformat(),
        'isActive': True,
        'field': field
    }

def generate_candidate_profile(index: int) -> Dict[str, Any]:
    """Generate a single candidate profile."""
    # Select a field
    field = random.choice(list(JOB_TITLES.keys()))
    
    # Generate skills (5-15 skills per candidate)
    num_skills = random.randint(5, 15)
    skills = random.sample(ALL_SKILLS, num_skills)
    
    # Generate location
    location = random.choice(LOCATIONS)
    
    # Generate experience (0-20 years)
    years_experience = random.randint(0, 20)
    
    # Generate summary
    summary = f"Experienced professional with {years_experience} years in {field}. "
    summary += f"Skilled in {', '.join(skills[:5])}. "
    summary += f"Looking for opportunities to {random.choice(['grow', 'contribute', 'innovate', 'lead', 'collaborate'])}."
    
    # Generate work experience
    experience = []
    if years_experience > 0:
        num_jobs = min(5, max(1, years_experience // 3))
        for i in range(num_jobs):
            job_years = random.randint(1, min(5, years_experience // num_jobs + 1))
            experience.append({
                'title': random.choice(JOB_TITLES.get(field, JOB_TITLES['it'])),
                'company': random.choice(COMPANIES),
                'duration': f"{job_years} years",
                'description': f"Worked on {random.choice(['projects', 'initiatives', 'teams', 'systems'])}"
            })
    
    # Generate education
    education_levels = ['High School', 'Associate', "Bachelor's", "Master's", 'PhD']
    education = [{
        'degree': random.choice(education_levels),
        'field': random.choice(['Computer Science', 'Engineering', 'Business', 'Healthcare', 'Education', 'Arts', 'Science']),
        'year': str(random.randint(1990, 2024))
    }]
    
    return {
        'id': str(uuid.uuid4()),
        'anonymousId': str(uuid.uuid4()),
        'skills': skills,
        'location': location,
        'summary': summary,
        'experience': experience,
        'education': education,
        'yearsExperience': years_experience,
        'field': field,
        'preferences': {
            'workType': random.choice(['remote', 'hybrid', 'onsite']),
            'salaryMin': random.randint(50000, 150000),
            'employmentType': random.choice(EMPLOYMENT_TYPES)
        },
        'createdAt': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
    }

def generate_all_data():
    """Generate 1000 opportunities and 1000 profiles."""
    fields = list(JOB_TITLES.keys())
    
    # Generate 1000 job opportunities
    opportunities = []
    for i in range(1000):
        field = random.choice(fields)
        opportunity = generate_job_opportunity(field, i)
        opportunities.append(opportunity)
    
    # Generate 1000 candidate profiles
    profiles = []
    for i in range(1000):
        profile = generate_candidate_profile(i)
        profiles.append(profile)
    
    return opportunities, profiles

def main():
    """Main function to generate and save data."""
    print("Generating 1000 job opportunities and 1000 candidate profiles...")
    
    opportunities, profiles = generate_all_data()
    
    # Save opportunities
    opportunities_file = 'backend/data/simulated_opportunities.json'
    with open(opportunities_file, 'w') as f:
        json.dump(opportunities, f, indent=2)
    print(f"✅ Saved {len(opportunities)} opportunities to {opportunities_file}")
    
    # Save profiles
    profiles_file = 'backend/data/simulated_profiles.json'
    with open(profiles_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    print(f"✅ Saved {len(profiles)} profiles to {profiles_file}")
    
    # Generate summary
    print("\n📊 Summary:")
    print(f"  • Opportunities: {len(opportunities)}")
    print(f"  • Profiles: {len(profiles)}")
    
    # Field distribution
    field_dist_opps = {}
    field_dist_profs = {}
    for opp in opportunities:
        field_dist_opps[opp['field']] = field_dist_opps.get(opp['field'], 0) + 1
    for prof in profiles:
        field_dist_profs[prof['field']] = field_dist_profs.get(prof['field'], 0) + 1
    
    print("\n📈 Opportunities by field:")
    for field, count in sorted(field_dist_opps.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {field}: {count}")
    
    print("\n👥 Profiles by field:")
    for field, count in sorted(field_dist_profs.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {field}: {count}")
    
    # Remote vs Onsite
    remote_count = sum(1 for opp in opportunities if opp['isRemote'])
    print(f"\n🌍 Remote opportunities: {remote_count} ({remote_count/len(opportunities)*100:.1f}%)")
    
    print("\n✅ Data generation complete!")

if __name__ == '__main__':
    import os
    os.makedirs('backend/data', exist_ok=True)
    main()

