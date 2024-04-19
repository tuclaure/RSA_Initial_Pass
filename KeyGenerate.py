import sys
import random
import math
from sympy import nextprime, mod_inverse
import base64
from os import path
from os import makedirs

def generate_prime(bits):
  """Generates a prime integer with a specified bit size"""
  while True:
    candidate = random.getrandbits(bits) #get a random integer with specified bits
    prime = nextprime(candidate) #get the next prime from that integer
    if prime.bit_length() == bits: #make sure its the right bit length
      return prime

def generate_keypair(bits):
  """Creates A Public/Private Key Pair 
  
  Arguments
  bits: size for p and q random assignment
  Returns
  Public Key; Private Key, as two tupples (n,e) (n,d)
  """
  p = generate_prime(bits//2) #get a prime for p (half the bitsize so its multiple is about the bit size)
  while True: #loop for improper p and q
    q = generate_prime(bits//2) #generate q
    n = p * q #create n
    if not p == q and n.bit_length() == bits: #make sure p and q are unique, and n is the correct length
      break
  
  z = (p - 1) * (q - 1) #calculate z
  # e such that 1 < e < z and gcd(e, z) = 1 (e coprime)
  e = random.randrange(2, z)
  while math.gcd(e, z) != 1:
      e = random.randrange(2, z)
  # e = 65537 #using a set e for simplicity

  # Calculate d as the modular inverse of e mod z
  d = mod_inverse(e, z)

  return n, e , d
  
def write_keys(n, e, d):
  #create folder if it doesnt exist
  if not path.exists('Output') :
    makedirs('Output')
    
  #convert each number to bytes
  e_bytes = e.to_bytes((e.bit_length() + 7) // 8, byteorder='big')
  n_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
  d_bytes = d.to_bytes((d.bit_length() + 7) // 8, byteorder='big')
  
  # Encode bytes to Base64
  e_base64 = base64.b64encode(e_bytes)
  n_base64 = base64.b64encode(n_bytes)
  d_base64 = base64.b64encode(d_bytes)
  
  # Write Base64 encoded public_key to PEM file
  with open('Output/public_key.pem', 'w') as pem_file:
    pem_file.write("-----BEGIN PUBLIC KEY-----\n")
    pem_file.write(n_base64.decode('utf-8') + "\n")
    pem_file.write(e_base64.decode('utf-8') + "\n")
    pem_file.write("-----END PUBLIC KEY-----\n")
    
  # Write Base64 encoded private_key to PEM file
  with open('Output/private_key.pem', 'w') as pem_file:
    pem_file.write("-----BEGIN PUBLIC KEY-----\n")
    pem_file.write(n_base64.decode('utf-8') + "\n")
    pem_file.write(d_base64.decode('utf-8') + "\n")
    pem_file.write("-----END PUBLIC KEY-----\n")

def get_user_key_size():
  """gets a key size from the user
  Key must be >= 512 and evenly % by 2
  Protections in place for this"""
  while(True):
    try:
      key_size = input("Key Size: ") #ask for user input
      key_size = int(key_size) #convert to int
      if key_size >= 512 and key_size%2 == 0: #make sure its within size and division parameters
        break
      else :
        raise Exception("Key Size must be > 512 and %2")
    except Exception as e:
      print(f"Invalid input: {e}")
  return key_size
  
def run_generator(*args):
  """Fucntion to call and use all other functions"""
  if len(sys.argv) > 1 : #for command line use
    key_size = int(sys.argv[1]) #command line key size
  else:
    key_size = get_user_key_size() #user use for key size
    
  n, e, d = generate_keypair(key_size) #create the key numbers
  write_keys(n, e, d) #write them

if __name__ == "__main__":
  run_generator()