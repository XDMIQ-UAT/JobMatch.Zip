#!/usr/bin/env python3
"""
Generate simulated jobs and candidate profiles using Ollama.
Designed to run overnight to populate the database.
"""
import os
import sys
import json
import time
import random
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.database.models import Base, AnonymousUser, LLCProfile, JobPosting
from backend.database.connection import get_db, init_db

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
# Support both localhost and Docker service names
_db_host = os.getenv("DB_HOST", "localhost")
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://jobfinder:jobfinder@{_db_host}:5432/jobfinder")

# Rate limiting
REQUESTS_PER_MINUTE = 10
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# Generation limits
MAX_JOBS = int(os.getenv("MAX_JOBS", "50"))
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "100"))
BATCH_SIZE = 5

# AI Tools/Skills pool
AI_TOOLS = [
    "ChatGPT", "Claude", "Midjourney", "Stable Diffusion", "DALL-E",
    "GitHub Copilot", "Cursor", "Replit", "Anthropic API", "OpenAI API",
    "LangChain", "LlamaIndex", "Pinecone", "Weaviate", "Chroma",
    "TensorFlow", "PyTorch", "Hugging Face", "Transformers", "Gradio",
    "FastAPI", "Streamlit", "Flask", "Django", "Next.js",
    "React", "Vue.js", "TypeScript", "Python", "JavaScript",
    "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Supabase",
    "AWS", "GCP", "Azure", "Vercel", "Netlify",
    "Docker", "Kubernetes", "Terraform", "Git", "CI/CD"
]

JOB_CATEGORIES = [
    "AI Product Development",
    "LLM Integration Specialist",
    "AI Content Creation",
    "Machine Learning Engineer",
    "AI Automation Consultant",
    "Prompt Engineering",
    "AI Tool Development",
    "AI Research Assistant",
    "AI Business Analyst",
    "AI UX Designer"
]


def call_ollama(prompt: str, max_retries: int = 3) -> str:
    """Call Ollama API with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"⚠️  Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed after {max_retries} attempts: {e}")
                return ""
    return ""


def generate_job_title(category: str) -> str:
    """Generate a realistic job title."""
    prefixes = ["Senior", "Lead", "Principal", "Junior", "Mid-level", ""]
    suffixes = ["Engineer", "Developer", "Specialist", "Consultant", "Architect", "Analyst"]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    if prefix:
        return f"{prefix} {category} {suffix}".strip()
    return f"{category} {suffix}"


def generate_job_description(title: str, category: str) -> str:
    """Generate job description using Ollama."""
    prompt = f"""Write a professional job description for a {title} position in {category}.

Requirements:
- Focus on AI/LLM tools and capabilities
- Include specific technical skills
- Mention remote work and flexible hours
- Keep it concise (150-200 words)
- Professional tone

Job Description:"""
    
    description = call_ollama(prompt)
    if not description:
        # Fallback description
        description = f"""We are seeking a {title} to join our team. This role focuses on {category.lower()} using modern AI tools and LLMs.

Key responsibilities include working with AI technologies, developing solutions, and collaborating with cross-functional teams.

The ideal candidate will have experience with AI tools, strong problem-solving skills, and the ability to work independently."""
    
    return description


def generate_required_skills() -> List[str]:
    """Generate required skills for a job."""
    num_skills = random.randint(3, 6)
    return random.sample(AI_TOOLS, num_skills)


def generate_preferred_skills(required: List[str]) -> List[str]:
    """Generate preferred skills (different from required)."""
    available = [s for s in AI_TOOLS if s not in required]
    num_skills = random.randint(2, 4)
    return random.sample(available, min(num_skills, len(available)))


def generate_candidate_skills() -> List[str]:
    """Generate skills for a candidate profile."""
    num_skills = random.randint(5, 12)
    return random.sample(AI_TOOLS, num_skills)


def generate_experience_summary(skills: List[str]) -> str:
    """Generate experience summary using Ollama."""
    skills_str = ", ".join(skills[:5])
    prompt = f"""Write a brief professional experience summary (100-150 words) for an LLC owner who specializes in AI tools including: {skills_str}.

Focus on:
- Years of experience (2-8 years)
- Types of projects completed
- Key achievements
- Professional tone

Experience Summary:"""
    
    summary = call_ollama(prompt)
    if not summary:
        # Fallback summary
        years = random.randint(2, 8)
        summary = f"""Experienced LLC owner with {years} years of expertise in AI and LLM technologies. Specialized in {skills_str}. 

Completed numerous projects involving AI tool integration, automation, and custom solution development. Strong background in working with modern AI platforms and delivering high-quality results for clients."""
    
    return summary


def generate_projects(skills: List[str]) -> List[Dict[str, Any]]:
    """Generate portfolio projects."""
    num_projects = random.randint(2, 5)
    projects = []
    
    for _ in range(num_projects):
        project_skills = random.sample(skills, min(3, len(skills)))
        project = {
            "title": f"AI Project using {', '.join(project_skills[:2])}",
            "description": f"Developed a solution using {', '.join(project_skills)}",
            "technologies": project_skills,
            "year": random.randint(2020, 2024)
        }
        projects.append(project)
    
    return projects


def create_anonymous_user_id() -> str:
    """Generate a unique anonymous user ID."""
    random_bytes = secrets.token_bytes(32)
    return hashlib.sha256(random_bytes).hexdigest()


def create_job(db, title: str, description: str, required_skills: List[str], preferred_skills: List[str]) -> JobPosting:
    """Create a job posting."""
    job = JobPosting(
        title=title,
        description=description,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        active=True
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_candidate(db, skills: List[str], experience_summary: str, projects: List[Dict]) -> tuple:
    """Create a candidate profile."""
    user_id = create_anonymous_user_id()
    
    # Create anonymous user
    user = AnonymousUser(
        id=user_id,
        metadata={"generated": True, "generated_at": datetime.utcnow().isoformat()}
    )
    db.add(user)
    
    # Create LLC profile
    profile = LLCProfile(
        user_id=user_id,
        skills=skills,
        projects=projects,
        experience_summary=experience_summary
    )
    db.add(profile)
    
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    
    return user, profile


def main():
    """Main generation function."""
    print("🚀 Starting test data generation...")
    print(f"   Ollama URL: {OLLAMA_URL}")
    print(f"   Model: {OLLAMA_MODEL}")
    print(f"   Max Jobs: {MAX_JOBS}")
    print(f"   Max Candidates: {MAX_CANDIDATES}")
    print(f"   Rate Limit: {REQUESTS_PER_MINUTE} requests/minute")
    print()
    
    # Initialize database
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check existing counts
        existing_jobs = db.query(JobPosting).count()
        existing_candidates = db.query(AnonymousUser).count()
        
        print(f"📊 Current database state:")
        print(f"   Jobs: {existing_jobs}")
        print(f"   Candidates: {existing_candidates}")
        print()
        
        # Generate jobs
        jobs_to_create = max(0, MAX_JOBS - existing_jobs)
        if jobs_to_create > 0:
            print(f"📝 Generating {jobs_to_create} jobs...")
            for i in range(jobs_to_create):
                category = random.choice(JOB_CATEGORIES)
                title = generate_job_title(category)
                
                print(f"   [{i+1}/{jobs_to_create}] Creating job: {title}")
                
                description = generate_job_description(title, category)
                required_skills = generate_required_skills()
                preferred_skills = generate_preferred_skills(required_skills)
                
                job = create_job(db, title, description, required_skills, preferred_skills)
                print(f"      ✅ Created job ID: {job.id}")
                
                # Rate limiting
                if i < jobs_to_create - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            print(f"✅ Created {jobs_to_create} jobs")
            print()
        else:
            print("✅ Sufficient jobs already exist")
            print()
        
        # Generate candidates
        candidates_to_create = max(0, MAX_CANDIDATES - existing_candidates)
        if candidates_to_create > 0:
            print(f"👤 Generating {candidates_to_create} candidate profiles...")
            
            for i in range(0, candidates_to_create, BATCH_SIZE):
                batch_size = min(BATCH_SIZE, candidates_to_create - i)
                print(f"   Batch {i//BATCH_SIZE + 1}: Creating {batch_size} candidates...")
                
                for j in range(batch_size):
                    idx = i + j + 1
                    print(f"      [{idx}/{candidates_to_create}] Creating candidate profile...")
                    
                    skills = generate_candidate_skills()
                    experience_summary = generate_experience_summary(skills)
                    projects = generate_projects(skills)
                    
                    user, profile = create_candidate(db, skills, experience_summary, projects)
                    print(f"         ✅ Created user ID: {user.id[:16]}...")
                    
                    # Rate limiting
                    if idx < candidates_to_create:
                        time.sleep(DELAY_BETWEEN_REQUESTS)
                
                print(f"   ✅ Batch complete")
                print()
            
            print(f"✅ Created {candidates_to_create} candidate profiles")
            print()
        else:
            print("✅ Sufficient candidates already exist")
            print()
        
        # Final stats
        final_jobs = db.query(JobPosting).count()
        final_candidates = db.query(AnonymousUser).count()
        
        print("📊 Final database state:")
        print(f"   Jobs: {final_jobs}")
        print(f"   Candidates: {final_candidates}")
        print()
        print("✅ Test data generation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

