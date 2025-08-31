# -*- coding: utf-8 -*-
"""
Handles interaction with the Perplexity AI API.
"""
import requests
import os
from dotenv import load_dotenv
from scripts.config import (
    PERPLEXITY_INPUT_FILE, PERPLEXITY_OUTPUT_FILE,
    PERPLEXITY_MODEL, PERPLEXITY_SYSTEM_PROMPT, PERPLEXITY_API_ENDPOINT
)
from scripts.modules.file_operations import FileManager

class Perplexity:
    """A class to handle Perplexity AI API interactions."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.url = PERPLEXITY_API_ENDPOINT

    def _read_query(self):
        """Reads the query from the configured input file."""
        FileManager().ensure_file_exists(PERPLEXITY_INPUT_FILE)
        with open(PERPLEXITY_INPUT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _write_response(self, response_data):
        """Writes the response content and citations to the configured output file."""
        FileManager().ensure_file_exists(PERPLEXITY_OUTPUT_FILE)
        
        content = "Error: Could not extract a valid response."
        if response_data and 'choices' in response_data and response_data['choices']:
            content = response_data['choices'][0]['message']['content']
        
        citations = response_data.get('citations')
        
        with open(PERPLEXITY_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
            if citations and isinstance(citations, list):
                f.write("\n\n" + "="*40 + "\n")
                f.write("## Citations\n\n")
                for i, citation in enumerate(citations, 1):
                    if isinstance(citation, dict):
                        title = citation.get('title', 'N/A')
                        url = citation.get('url', '#')
                        f.write(f"{i}. **{title}**: [{url}]({url})\n")
                    else:
                        f.write(f"{i}. {citation}\n")

    def run(self):
        """Executes the Perplexity query and writes the response."""
        print("Starting Perplexity script...")
        if not self.api_key:
            error_message = "PERPLEXITY_API_KEY not found in environment. Please add it to your .env file."
            print(f"ERROR: {error_message}")
            self._write_response(error_message)
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print("Reading query from file...")
        query = self._read_query()
        if not query:
            error_message = "Input file is empty. Please provide a query."
            print(f"ERROR: {error_message}")
            self._write_response(error_message)
            return False
        print(f"Query: {query}")

        payload = {
            "model": PERPLEXITY_MODEL,
            "messages": [
                {"role": "system", "content": PERPLEXITY_SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        }

        print("Sending request to Perplexity API...")
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data and 'choices' in response_data and response_data['choices']:
                self._write_response(response_data)
                print("Request successful.")
                return True
            else:
                error_message = "Error: Could not extract a valid response from the API."
                print(error_message)
                self._write_response({"choices": [{"message": {"content": error_message}}]})
                return False

        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            self._write_response(error_message)
            return False
        finally:
            print("Script finished.")

def main():
    """Main function to run the Perplexity script."""
    perplexity_instance = Perplexity()
    perplexity_instance.run()

if __name__ == "__main__":
    main()