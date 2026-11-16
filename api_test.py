from google import genai

client = genai.Client()

response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="explain api keys in one sentence.")
print(response.text)
