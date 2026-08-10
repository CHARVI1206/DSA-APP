import json
import streamlit as st
import google.generativeai as genai
from services.cache_service import get_cached, set_cached, generate_cache_key
from utils.helpers import hash_prompt

@st.cache_resource
def _get_model():
    """Initializes and returns the Gemini model."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-2.0-flash')

def _cached_generate(cache_key: str, prompt: str, temperature: float = 0.3) -> str:
    """Generates text from Gemini, using cache if available."""
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    model = _get_model()
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=temperature)
    )
    
    result = response.text
    set_cached(cache_key, hash_prompt(prompt), result)
    return result

def generate_topic_notes(topic_name: str, section_type: str) -> str:
    """Generates markdown notes for a specific topic and section."""
    prompt = f"Create detailed markdown notes for the Data Structures and Algorithms topic '{topic_name}', specifically focusing on the '{section_type}' section. Make it educational, clear, and concise."
    cache_key = generate_cache_key("notes", topic_name, section_type)
    return _cached_generate(cache_key, prompt, temperature=0.3)

def generate_flashcards(topic_name: str, count: int = 10) -> list[dict]:
    """Generates flashcards for a topic."""
    prompt = f"Generate {count} flashcards for the DSA topic '{topic_name}'. Return ONLY a JSON array of objects with 'front' and 'back' string keys. No markdown blocks."
    cache_key = generate_cache_key("flashcards", topic_name, count)
    
    try:
        response_text = _cached_generate(cache_key, prompt, temperature=0.5)
        # Handle potential markdown code blocks in output
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
        return json.loads(response_text.strip())
    except Exception as e:
        st.error(f"Failed to generate flashcards: {e}")
        return []

def validate_logic_gate(problem_title: str, problem_desc: str, user_responses: dict) -> dict:
    """Validates user's conceptual understanding before allowing coding."""
    prompt = f"Problem: {problem_title}\nDescription: {problem_desc}\nUser's proposed logic: {json.dumps(user_responses)}\n\nEvaluate if the user's logic is sound enough to start coding. Return ONLY JSON with keys: 'validated' (boolean), 'feedback' (string), 'suggestions' (list of strings)."
    cache_key = generate_cache_key("logic_gate", problem_title, json.dumps(user_responses, sort_keys=True))
    
    try:
        response_text = _cached_generate(cache_key, prompt, temperature=0.2)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
        return json.loads(response_text.strip())
    except Exception as e:
        return {"validated": False, "feedback": f"Error validating logic: {e}", "suggestions": []}

def mentor_chat(mode: dict, context: str, user_message: str, history: list = []) -> str:
    """Chats with AI using a specific persona."""
    prompt = f"{mode['system_prompt']}\n\nContext: {context}\n\nHistory: {json.dumps(history)}\n\nUser: {user_message}\nAI:"
    # No cache for chat to keep it dynamic, or we can just call it directly
    model = _get_model()
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.7)
    )
    return response.text

def review_code(code: str, language: str, problem_title: str) -> str:
    """Provides code review feedback."""
    prompt = f"Review the following {language} code for the problem '{problem_title}'. Provide feedback on time/space complexity, edge cases, and best practices.\n\nCode:\n{code}"
    cache_key = generate_cache_key("code_review", problem_title, language, hash_prompt(code))
    return _cached_generate(cache_key, prompt, temperature=0.3)

def generate_new_problem(topic_name: str, difficulty: str) -> dict:
    """Generates a brand new, unique problem for the given topic and difficulty."""
    prompt = f"""Generate a unique, high-quality Data Structures and Algorithms (DSA) problem for the topic '{topic_name}' with a '{difficulty}' difficulty. 
    It should be comparable in quality to a Leetcode problem.
    
    Return ONLY valid JSON matching this exact structure, with no extra markdown formatting or text outside the JSON:
    {{
        "title": "Problem Title",
        "description": "Full markdown description including problem statement, constraints, and examples.",
        "hints": ["Hint 1", "Hint 2"],
        "tags": ["{topic_name.lower()}", "tag2"],
        "companies": ["Company1", "Company2"],
        "test_cases": [
            {{"input": "input_string_1", "expected_output": "output_string_1", "is_hidden": false}},
            {{"input": "input_string_2", "expected_output": "output_string_2", "is_hidden": true}}
        ],
        "time_complexity": "O(N)",
        "space_complexity": "O(1)"
    }}
    Make sure to include at least 3 test cases (1 visible, 2 hidden). 
    """
    
    try:
        # Generate without cache because we want a *new* unique problem each time
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.8) # Higher temperature for novelty
        )
        
        response_text = response.text
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
        return json.loads(response_text.strip())
    except Exception as e:
        print(f"Error generating new problem: {e}")
        return None
