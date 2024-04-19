import subprocess

def compare(plaintext_file, decrypted_file, information_flag):
  file_contents_equal = False
  
  with open(plaintext_file, 'rb') as file:
    plaintext = file.read()
    plaintext_length = len(plaintext)

  with open(decrypted_file, 'rb') as file:
    decrypted_text = file.read()
    decrypted_text_length = len(decrypted_text)

  
  if(decrypted_text == plaintext):
    file_contents_equal = True
  else:
    file_contents_equal = False
  
  if(information_flag):
    print()
    print("Original size: ", plaintext_length)
    print("Decrypted size: ", decrypted_text_length)
    if(file_contents_equal):
      print("Original and Decrypted files are the same")
    else:
      print("Original and Decrypted files differ")
    
  return file_contents_equal


def cipher_process(name_package, flag_package):
  
  plaintext_file = name_package[0]
  encrypted_file = name_package[1]
  decrypted_file = name_package[2]
  
  key_size = flag_package[0]
  generate_keys = flag_package[1]
  show_comparison = flag_package[2]
  iterations = flag_package[3]
  
  success = 0
  fail = 0
  
  for i in range(0, iterations):
    if(generate_keys):
      subprocess.call(["python", 'KeyGenerate.py', key_size])
    subprocess.call(["python", 'Encrypt.py', plaintext_file])
    subprocess.call(["python", 'Decrypt.py', encrypted_file])
  
    if(compare(plaintext_file, decrypted_file, show_comparison)) :
      success +=1
    else:
      fail += 1
  
  if(show_comparison):
    print(f'S:{success} F:{fail}')
  
  
def send_recieve(filename, ip1, ip2, port1, port2, ip3, ip4, datagram_file):
  subprocess.call(["python", 'Sender.py', filename, ip1, ip2, port1, port2])
  subprocess.call(["python", 'Reciever.py', ip3, ip4, datagram_file])
  compare(filename, 'Output/output file', True)
    

def full_process(name_package, flag_package, sender_package, reciever_package):
  plaintext_file = name_package[0]
  encrypted_file = name_package[1]
  datagram_file = name_package[2]
  output_file = name_package[3]
  decrypted_file = name_package[4]
  
  key_size = flag_package[0]
  generate_keys = flag_package[1]
  show_comparison = flag_package[2]
  iterations = flag_package[3]
  success = 0
  fail = 0

  for i in range(0, iterations) :
    if(generate_keys):
      subprocess.call(["python", 'KeyGenerate.py', key_size])
    subprocess.call(["python", 'Encrypt.py', plaintext_file])
    subprocess.call(["python", 'Sender.py', encrypted_file] + sender_package)
    print()
    subprocess.call(["python", 'Reciever.py'] + reciever_package + [datagram_file])
    subprocess.call(["python", 'Decrypt.py', output_file])
  
    if(compare(plaintext_file, decrypted_file, show_comparison)):
      success += 1
    else:
      fail += 1

  if(show_comparison) :
    print(f'S:{success} F:{fail}')
  
if __name__ == "__main__":
  #File Names
  plaintext_file = 'PlainFiles/' + 'allbytes'
  encrypted_file = 'Output/' + 'cipher.enc'
  datagram_file = 'Output/' + 'datagram'
  output_file = 'Output/' + 'output file'
  decrypted_file = 'Output/' + 'decrypted'
  cipher_test_package = [plaintext_file, encrypted_file, decrypted_file]
  complete_name_package = [plaintext_file, encrypted_file, datagram_file, output_file, decrypted_file]
  
  #Flags and associated variables
  key_size = '1024'
  generate_keys = True
  show_comparison = True
  iterations = 1
  flag_package = [key_size, generate_keys, show_comparison, iterations]
  
  #Ips and Ports
  src_ip ='192.168.52.4'
  dst_ip = '192.168.35.10'
  src_port = '2300'
  dst_port = '23450'
  bad_ip = '100.10.198.2'
  sender_package = [src_ip, dst_ip, src_port, dst_port]
  reciever_package = [src_ip, dst_ip]
  bad_reciever_package = [bad_ip, dst_ip]
  
  
  # cipher_process(cipher_test_package, flag_package)
  full_process(complete_name_package, flag_package, sender_package, reciever_package)
  
  #cat test (output file needs to be retitled as a .jpg to read as a human)
  # send_recieve('PlainFiles/cat.jpg','192.168.52.4','192.168.35.10', '2300', '23540', '192.168.52.4','192.168.35.10','Output/datagram')
  
  #test case 1 Sending Allbytes
  # send_recieve('PlainFiles/allbytes','192.168.52.4','192.168.35.10', '2300', '23540', '192.168.52.4','192.168.35.10','Output/datagram')
  
  #test case 2 Checksum Calculation and test case 4 padding
  # send_recieve('PlainFiles/oddchars','192.168.52.4','192.168.35.10', '2300', '23540', '192.168.52.4','192.168.35.10','Output/datagram')
  
  #test case 3 Invalid datagram
  # send_recieve('PlainFiles/oddchars','192.168.52.4','192.168.35.10', '2300', '23540', '192.168.52.4','100.100.10.1','Output/datagram')
  
  #test case 5 Encryption
  # complete_name_package[0] = plaintext_file = 'PlainFiles/' + 'oddchars'
  # full_process(complete_name_package, flag_package, sender_package, reciever_package)

  