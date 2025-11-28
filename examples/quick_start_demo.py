"""
Quick Start Demo - Unbiased Job Matching System

This script demonstrates how to use the agentic AI system for unbiased job matching.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.llm_providers import OpenAILanguageModel, OpenAIEmbeddingModel
from src.agents import (
    JobDescriptionAnalyzerAgent,
    CandidateProfileAnalyzerAgent,
    BiasDetectionAgent,
    MatchingAgent,
    DataIngestionAgent
)
from src.tools import WebScraperTool, FileReaderTool, VectorDBStorageTool
from src.workflows import JobMatchingWorkflow


def setup_agents():
    """Initialize all agents and tools."""
    print("🔧 Setting up agents and tools...")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  Warning: No API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY")
        print("   Using mock mode (will fail on actual LLM calls)")
        return None
    
    # Initialize LLM (try OpenAI first, fallback to OpenRouter)
    try:
        llm = OpenAILanguageModel(model="gpt-4")
        embedding_model = OpenAIEmbeddingModel()
        print("✅ Using OpenAI")
    except Exception:
        try:
            from src.models.llm_providers import OpenRouterLanguageModel
            llm = OpenRouterLanguageModel(model="anthropic/claude-3.5-sonnet")
            embedding_model = None  # OpenRouter doesn't have embeddings in this example
            print("✅ Using OpenRouter")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            return None
    
    # Initialize analyzers
    job_analyzer = JobDescriptionAnalyzerAgent(llm=llm)
    candidate_analyzer = CandidateProfileAnalyzerAgent(llm=llm)
    bias_detector = BiasDetectionAgent(llm=llm)
    matcher = MatchingAgent(llm=llm, embedding_model=embedding_model)
    
    # Initialize tools
    web_scraper = WebScraperTool()
    file_reader = FileReaderTool()
    
    # Initialize vector DB (using ChromaDB for demo - no setup needed)
    try:
        vector_db = VectorDBStorageTool(provider="chroma")
        print("✅ Using ChromaDB for vector storage")
    except Exception as e:
        print(f"⚠️  Vector DB not available: {e}")
        vector_db = None
    
    # Initialize data ingestion agent
    tools = [web_scraper, file_reader]
    if vector_db:
        tools.append(vector_db)
    
    ingestion_agent = DataIngestionAgent(
        job_analyzer=job_analyzer,
        candidate_analyzer=candidate_analyzer,
        tools=tools
    )
    
    # Initialize workflow
    workflow = JobMatchingWorkflow(
        data_ingestion_agent=ingestion_agent,
        job_analyzer=job_analyzer,
        candidate_analyzer=candidate_analyzer,
        bias_detection_agent=bias_detector,
        matching_agent=matcher
    )
    
    print("✅ All agents initialized successfully!\n")
    return workflow


def demo_with_sample_data(workflow):
    """Run demo with sample job description and candidate profile."""
    print("=" * 80)
    print("DEMO: Unbiased Job Matching")
    print("=" * 80)
    
    # Sample job description
    job_description = """
    Senior Software Engineer
    
    We are looking for an experienced software engineer to join our team. 
    The ideal candidate will have:
    - 5+ years of experience in Python and JavaScript
    - Strong background in web development
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Excellent problem-solving skills
    - Ability to work in a fast-paced environment
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews
    - Mentor junior developers
    
    We offer competitive salary and benefits.
    """
    
    # Sample candidate profile
    candidate_profile = """
    John Doe - Software Engineer
    
    Summary:
    Experienced software engineer with 7 years of experience building web applications.
    Strong background in Python, JavaScript, and cloud technologies.
    
    Skills:
    - Python (7 years)
    - JavaScript/TypeScript (6 years)
    - React, Node.js
    - AWS, Docker, Kubernetes
    - PostgreSQL, MongoDB
    - Git, CI/CD
    
    Experience:
    - Senior Software Engineer at Tech Corp (2020-present)
      * Led development of microservices architecture
      * Mentored team of 5 junior developers
      * Improved system performance by 40%
    
    - Software Engineer at Startup Inc (2017-2020)
      * Built full-stack web applications
      * Implemented CI/CD pipelines
    
    Education:
    - BS in Computer Science, State University (2017)
    """
    
    print("\n📋 Job Description:")
    print("-" * 80)
    print(job_description[:200] + "...")
    
    print("\n👤 Candidate Profile:")
    print("-" * 80)
    print(candidate_profile[:200] + "...")
    
    print("\n🚀 Running matching workflow...\n")
    
    # Execute workflow
    result = workflow.execute({
        "job_content": job_description,
        "candidate_content": candidate_profile
    })
    
    # Display results
    print_results(result)
    
    return result


def print_results(result):
    """Pretty print workflow results."""
    print("=" * 80)
    print("MATCHING RESULTS")
    print("=" * 80)
    
    if result.get("status") != "completed":
        print(f"❌ Status: {result.get('status')}")
        if result.get("errors"):
            print("Errors:")
            for error in result["errors"]:
                print(f"  - {error}")
        return
    
    final_rec = result.get("final_recommendation", {})
    
    # Match score
    match_score = final_rec.get("match_score", 0.0)
    score_bar = "█" * int(match_score * 50) + "░" * (50 - int(match_score * 50))
    print(f"\n📊 Match Score: {match_score:.1%}")
    print(f"   [{score_bar}]")
    
    # Recommendation
    recommendation = final_rec.get("recommendation", "review").upper()
    rec_emoji = "✅" if recommendation == "PROCEED" else "⚠️" if recommendation == "REVIEW" else "❌"
    print(f"\n{rec_emoji} Recommendation: {recommendation}")
    
    # Bias severity
    bias_severity = final_rec.get("bias_severity", "low").upper()
    bias_emoji = "🟢" if bias_severity == "LOW" else "🟡" if bias_severity == "MEDIUM" else "🔴"
    print(f"{bias_emoji} Bias Severity: {bias_severity}")
    
    # Strengths
    strengths = final_rec.get("strengths", [])
    if strengths:
        print(f"\n✨ Strengths ({len(strengths)}):")
        for i, strength in enumerate(strengths[:5], 1):  # Show top 5
            print(f"   {i}. {strength}")
    
    # Gaps
    gaps = final_rec.get("gaps", [])
    if gaps:
        print(f"\n⚠️  Gaps ({len(gaps)}):")
        for i, gap in enumerate(gaps[:5], 1):  # Show top 5
            print(f"   {i}. {gap}")
    
    # Bias considerations
    bias_considerations = final_rec.get("bias_considerations", "")
    if bias_considerations:
        print(f"\n🔍 Bias Considerations:")
        print(f"   {bias_considerations[:200]}...")
    
    # Reasoning
    reasoning = final_rec.get("reasoning", "")
    if reasoning:
        print(f"\n💭 Reasoning:")
        print(f"   {reasoning[:300]}...")
    
    # Detailed bias analysis (if available)
    bias_step = result.get("steps", {}).get("bias_detection", {})
    if bias_step:
        bias_analysis = bias_step.get("bias_analysis", {})
        potential_biases = bias_analysis.get("potential_biases", [])
        if potential_biases:
            print(f"\n🚨 Potential Biases Detected ({len(potential_biases)}):")
            for i, bias in enumerate(potential_biases[:3], 1):  # Show top 3
                print(f"   {i}. [{bias.get('type', 'unknown').upper()}] {bias.get('description', '')[:100]}")
            
            mitigation = bias_analysis.get("mitigation_strategies", [])
            if mitigation:
                print(f"\n💡 Mitigation Strategies:")
                for i, strategy in enumerate(mitigation[:3], 1):
                    print(f"   {i}. {strategy}")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("🤖 Agentic AI - Unbiased Job Matching System")
    print("=" * 80 + "\n")
    
    # Setup
    workflow = setup_agents()
    if not workflow:
        print("\n❌ Failed to initialize. Please check your API keys and dependencies.")
        print("\nTo set up:")
        print("  1. Install dependencies: pip install -r requirements-agentic-ai.txt")
        print("  2. Set API key: export OPENAI_API_KEY='your-key'")
        print("  3. Run again: python examples/quick_start_demo.py")
        return
    
    # Run demo
    try:
        result = demo_with_sample_data(workflow)
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("  - Try with your own job descriptions and candidate profiles")
        print("  - Experiment with different data sources (URLs, files)")
        print("  - Customize agent prompts for your specific use case")
        print("  - See UNBIASED_JOB_MATCHING_GUIDE.md for more examples")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

