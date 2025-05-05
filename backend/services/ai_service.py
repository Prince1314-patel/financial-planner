from backend.models.user_profile import UserProfile
from typing import Dict, Any
from backend.prompts.system_prompts import SYSTEM_PROMPT
from backend.prompts.templates import build_prompt
import langchain
import groq


def get_ai_recommendation(profile: UserProfile, metrics: Dict[str, Any], groq_api_key: str) -> Dict[str, Any]:
    # Compose the prompt
    user_prompt = build_prompt(profile, metrics)
    full_prompt = SYSTEM_PROMPT + "\n" + user_prompt

    try:
        # Use the official LangChain Groq integration with ChatGroq
        from langchain_groq import ChatGroq
        import json
        
        # Compose messages in the expected format
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", user_prompt + '\n\nRespond strictly in the following JSON format: {"narrative": str, "allocations": {str: int}, "next_steps": str}')
        ]
        # Instantiate the Groq chat model with the requested model
        llm = ChatGroq(
            api_key=groq_api_key,
            model="mistral-saba-24b",
            temperature=0.3,
            max_tokens=1024,
            timeout=60,
            max_retries=2
        )
        ai_msg = llm.invoke(messages)
        response = ai_msg.content.strip() if hasattr(ai_msg, 'content') else str(ai_msg)
        import re
        try:
            # Remove triple backticks and language specifier
            cleaned = re.sub(r"^```(?:json)?|```$", "", response.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()
            # Find the first { and the last }
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = cleaned[start:end+1]
                parsed = json.loads(json_str)
            else:
                raise ValueError("No JSON object found")
        except Exception as parse_exc:
            print("[ERROR] JSON parsing failed:", parse_exc)
            # Fallback: crude parsing
            parsed = {
                "narrative": response,
                "allocations": {},
                "next_steps": "Please review the above advice."
            }
        if "allocations" not in parsed:
            parsed["allocations"] = {}
        if "narrative" not in parsed:
            parsed["narrative"] = response
        if "next_steps" not in parsed:
            parsed["next_steps"] = "Please review the above advice."
        return parsed
    except Exception as e:
        print("[ERROR] Exception in get_ai_recommendation:", e)
        # Fallback to mock response if Groq or LangChain fails
        return {
            "narrative": "Based on your profile, we recommend a diversified allocation across stocks, bonds, real estate, and cash equivalents.",
            "allocations": {
                "Stocks (ETFs)": 50,
                "Bonds": 25,
                "Real Estate": 15,
                "Cash Equivalents": 10
            },
            "next_steps": "Consider reviewing your goals periodically and adjusting your allocation as your financial situation changes."
        }
