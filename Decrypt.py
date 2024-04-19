from os import path
from os import makedirs
import sys
import base64

def get_user_input(prompt):
  """Gets a user input for a file path, checks that it exists before allowing return"""
  while(True):
    user_input = input(prompt) #user input
    if path.isfile(user_input): #checks file is valid
      return user_input
    else :
      print("Invalid Input")
      
def get_cipher_text(path):
  """reads encrypted text from a ciphered file"""
  try:
    with open(path, 'rb') as file: #reads in cipher as binary
      cipher_text = file.read()
  except Exception as e:
    print("File not supported: ", e)
    print(path)
    new_path = get_user_input("Text Path: ") #gets new user input
    cipher_text = get_cipher_text(new_path) #recurersion with new location
  return cipher_text

def write_plain_text(plain_text):
  """writes decrypted plain text to a file called decrypted.txt"""
  #create folder if it doesnt exist
  if not path.exists('Output') :
    makedirs('Output')
    
  with open('Output/decrypted', 'wb') as file: #always reads binary from the location Output/decrypted
    file.write(plain_text)

def read_private_key(path):
  """reads in a private key
  File must have header and footer"""
  try:
    read_numbers = [] #to seperate key numbers
    with open(path, 'r') as pem_file: #reads pem file as a string (Not the problem, the produced key is correct and works with other files)
      for line in pem_file: #iterates through string
        line = line.strip() #strips
        if line and line != "-----BEGIN PUBLIC KEY-----" and line != "-----END PUBLIC KEY-----": #looks for header and footer
          read_numbers.append(base64.b64decode(line)) #reads them as decoded bytes
    # Decode bytes back to integers
    decoded_n = int.from_bytes(read_numbers[0], byteorder='big')
    decoded_d = int.from_bytes(read_numbers[1], byteorder='big')
  except Exception as e:
    print("Invalid Private Key")
    new_path = get_user_input("Private Key Path: ") #recursion with new path
    decoded_n, decoded_d = read_private_key(new_path)
  return decoded_n, decoded_d
  
def decrypt(cipher, private_key):
  """Decrypts a message using a private_key
  
  Arguments:
    cipher: list of n byte encrypted chunks
    private_key: tupple holding n and d
    
  Returns:
    decrypted_text: byte string holding the decrypted message
  """
  n, d = private_key #aquires n and d from key 
  message_base64 = b"" #byte string
  chunk_size = n.bit_length() // 8  # Calculate the maximum chunk size based on the modulus size
  
  for i in range(0, len(cipher), chunk_size): #loops through chunks
    cipher_chunk = cipher[i:i+chunk_size] #gets chunk from message
    cipher_int = int.from_bytes(cipher_chunk, 'big') #converts to integer
    plain_int = pow(cipher_int, d, n) #performs m^d mod n
    plain_chunk = plain_int.to_bytes(chunk_size, 'big') #casts back as bytes within allowable size
    message_base64 += plain_chunk #append
  message = base64.b64decode(message_base64) #decode from base 64
  return message
  
  # #remove and store null locations
  # null_locations = []
  # cipher_array = bytearray(cipher)
  # for i, byte in enumerate(cipher_array) :
  #   if byte == 0 :
  #     del cipher_array[i]
  #     null_locations.append(i)
  # cipher = bytes(cipher_array)
      
  # for i in range(0, len(cipher), chunk_size): #loops through chunks
  #   cipher_chunk = cipher[i:i+chunk_size] #gets chunk from message
  #   cipher_int = int.from_bytes(cipher_chunk, 'big') #converts to integer
  #   plain_int = pow(cipher_int, d, n) #performs m^d mod n
  #   plain_chunk = plain_int.to_bytes((plain_int.bit_length()+7)//8, 'big') #casts back as bytes within allowable size
  #   plaintext += plain_chunk #append
      
  # #Re add null characters from location
  # plaintext_array = bytearray(plaintext)
  # for location in null_locations :
  #   plaintext_array.insert(location, 0)
  #   print(location)
  # plaintext_complete = bytes(plaintext_array)      
      
  # return plaintext_complete
    
def run_decrypt():
  """manages function use to actually run the decryption program"""
  if len(sys.argv) > 1: #for command line input
    text_path = sys.argv[1] #file from command line
    key_path = 'Output/private_key.pem' if len(sys.argv) < 3 else sys.argv[2] #key from cmd line, has default
  else:
    text_path = get_user_input("Cipher Text Path: ") #user file
    key_path = get_user_input("Private Key Path: ") #user key
    
    
  cipher_text = get_cipher_text(text_path) #gets cipher as byte string
  key = read_private_key(key_path) #gets key as tupple (n, d)
  plain_text = decrypt(cipher_text, key) #decrypts plain text from byte string and key
  write_plain_text(plain_text) #writes decrypted info as binary
  
if __name__ == "__main__":
  run_decrypt()