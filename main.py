import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions
from prompts import system_prompt


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        )
    )

    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")

    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count

    if args.verbose:
        print("User prompt: ", args.user_prompt)
        print("Prompt tokens: ", prompt_tokens)
        print("Response tokens: ", response_tokens)
    
    if not response.function_calls:
        print("Response:")
        print(response.text)
        return

    function_results = []
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose=args.verbose)

        if not function_call_result.parts:
            raise RuntimeError("Function call returned Content with empty parts list")

        first_part = function_call_result.parts[0]
        if first_part.function_response is None:
            raise RuntimeError("Function call part has no FunctionResponse")

        if first_part.function_response.response is None:
            raise RuntimeError("FunctionResponse has no response payload")

        function_results.append(first_part)

        if args.verbose:
            print(f"-> {first_part.function_response.response}")


if __name__ == "__main__":
    main()
