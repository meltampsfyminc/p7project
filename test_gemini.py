import os
import sys
import google.generativeai as genai

# Best practice: load the API key from an environment variable
try:
    # The client gets the API key from the environment variable `GOOGLE_API_KEY`.
    # To set it in your terminal:
    # export GOOGLE_API_KEY="YOUR_API_KEY"  (on Linux/macOS)
    # set GOOGLE_API_KEY="YOUR_API_KEY"     (on Windows Command Prompt)
    # $env:GOOGLE_API_KEY="YOUR_API_KEY"   (on Windows PowerShell)
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    sys.exit("Error: GOOGLE_API_KEY environment variable not set.")

# Create a model instance
model = genai.GenerativeModel('gemini-flash-latest')

# Get the prompt from command-line arguments, or use a default.
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
else:
    sys.exit("Usage: python test_gemini.py <your prompt here>")

print(f"\n--- Sending Prompt ---\n{prompt}\n")
print("--- Gemini's Response ---")

# Generate content
response = model.generate_content("Explain how AI works in a few words")
response = model.generate_content(prompt)
print(response.text)