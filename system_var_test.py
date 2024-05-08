import os

# Access the DATABASE_URL environment variable
database_url = os.environ.get('GOOGLE_CLIENT_ID')

if database_url:
    print("google cliend id:", type(database_url))
else:
    print("DATABASE_URL environment variable is not set.")
