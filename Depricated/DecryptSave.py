from os import path
from os import makedirs
import sys
import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes


def get_user_input(prompt):
  """Gets a user input for a file path, checks that it exists before allowing return"""
  while(True):
    user_input = input(prompt)
    if path.isfile(user_input):
      return user_input
    else :
      print("Invalid Input")
      
def get_cipher_text(path):
  """reads encrypted text from a ciphered file"""
  try:
    with open(path, 'rb') as file:
      cipher_text = file.read()
  except Exception as e:
    print("File not supported: ", e)
    print(path)
    new_path = get_user_input("Text Path: ")
    cipher_text = get_cipher_text(new_path)
  return cipher_text

def write_plain_text(plain_text):
  """writes decrypted plain text to a file called decrypted.txt"""
  #create folder if it doesnt exist
  if not path.exists('Output') :
    makedirs('Output')
    
  with open('Output/decrypted', 'wb') as file:
    file.write(plain_text)

def read_private_key(path):
  """reads in a private key
  File must have header and footer"""
  try:
    read_numbers = []
    with open(path, 'r') as pem_file:
      for line in pem_file:
        line = line.strip()
        if line and line != "-----BEGIN PUBLIC KEY-----" and line != "-----END PUBLIC KEY-----":
          read_numbers.append(base64.b64decode(line))
    # Decode bytes back to integers
    decoded_n = int.from_bytes(read_numbers[0], byteorder='big')
    decoded_d = int.from_bytes(read_numbers[1], byteorder='big')
  except Exception as e:
    print("Invalid Private Key")
    new_path = get_user_input("Private Key Path: ")
    decoded_n, decoded_d = read_private_key(new_path)
  return decoded_n, decoded_d
  
def decrypt(cipher, private_key):
  """Decrypts Text = C^d mod n
  iterates through the cipher applying the decryption algo
  converts to a character adding it to final
  
  Arguments:
    cipher: list of n byte encrypted chunks
    private_key: tupple holding n and d
    
  Returns:
    decrypted_text: byte holding the decrypted message
  """
  n, d = private_key
  try:    
    plaintext = b""
    chunk_size = n.bit_length() // 8  # Calculate the maximum chunk size based on the modulus size
    
    for i in range(0, len(cipher), chunk_size):
      chunk = cipher[i:i+chunk_size]
      m = int.from_bytes(chunk)
      decrypted = pow(m, d, n)
      plaintext += decrypted.to_bytes((decrypted.bit_length()+7)//8, 'big')

  except OverflowError as e:
    print("That Key Is not Valid for this file")
    print(e)
    new_path = get_user_input("Private Key Path: ")
    new_key = read_private_key(new_path)
    plaintext = decrypt(cipher, new_key)
  return plaintext
    
  
def run_decrypt():
  """manages function use to actually run the decryption program"""
  if len(sys.argv) > 1:
    text_path = sys.argv[1]
    key_path = 'Output/private_key.pem' if len(sys.argv) < 3 else sys.argv[2]
  else:
    text_path = get_user_input("Cipher Text Path: ")
    key_path = get_user_input("Private Key Path: ")
    
    
  cipher_text = get_cipher_text(text_path)
  key = read_private_key(key_path)
  plain_text = decrypt(cipher_text, key)
  write_plain_text(plain_text)
  
if __name__ == "__main__":
  run_decrypt()