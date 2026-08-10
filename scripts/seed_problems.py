import sys
import os
import time
import uuid

# Add parent directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_client import get_client
from services.ai_service import generate_new_problem
from services.problem_service import create_problem
from utils.helpers import slugify

def seed_problems(problems_per_topic=3):
    """
    Connects to Supabase, retrieves all topics, and uses Gemini to generate
    and insert new problems for each topic.
    """
    print("=" * 50)
    print("♾️  Infinity Practice — Problem Seeder")
    print("=" * 50)
    
    client = get_client()
    
    # 1. Fetch all topics
    print("Fetching topics from database...")
    res = client.table("topics").select("id, title").execute()
    topics = res.data
    
    if not topics:
        print("No topics found. Please run the schema.sql seed data first.")
        return
        
    print(f"Found {len(topics)} topics. Generating {problems_per_topic} problems each.")
    
    difficulties = ["easy", "medium", "hard"]
    total_generated = 0
    
    for topic in topics:
        topic_id = topic["id"]
        topic_title = topic["title"]
        print(f"\n--- Generating for Topic: {topic_title} ---")
        
        for i in range(problems_per_topic):
            diff = difficulties[i % len(difficulties)]
            print(f"[{i+1}/{problems_per_topic}] Generating {diff} problem...")
            
            try:
                # Call Gemini to generate the problem
                problem_data = generate_new_problem(topic_title, diff)
                
                if problem_data:
                    # Clean up data and prepare for insert
                    base_slug = slugify(problem_data["title"])
                    problem_data["slug"] = f"{base_slug}-{str(uuid.uuid4())[:6]}"
                    problem_data["topic_id"] = topic_id
                    problem_data["is_custom"] = False # System seeded
                    
                    # Ensure JSONB arrays are properly formatted lists
                    problem_data["tags"] = problem_data.get("tags", [])
                    problem_data["companies"] = problem_data.get("companies", [])
                    problem_data["test_cases"] = problem_data.get("test_cases", [])
                    
                    # Insert into DB
                    created = create_problem(problem_data)
                    print(f"✅ Inserted: {problem_data['title']}")
                    total_generated += 1
                else:
                    print("❌ Failed to generate (AI returned None).")
                    
            except Exception as e:
                print(f"❌ Error inserting problem: {e}")
                
            # Sleep briefly to avoid hitting rate limits too hard
            time.sleep(2)
            
    print("=" * 50)
    print(f"Done! Successfully seeded {total_generated} new problems.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed DSA problems via Gemini AI")
    parser.add_argument("--count", type=int, default=3, help="Number of problems to generate per topic")
    args = parser.parse_args()
    
    # Requires Streamlit secrets to be available in the environment or .streamlit/secrets.toml
    # For a standalone script, we might need to load secrets manually if not running via streamlit,
    # but the Streamlit `st.secrets` mechanism usually works if run from the project root 
    # where `.streamlit/` exists, although it might complain if not strictly a streamlit run.
    # To be safe, we wrap the execution.
    try:
        import streamlit as st
        # Just accessing a secret initializes the secrets manager
        _ = st.secrets["SUPABASE_URL"]
        seed_problems(args.count)
    except FileNotFoundError:
        print("Error: Could not find .streamlit/secrets.toml. Please run from project root.")
    except Exception as e:
        print(f"Error: {e}")
