from werkzeug.security import generate_password_hash
hashed_password = generate_password_hash('#Ajs@2007')
print(hashed_password)
