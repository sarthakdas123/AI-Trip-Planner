import os
import groq
import json
from dotenv import load_dotenv

def test_groq_connection():
    """Test the connection to the Groq API"""
    # Load environment variables
    load_dotenv()
    
    # Get Groq API key
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not groq_api_key:
        print("No Groq API key found in .env file")
        print("Please add your Groq API key to the .env file:")
        print("GROQ_API_KEY=your_api_key_here")
        return False
    
    print(f"Found Groq API key: {groq_api_key[:4]}...{groq_api_key[-4:]}")
    
    try:
        # Initialize Groq client
        client = groq.Client(api_key=groq_api_key)
        print("Groq client initialized successfully")
        
        # Test models
        models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
        
        for model in models:
            try:
                print(f"\nTesting model: {model}")
                # Simple test prompt
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say hello and return a simple JSON with your name and the current date."}
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                
                # Print response
                content = response.choices[0].message.content
                print(f"Response from {model}:")
                print(content)
                print("\nTest successful!")
                
                # Try to parse JSON
                try:
                    # Look for JSON in the response
                    import re
                    json_match = re.search(r'({.*})', content.replace('\n', ' '))
                    if json_match:
                        json_str = json_match.group(1)
                        json_obj = json.loads(json_str)
                        print(f"Successfully parsed JSON: {json_obj}")
                    else:
                        print("No JSON found in response")
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                
                return True
                
            except Exception as e:
                print(f"Error testing model {model}: {e}")
                continue
        
        print("\nAll models failed. Please check your API key and try again.")
        return False
        
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connectivity problems")
        print("3. Groq service might be down")
        print("\nPlease check your API key and try again.")
        return False

if __name__ == "__main__":
    print("=== Groq API Connection Test ===")
    success = test_groq_connection()
    
    if success:
        print("\n Groq API connection test passed!")
        print("You can now use the AI Trip Planner with Groq-powered itineraries.")
    else:
        print("\n Groq API connection test failed.")
        print("The application will use mock data for itineraries until this is resolved.")
        print("\nFor help, see groq_api_setup.md")