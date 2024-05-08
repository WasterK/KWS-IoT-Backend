from Database_Access import DatabaseAccess

db = DatabaseAccess(database_url="postgres://admin:OpJDk0pEeegH9dqDkYA7BCWOE8XYoeMB@dpg-cockj5fsc6pc73d1q1m0-a.singapore-postgres.render.com/device_manag_db")

class User:
    def __init__(self, id_, name, email, profile_pic, is_active=True):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.is_active = is_active

    @staticmethod
    def get(user_id):
        userDetails = db.get_user_detials(user_id)
        # print(f"user data from db {userDetails}")
        name = userDetails['name']
        email = userDetails['email']
        profile_pic = userDetails['image']
        return User(user_id, name, email, profile_pic)

    @staticmethod
    def create(id_, name, email, profile_pic):
        # This method should add a new user to the database
        # For demonstration purposes, let's just print the user info
        print(f"Creating user: {name}, {email}")

    def is_authenticated(self):
        # Return True if the user is authenticated, False otherwise
        return True  # Modify this based on your authentication logic

    def is_active(self):
        # Return True if the user is active, False otherwise
        return self.is_active

    def is_anonymous(self):
        # Return True if the user is anonymous, False otherwise
        return False  # We don't have anonymous users in this example

    def get_id(self):
        # Return the user ID, typically a string or integer
        return str(self.id)