import bcrypt
import jwt

# Need to hide secret signature
def generateToken(username):
    return jwt.encode(username, 'datica')

def generatePassword(password):
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashedPassword

def validatePassword(reqPassword, hashedPassword):
    if bcrypt.checkpw(reqPassword.encode('utf-8'), hashedPassword):
        return True
    else: 
        return False