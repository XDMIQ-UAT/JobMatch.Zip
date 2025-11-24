#!/usr/bin/env python3
"""
JobMatch.zip Terminal CLI
Terminal-based capability matching interface for paid beta users
"""

import cmd
import sys
import os
import json
from datetime import datetime
from typing import Optional
import psycopg2
import redis

# ASCII art banner
BANNER = """
╔══════════════════════════════════════════════════════════╗
║              JOBMATCH.ZIP - Session #{session_id}        ║
║  Capability-First Matching | Beta Access Confirmed      ║
╚══════════════════════════════════════════════════════════╝
"""

SEPARATOR = "━" * 60


class JobMatchCLI(cmd.Cmd):
    """Interactive terminal interface for JobMatch capability matching"""
    
    intro = BANNER + f"\n\nWelcome! You've purchased a JobMatch session.\n\nLet's find your best match in 3 steps.\n\nType 'help' for commands or just follow the prompts.\n\n{SEPARATOR}\n"
    prompt = "> "
    
    def __init__(self, user_id: str, session_id: str):
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
        self.intro = self.intro.format(session_id=session_id)
        
        # Connect to database
        self.db = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Load user session state
        self.load_state()
    
    def load_state(self):
        """Load user's session state from Redis"""
        state_key = f"jobmatch:session:{self.session_id}"
        state = self.redis.hgetall(state_key)
        
        self.task_description = state.get("task_description", "")
        self.time_estimate = state.get("time_estimate", "")
        self.availability = state.get("availability", "")
        self.interaction_mode = state.get("interaction_mode", "")
        self.current_step = int(state.get("current_step", 1))
        self.matched = state.get("matched", "false") == "true"
        
    def save_state(self):
        """Save user's session state to Redis"""
        state_key = f"jobmatch:session:{self.session_id}"
        self.redis.hset(state_key, mapping={
            "task_description": self.task_description,
            "time_estimate": self.time_estimate,
            "availability": self.availability,
            "interaction_mode": self.interaction_mode,
            "current_step": self.current_step,
            "matched": str(self.matched).lower(),
            "last_updated": datetime.now().isoformat()
        })
        self.redis.expire(state_key, 86400 * 7)  # 7 days
    
    def do_status(self, arg):
        """Check your session status and progress"""
        print(f"\n{SEPARATOR}")
        print(f"Session ID: {self.session_id}")
        print(f"Current Step: {self.current_step}/3")
        
        if self.task_description:
            print(f"Task: {self.task_description[:50]}...")
        if self.time_estimate:
            print(f"Estimate: {self.time_estimate} minutes")
        if self.availability:
            print(f"Available: {self.availability}")
        if self.matched:
            print("\n✅ YOU HAVE A MATCH!")
            print("Type 'match' to see match details")
        else:
            print("\n⏳ Matching in progress...")
        
        print(f"{SEPARATOR}\n")
    
    def do_start(self, arg):
        """Start or continue your capability assessment"""
        if self.current_step == 1:
            self.step1_task_description()
        elif self.current_step == 2:
            self.step2_preferences()
        elif self.current_step == 3:
            self.step3_review()
        else:
            print("Assessment complete! Type 'match' to check for matches.")
    
    def step1_task_description(self):
        """Step 1: Describe the task"""
        print(f"\n{SEPARATOR}")
        print("\nSTEP 1: What capability do you need?\n")
        print("Examples:")
        print("• Debug Python FastAPI endpoint")
        print("• Review AI prompt engineering strategy")
        print("• Explain Kubernetes deployment")
        print("• Brainstorm LLC business structure")
        print("• Automate data pipeline with n8n")
        print("\nYour task (200 chars max):")
        
        task = input(self.prompt).strip()
        
        if len(task) > 200:
            print("\n⚠️  Too long! Please keep it under 200 characters.")
            return
        
        if len(task) < 10:
            print("\n⚠️  Please provide more detail (at least 10 characters).")
            return
        
        self.task_description = task
        self.current_step = 2
        self.save_state()
        
        print(f"\n✅ Task recorded!\n\n{SEPARATOR}\n")
        self.step2_preferences()
    
    def step2_preferences(self):
        """Step 2: Time estimate and availability"""
        print(f"\n{SEPARATOR}")
        print("\nSTEP 2: Session details\n")
        
        # Time estimate
        print("How long do you think this takes?")
        print("1) 15-30 minutes")
        print("2) 45-60 minutes")
        print("3) 2+ hours (we'll break it down)")
        
        choice = input(self.prompt).strip()
        
        time_map = {
            "1": "15-30 minutes",
            "2": "45-60 minutes",
            "3": "2+ hours"
        }
        
        if choice not in time_map:
            print("\n⚠️  Please enter 1, 2, or 3")
            return
        
        self.time_estimate = time_map[choice]
        
        # Availability
        print("\nWhen do you need this done?")
        print("1) In the next 2 hours")
        print("2) Within 24 hours")
        print("3) This week (flexible)")
        
        choice = input(self.prompt).strip()
        
        avail_map = {
            "1": "next 2 hours",
            "2": "within 24 hours",
            "3": "this week"
        }
        
        if choice not in avail_map:
            print("\n⚠️  Please enter 1, 2, or 3")
            return
        
        self.availability = avail_map[choice]
        
        # Interaction mode
        print("\nPreferred interaction mode?")
        print("1) Text chat")
        print("2) Voice call")
        print("3) Video call")
        print("4) Async (email/docs)")
        
        choice = input(self.prompt).strip()
        
        mode_map = {
            "1": "text",
            "2": "voice",
            "3": "video",
            "4": "async"
        }
        
        if choice not in mode_map:
            print("\n⚠️  Please enter 1, 2, 3, or 4")
            return
        
        self.interaction_mode = mode_map[choice]
        self.current_step = 3
        self.save_state()
        
        print(f"\n✅ Preferences recorded!\n\n{SEPARATOR}\n")
        self.step3_review()
    
    def step3_review(self):
        """Step 3: Review and submit"""
        print(f"\n{SEPARATOR}")
        print("\nSTEP 3: Review your request\n")
        
        print(f"Task: {self.task_description}")
        print(f"Estimated time: {self.time_estimate}")
        print(f"Need it: {self.availability}")
        print(f"Mode: {self.interaction_mode}")
        
        print(f"\n{SEPARATOR}")
        print("\nLook good? (y/n/edit)")
        
        choice = input(self.prompt).strip().lower()
        
        if choice == "y":
            self.submit_request()
        elif choice == "edit":
            print("\nWhich step do you want to edit?")
            print("1) Task description")
            print("2) Preferences")
            
            step = input(self.prompt).strip()
            
            if step == "1":
                self.current_step = 1
                self.step1_task_description()
            elif step == "2":
                self.current_step = 2
                self.step2_preferences()
        else:
            print("\nType 'start' when ready to continue")
    
    def submit_request(self):
        """Submit the matching request"""
        print(f"\n{SEPARATOR}")
        print("\n📤 Submitting your request...")
        
        # Save to database
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO jobmatch_requests (
                session_id, user_id, task_description,
                time_estimate, availability, interaction_mode,
                status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            self.session_id, self.user_id, self.task_description,
            self.time_estimate, self.availability, self.interaction_mode,
            "pending", datetime.now()
        ))
        self.db.commit()
        
        # Notify founder (you) via webhook/email
        self.notify_founder()
        
        self.current_step = 4
        self.save_state()
        
        print("\n✅ Request submitted!")
        print("\n" + SEPARATOR)
        print("\nWhat happens next:")
        print("\n1. We'll manually curate your best match (within 24 hours)")
        print("2. You'll receive an email notification")
        print("3. SSH back in and type 'match' to see details")
        print("4. Schedule your session via the provided link")
        print("\n" + SEPARATOR)
        print("\nType 'logout' to exit (you can SSH back anytime)")
        print("Type 'status' to check progress")
        print("\n")
    
    def notify_founder(self):
        """Send notification to founder about new request"""
        # This would integrate with email/Slack/etc
        # For now, just log to Redis for polling
        self.redis.lpush("jobmatch:new_requests", json.dumps({
            "session_id": self.session_id,
            "user_id": self.user_id,
            "task": self.task_description,
            "time": self.time_estimate,
            "avail": self.availability,
            "mode": self.interaction_mode,
            "timestamp": datetime.now().isoformat()
        }))
    
    def do_match(self, arg):
        """Check if you have a match"""
        print(f"\n{SEPARATOR}")
        
        # Check for match in database
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT match_id, helper_name, helper_capabilities,
                   scheduled_time, meeting_link, created_at
            FROM jobmatch_matches
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.session_id,))
        
        match = cursor.fetchone()
        
        if not match:
            print("\n⏳ No match yet - we're working on it!")
            print("\nWe'll notify you via email when matched.")
            print("Average matching time: 8-12 hours")
        else:
            match_id, helper_name, capabilities, scheduled_time, meeting_link, created = match
            
            print("\n✅ YOU HAVE A MATCH!\n")
            print(f"Match ID: #{match_id}")
            print(f"Helper: {helper_name}")
            print(f"Capabilities: {capabilities}")
            
            if scheduled_time:
                print(f"\n📅 Scheduled: {scheduled_time}")
                print(f"🔗 Meeting link: {meeting_link}")
            else:
                print("\n📅 Not yet scheduled")
                print("\nSchedule your session:")
                print(meeting_link)  # Calendly link
        
        print(f"\n{SEPARATOR}\n")
    
    def do_feedback(self, arg):
        """Leave feedback after your session"""
        print(f"\n{SEPARATOR}")
        print("\nSESSION FEEDBACK\n")
        
        print("1. Did the task get done?")
        print("1) Yes, completely")
        print("2) Partially")
        print("3) No")
        
        completion = input(self.prompt).strip()
        
        print("\n2. Would you work with this helper again?")
        print("Rating (1-5 stars):")
        
        rating = input(self.prompt).strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except:
            print("\n⚠️  Please enter a number 1-5")
            return
        
        print("\n3. How long did it actually take? (minutes)")
        actual_time = input(self.prompt).strip()
        
        print("\n4. What went well? (optional, 100 chars)")
        what_worked = input(self.prompt).strip()[:100]
        
        # Save feedback
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO jobmatch_feedback (
                session_id, completion_status, rating,
                actual_time, what_worked, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            self.session_id, completion, rating,
            actual_time, what_worked, datetime.now()
        ))
        self.db.commit()
        
        print(f"\n✅ Feedback submitted! Thanks for helping us improve.\n")
        print(f"{SEPARATOR}\n")
    
    def do_help(self, arg):
        """Show available commands"""
        print(f"\n{SEPARATOR}")
        print("\nAVAILABLE COMMANDS:\n")
        print("start     - Start or continue capability assessment")
        print("status    - Check your session status")
        print("match     - Check if you have a match")
        print("feedback  - Leave feedback after your session")
        print("help      - Show this help message")
        print("logout    - Exit the terminal")
        print(f"\n{SEPARATOR}\n")
    
    def do_logout(self, arg):
        """Exit the JobMatch terminal"""
        print(f"\n{SEPARATOR}")
        print("\nThanks for using JobMatch.zip!")
        print("SSH back anytime to check status or leave feedback.")
        print(f"\n{SEPARATOR}\n")
        return True
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        return self.do_logout(arg)


def main():
    """Entry point for JobMatch CLI"""
    # Get user credentials from SSH environment
    user_id = os.getenv("JOBMATCH_USER_ID")
    session_id = os.getenv("JOBMATCH_SESSION_ID")
    
    if not user_id or not session_id:
        print("Error: Invalid session. Please check your SSH credentials.")
        sys.exit(1)
    
    # Start interactive CLI
    cli = JobMatchCLI(user_id, session_id)
    
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
