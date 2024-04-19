from os import path
from os import makedirs
import base64
import sys

def get_user_input(prompt):
  """Gets a user input for a file path, checks that file exists before allowing return"""
  while(True):
    user_input = input(prompt)
    if path.isfile(user_input):
      return user_input
    else :
      print("Invalid Input")

def read_plain_text(path):
  """Reads in plain text to a string from a pre checked path"""
  try:
    with open(path, 'rb') as file:
      plain_text = file.read()
  except Exception as e:
    print(f"{e}")
    new_path = get_user_input("Text Path: ")
    plain_text = read_plain_text(new_path)
  return plain_text
  
def read_public_key(path):
  """Reads in a public key into a tupple
  Checks for the prescence of a Header and Footer
  Otherwise gets a new file and recursively uses itself
  """
  try:
    read_numbers = []
    with open(path, 'r') as pem_file:
      for line in pem_file:
        line = line.strip()
        if line and line != "-----BEGIN PUBLIC KEY-----" and line != "-----END PUBLIC KEY-----":
          read_numbers.append(base64.b64decode(line))
    # Decode bytes back to integers
    decoded_n = int.from_bytes(read_numbers[0], byteorder='big')
    decoded_e = int.from_bytes(read_numbers[1], byteorder='big')
  except Exception as e:
    print(f"{e}")
    new_path = get_user_input("Public Key Path: ")
    decoded_n, decoded_e = read_public_key(new_path)
  return (decoded_n, decoded_e)

def write_cipher_text(cipher):
  """Writes out the encrypted text to CWD as cipher.enc"""
  #create folder if it doesnt exist
  if not path.exists('Output') :
    makedirs('Output')
    
  with open('Output/cipher.enc', 'wb') as file:
    file.write(cipher)
  
def encrypt(message, public_key):
  """Encrypts message = M^e mod n
  
  Arguments:
    message: String
    public_key: tupple holding n and e
  
  Returns:
    ciphertext: list containing n byte encrypted chunks at each index"""

  n, e = public_key
  chunk_size = n.bit_length() // 8  # Calculate the maximum chunk size based on the modulus size
  bit_size = chunk_size #(n.bit_length() + 7) // 8
  ciphertext = b""
  
  for i in range(0, len(message), chunk_size):
    chunk = message[i:i + chunk_size]
    chunk_byte = int.from_bytes(chunk)
    ciphertext += pow(chunk_byte, e, n).to_bytes(bit_size, 'big')
    
  return ciphertext

def run_encrypt(*args):
  """Executes the encryption program using internal functions"""
  
  if len(sys.argv) > 1:
    text_path = sys.argv[1]
    key_path = 'Output/public_key.pem' if len(sys.argv) < 3 else sys.argv[2]
  else:
    text_path = get_user_input("Text Path: ")
    key_path = get_user_input("Public Key Path: ")
      
  plain_text = read_plain_text(text_path)
  key = read_public_key(key_path)
  cipher = encrypt(plain_text, key)
  write_cipher_text(cipher)

if __name__ == "__main__":
  run_encrypt()