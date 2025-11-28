"""
Generate simulated users for zero-knowledge JobMatch testing
No real PII - synthetic data only for testing matching engine
"""

import random
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import hashlib


class SimulatedUserGenerator:
    """Generate synthetic users for testing without exposing real PII"""
    
    SKILLS = [
        'Python', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
        'FastAPI', 'Django', 'Flask', 'Node.js', 'Express', 'NestJS',
        'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
        'CI/CD', 'Git', 'Linux', 'Bash', 'PowerShell',
        'AI/ML', 'TensorFlow', 'PyTorch', 'Scikit-learn',
        'Data Analysis', 'Pandas', 'NumPy', 'Matplotlib',
        'REST APIs', 'GraphQL', 'WebSockets', 'gRPC',
        'Security', 'OAuth', 'JWT', 'Encryption',
        'UI/UX', 'Figma', 'Sketch', 'Adobe XD',
        'Testing', 'Jest', 'Pytest', 'Selenium', 'Cypress',
        'Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence'
    ]
    
    INDUSTRIES = [
        'FinTech', 'HealthTech', 'EdTech', 'E-commerce', 'SaaS',
        'Gaming', 'Social Media', 'Analytics', 'Cybersecurity',
        'AI/ML', 'DevOps', 'Enterprise', 'Startup', 'Agency'
    ]
    
    AVAILABILITY_TYPES = [
        'full-time', 'part-time', 'contract', 'freelance', 'consulting'
    ]
    
    RATE_RANGES = ['junior', 'mid', 'senior', 'staff', 'principal']
    
    EXPERIENCE_LEVELS = {
        'junior': (0, 3),
        'mid': (3, 7),
        'senior': (7, 12),
        'staff': (12, 18),
        'principal': (18, 30)
    }
    
    def __init__(self, seed: int = 42):
        """Initialize with optional seed for reproducibility"""
        random.seed(seed)
    
    def generate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate a single simulated user"""
        
        # Determine experience level first
        rate_range = random.choice(self.RATE_RANGES)
        min_exp, max_exp = self.EXPERIENCE_LEVELS[rate_range]
        experience_years = random.randint(min_exp, max_exp)
        
        # Generate capabilities (public data for matching)
        num_skills = random.randint(3, 8)
        capabilities = {
            'skills': random.sample(self.SKILLS, k=num_skills),
            'experience_years': experience_years,
            'availability': random.choice(self.AVAILABILITY_TYPES),
            'rate_range': rate_range,
            'industries': random.sample(self.INDUSTRIES, k=random.randint(1, 4)),
            'remote_preference': random.choice(['remote', 'hybrid', 'onsite', 'flexible']),
            'hours_per_week': random.choice([10, 20, 30, 40, 50]),
            'currently_available': random.choice([True, False]),
            'timezone': random.choice(['EST', 'PST', 'CST', 'MST', 'UTC', 'GMT'])
        }
        
        # Generate private data (would be encrypted in real system)
        # Using completely synthetic data - NO real PII
        private_data = {
            'display_name': f'User_{user_id}',  # Not real name
            'bio': self._generate_bio(capabilities),
            'portfolio_url': f'https://portfolio.example.com/{user_id}',
            'preferred_contact': random.choice(['email', 'in-app', 'video-call']),
            'work_preferences': {
                'team_size': random.choice(['small', 'medium', 'large', 'any']),
                'project_duration': random.choice(['short', 'medium', 'long', 'ongoing']),
                'communication_style': random.choice(['async', 'sync', 'mixed'])
            }
        }
        
        # Simulate encrypted blob (in real system, this would be AES-256 encrypted)
        encrypted_profile = self._mock_encrypt(private_data, user_id)
        
        return {
            'user_id': user_id,
            'email': f'simuser{user_id}@example.com',  # Synthetic email
            'auth_hash': self._generate_auth_hash(user_id),
            'encrypted_profile': encrypted_profile,
            'capabilities': capabilities,
            'created_at': self._random_date(),
            'last_active': datetime.utcnow().isoformat()
        }
    
    def generate_users(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate multiple simulated users"""
        return [self.generate_user(f'sim_{i:04d}') for i in range(count)]
    
    def generate_seekers(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate users looking for candidates (employers/clients)"""
        seekers = []
        
        for i in range(count):
            seeker_id = f'seek_{i:04d}'
            
            # What they're looking for
            seeking = {
                'seeker_id': seeker_id,
                'seeking_skills': random.sample(self.SKILLS, k=random.randint(3, 6)),
                'experience_level': random.choice(self.RATE_RANGES),
                'availability_needed': random.choice(self.AVAILABILITY_TYPES),
                'industries': random.sample(self.INDUSTRIES, k=random.randint(1, 3)),
                'budget_range': random.choice(['budget', 'mid', 'premium', 'negotiable']),
                'project_duration': random.choice(['1-week', '1-month', '3-months', '6-months', 'ongoing']),
                'start_date': random.choice(['immediate', '2-weeks', '1-month', 'flexible']),
                'remote_ok': random.choice([True, False]),
                'timezone_preference': random.choice(['EST', 'PST', 'CST', 'UTC', 'any'])
            }
            
            seekers.append(seeking)
        
        return seekers
    
    def _generate_bio(self, capabilities: Dict) -> str:
        """Generate synthetic bio based on capabilities"""
        skills_str = ', '.join(capabilities['skills'][:3])
        exp = capabilities['experience_years']
        
        templates = [
            f"Experienced professional with {exp} years in {skills_str}",
            f"{exp} years of expertise in {skills_str} and related technologies",
            f"Specialist in {skills_str} with {exp} years of hands-on experience",
            f"Passionate about {skills_str}. {exp} years building scalable systems"
        ]
        
        return random.choice(templates)
    
    def _mock_encrypt(self, data: Dict, user_id: str) -> str:
        """Mock encryption (in real system, use AES-256)"""
        # Simulating encrypted blob - just JSON + hash for testing
        json_str = json.dumps(data, sort_keys=True)
        # In real system: return AES-256 encrypted blob
        return f"ENCRYPTED:{hashlib.sha256(json_str.encode()).hexdigest()}:{len(json_str)}"
    
    def _generate_auth_hash(self, user_id: str) -> str:
        """Generate mock auth hash (in real system, use PBKDF2)"""
        # Simulating auth hash
        return hashlib.sha256(f"auth_{user_id}".encode()).hexdigest()
    
    def _random_date(self) -> str:
        """Generate random creation date in past 6 months"""
        days_ago = random.randint(0, 180)
        date = datetime.utcnow() - timedelta(days=days_ago)
        return date.isoformat()
    
    def export_to_json(self, users: List[Dict], filename: str = 'simulated_users.json'):
        """Export users to JSON file"""
        with open(filename, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"Exported {len(users)} users to {filename}")
    
    def export_to_sql(self, users: List[Dict], filename: str = 'simulated_users.sql'):
        """Export users as SQL INSERT statements"""
        with open(filename, 'w') as f:
            f.write("-- Simulated users for testing\n")
            f.write("-- NO REAL PII - Synthetic data only\n\n")
            
            # Users table inserts
            f.write("-- Users (zero-knowledge)\n")
            for user in users:
                f.write(f"INSERT INTO users (user_id, email, auth_hash, encrypted_profile, created_at) VALUES (\n")
                f.write(f"  '{user['user_id']}',\n")
                f.write(f"  '{user['email']}',\n")
                f.write(f"  '{user['auth_hash']}',\n")
                f.write(f"  '{user['encrypted_profile']}',\n")
                f.write(f"  '{user['created_at']}'\n")
                f.write(");\n\n")
            
            # Capabilities table inserts
            f.write("-- Capabilities (public, for matching)\n")
            for user in users:
                cap = user['capabilities']
                for skill in cap['skills']:
                    f.write(f"INSERT INTO capabilities (user_id, skill, experience_years, availability, rate_range) VALUES (\n")
                    f.write(f"  '{user['user_id']}',\n")
                    f.write(f"  '{skill}',\n")
                    f.write(f"  {cap['experience_years']},\n")
                    f.write(f"  '{cap['availability']}',\n")
                    f.write(f"  '{cap['rate_range']}'\n")
                    f.write(");\n")
        
        print(f"Exported {len(users)} users to {filename}")


def main():
    """Generate and export simulated users"""
    print("Generating simulated users for JobMatch zero-knowledge testing...")
    
    generator = SimulatedUserGenerator(seed=42)
    
    # Generate 100 candidates
    print("\n1. Generating 100 simulated candidates...")
    users = generator.generate_users(count=100)
    
    # Generate 20 seekers
    print("2. Generating 20 simulated seekers...")
    seekers = generator.generate_seekers(count=20)
    
    # Export to JSON
    print("\n3. Exporting to JSON...")
    generator.export_to_json(users, 'simulated_users.json')
    generator.export_to_json(seekers, 'simulated_seekers.json')
    
    # Export to SQL
    print("4. Exporting to SQL...")
    generator.export_to_sql(users, 'simulated_users.sql')
    
    # Print summary
    print("\n✅ Generation complete!")
    print(f"\nSummary:")
    print(f"  - {len(users)} simulated candidates")
    print(f"  - {len(seekers)} simulated seekers")
    print(f"  - Skill distribution: {len(SimulatedUserGenerator.SKILLS)} unique skills")
    print(f"  - Experience range: 0-30 years")
    print(f"  - NO real PII - all synthetic data")
    
    # Show sample user
    print("\n📋 Sample User (capabilities only - no PII):")
    sample = users[0]
    print(f"  User ID: {sample['user_id']}")
    print(f"  Skills: {', '.join(sample['capabilities']['skills'][:3])}...")
    print(f"  Experience: {sample['capabilities']['experience_years']} years")
    print(f"  Availability: {sample['capabilities']['availability']}")
    print(f"  Rate Range: {sample['capabilities']['rate_range']}")
    print(f"  Encrypted Profile: {sample['encrypted_profile'][:50]}...")
    
    return users, seekers


if __name__ == '__main__':
    users, seekers = main()
