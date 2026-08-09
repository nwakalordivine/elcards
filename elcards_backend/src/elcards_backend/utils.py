from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def create_password_hash(new_password):
    return password_hash.hash(new_password)


def verify_user_password(password, hash):
    return password_hash.verify(password=password, hash=hash)