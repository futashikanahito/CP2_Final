from cryptography.fernet import Fernet as F

def get_key():
    key = F.generate_key()
    f = F(key)
    return f

def encryption(f,Text):
    etext = f.encrypt(Text)
    return etext

def decryption(f, Text):
    origin_text = f.decrypt(Text)
    return origin_text

f = get_key()
print(f)
encrypted = encryption(f,b"This is text")
print(encrypted)
decrypted = decryption(f,encrypted)
print(decrypted)