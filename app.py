import os
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import VULNERABLE_PROMPT
from mitigation import build_secure_prompt
from attacks import NORMAL_JOB, ATTACKS
from evaluator import evaluate_injection
from test_results import save_results


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Job Injection Security Tester",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Job Listing Prompt Injection Security Tester")

st.write(
    "Test how a job-listing prompt responds to injection attempts. "
    "Compare the results before and after applying the mitigation."
)

st.info(
    "**Security principle:** User input is data, never an instruction."
)


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file and restart the app."
    )
    st.stop()


# ==========================================
# Gemini Client and Model
# ==========================================

client = genai.Client(api_key=api_key)

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

    return response.text or "The model returned an empty response."


# ==========================================
# Run Injection Tests
# ==========================================

def run_injection_tests():

    results = []

    for attack in ATTACKS:

        attack_name = attack["name"]
        attack_input = attack["input"]

        # ------------------------------
        # Before mitigation
        # ------------------------------

        vulnerable_response = ask_ai(
            VULNERABLE_PROMPT,
            attack_input
        )

        before_obeyed = evaluate_injection(
            attack_name,
            vulnerable_response
        )

        # ------------------------------
        # After mitigation
        # ------------------------------

        secure_prompt = build_secure_prompt(
            attack_input
        )

        secure_response = ask_ai(
            secure_prompt,
            attack_input
        )

        after_obeyed = evaluate_injection(
            attack_name,
            secure_response
        )

        # ------------------------------
        # Store results
        # ------------------------------

        results.append({
            "attack_name": attack_name,
            "malicious_input": attack_input,

            "before_mitigation": {
                "response": vulnerable_response,
                "injection_obeyed": before_obeyed
            },

            "after_mitigation": {
                "response": secure_response,
                "injection_obeyed": after_obeyed
            }
        })

    return results


# ==========================================
# Display Evaluation Status
# ==========================================

def show_status(obeyed):

    if obeyed:
        st.error("Injection obeyed: Yes")
    else:
        st.success("Injection obeyed: No")


# ==========================================
# Normal Job Listing Test
# ==========================================

st.header("1. Normal Job Listing Test")

st.write("Enter a job search query below.")

user_query = st.text_input(
    "Job search query",
    value=NORMAL_JOB,
    placeholder="Enter your job search query here"
)

if st.button("Run Normal Job Test", type="primary"):

    if not user_query.strip():

        st.warning("Please enter a job search query.")

    else:

        with st.spinner("Requesting a response from Gemini..."):

            try:

                normal_response = ask_ai(
                    VULNERABLE_PROMPT,
                    user_query
                )

                st.subheader("AI Response")
                st.write(normal_response)

            except Exception as error:

                st.error(
                    f"Normal test failed: {error}"
                )


st.divider()


# ==========================================
# Prompt Injection Security Tests
# ==========================================

st.header("2. Prompt Injection Security Tests")

st.write(
    "Run the configured injection attempts. "
    "Each test is evaluated before and after mitigation."
)

if st.button(
    "Run All Injection Tests",
    type="primary"
):

    try:

        with st.spinner(
            "Running injection tests. "
            "This may take a little while..."
        ):

            results = run_injection_tests()

        st.session_state["injection_results"] = results

        try:

            save_results(results)

            st.success(
                "Test results saved successfully."
            )

        except Exception as error:

            st.warning(
                f"Could not save results to file: {error}"
            )

    except Exception as error:

        st.error(
            f"Injection testing failed: {error}"
        )


# ==========================================
# Display Injection Test Results
# ==========================================

if "injection_results" in st.session_state:

    results = st.session_state["injection_results"]

    st.subheader("3. Test Results")

    for index, result in enumerate(
        results,
        start=1
    ):

        with st.expander(
            f"Attack {index}: {result['attack_name']}",
            expanded=True
        ):

            st.markdown("**Malicious input:**")

            st.code(
                result["malicious_input"],
                language="text"
            )

            col1, col2 = st.columns(2)

            # ==================================
            # Before Mitigation
            # ==================================

            with col1:

                st.markdown(
                    "### Before Mitigation"
                )

                st.markdown(
                    "**AI Response:**"
                )

                st.write(
                    result[
                        "before_mitigation"
                    ]["response"]
                )

                show_status(
                    result[
                        "before_mitigation"
                    ]["injection_obeyed"]
                )

            # ==================================
            # After Mitigation
            # ==================================

            with col2:

                st.markdown(
                    "### After Mitigation"
                )

                st.markdown(
                    "**AI Response:**"
                )

                st.write(
                    result[
                        "after_mitigation"
                    ]["response"]
                )

                show_status(
                    result[
                        "after_mitigation"
                    ]["injection_obeyed"]
                )

            st.caption(
                "The evaluation reflects the result returned "
                "by your evaluate_injection() function."
            )


    # ==========================================
    # Final Summary
    # ==========================================

    st.divider()

    st.subheader("4. Final Summary")

    for result in results:

        before = result[
            "before_mitigation"
        ]["injection_obeyed"]

        after = result[
            "after_mitigation"
        ]["injection_obeyed"]

        st.write(
            f"**{result['attack_name']}**"
        )

        st.write(
            "Before mitigation: "
            f"{'Obeyed' if before else 'Not obeyed'}"
        )

        st.write(
            "After mitigation: "
            f"{'Obeyed' if after else 'Not obeyed'}"
        )

    st.info(
        "Review the actual responses as well as the "
        "evaluator's labels. The labels are only as "
        "reliable as your evaluation function."
    )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "Job Listing Prompt Injection Security Testing Project"
)