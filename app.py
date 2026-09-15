# app.py

import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import (
    VULNERABLE_PROMPT,
    SECURE_PROMPT
)

from attacks import (
    NORMAL_JOB,
    ATTACKS
)

from test_results import save_results


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()


# ==========================================
# Gemini API Key
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file."
    )


# ==========================================
# Gemini Client
# ==========================================

client = genai.Client(
    api_key=api_key
)


# ==========================================
# Model Configuration
# ==========================================

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


# ==========================================
# Call Gemini Model
# ==========================================

def ask_ai(system_prompt, user_input):

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=user_input,

        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        )
    )

    return response.text


# ==========================================
# Test Normal Job Listing
# ==========================================

def test_normal_job():

    print()
    print("=" * 70)
    print("NORMAL JOB LISTING TEST")
    print("=" * 70)

    print("\nUser Input:")
    print(NORMAL_JOB)

    response = ask_ai(
        VULNERABLE_PROMPT,
        NORMAL_JOB
    )

    print("\nAI Response:")
    print(response)

    return response


# ==========================================
# Run Injection Tests
# ==========================================

def run_injection_tests():

    results = []

    print()
    print("=" * 70)
    print("PROMPT INJECTION SECURITY TEST")
    print("=" * 70)

    for attack in ATTACKS:

        print()
        print("-" * 70)
        print(attack["name"])
        print("-" * 70)

        print("\nMalicious Input:")
        print(attack["input"])


        # --------------------------------------
        # BEFORE MITIGATION
        # --------------------------------------

        print("\n[1] BEFORE MITIGATION")

        vulnerable_response = ask_ai(
            VULNERABLE_PROMPT,
            attack["input"]
        )

        print("\nAI Response:")
        print(vulnerable_response)


        # --------------------------------------
        # AFTER MITIGATION
        # --------------------------------------

        print("\n[2] AFTER MITIGATION")

        secure_prompt = SECURE_PROMPT.format(
            user_input=attack["input"]
        )

        secure_response = ask_ai(
            secure_prompt,
            ""
        )

        print("\nAI Response:")
        print(secure_response)


        # --------------------------------------
        # Store Results
        # --------------------------------------

        results.append({

            "attack_name": attack["name"],

            "malicious_input": attack["input"],

            "before_mitigation": vulnerable_response,

            "after_mitigation": secure_response

        })


    return results


# ==========================================
# Print Summary
# ==========================================

def print_summary(results):

    print()
    print("=" * 70)
    print("FINAL SECURITY TEST SUMMARY")
    print("=" * 70)

    for index, result in enumerate(results, start=1):

        print()

        print(
            f"Attack {index}: "
            f"{result['attack_name']}"
        )

        print("\nBefore Mitigation:")

        print(
            result["before_mitigation"]
        )

        print("\nAfter Mitigation:")

        print(
            result["after_mitigation"]
        )

        print("-" * 70)


# ==========================================
# Main Program
# ==========================================

def main():

    print()
    print("=" * 70)
    print("JOB LISTING PROMPT INJECTION SECURITY TEST")
    print("=" * 70)


    # Test normal job listing
    test_normal_job()


    # Run injection attacks
    results = run_injection_tests()


    # Save results
    save_results(results)


    # Display summary
    print_summary(results)


    print()
    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()