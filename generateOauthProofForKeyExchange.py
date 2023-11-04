import secrets
import hashlib
import base64

code_verifier = secrets.token_urlsafe(50)
print("Code Verifier:", code_verifier)

# Generate a code verifier (as shown in the previous step)
#code_verifier = "your_generated_code_verifier"

# Hash the code verifier using SHA-256
code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()

# Base64 encode the hashed code challenge
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).rstrip(b'=').decode()
print("Code Challenge:", code_challenge)
