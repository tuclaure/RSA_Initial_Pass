import sys
import os

def convert_ip(ip):
  '''Takes an IP and converts it into a 32 bit hex string'''

  octets = ip.split('.') #split into octets
  
  # Convert each octet to hexadecimal and join them together
  hex_ip = ''.join(format(int(octet), '02x') for octet in octets)
  return hex_ip

def convert_port(port):
  '''Takes a port and turns it into a 16 bit hex string'''

  #check port is of valid size
  if not 0 <= port <= 65535:
    raise ValueError("Port number must be between 0 and 65535")

  #convert to padded hex
  hex_port = hex(port)[2:].zfill(4)
  return hex_port

def get_data_information(data_filename):
  '''reads in a binary file, returns raw file and its length'''

  with open(data_filename, 'rb') as file:
    data = file.read()
  data_length = len(data)
  return data, data_length

def convert_udp_length(data_length):
  '''takes the length of a data file, converts it into a hex string of udp length (hex and 8 more bytes)'''

   #add 8 bytes to data_length (for header)
  udp_length = data_length + 8
  
  #check the file length is 16 bit compatible
  if not 0 <= udp_length <= 65535:
    raise ValueError("File Too Large")

  #convert to a 16 bit hex number
  hex_udp_length = hex(udp_length)[2:].zfill(4)
  return hex_udp_length

def convert_data(data):
  '''takes in a raw binary data file and converts it into a 16 bit divisible hex string (pads with 0 if not even number of byte)'''

  #deliniate out every two characters
  hex_chunks = [hex(int.from_bytes(data[i:i+2], byteorder='big'))[2:] for i in range(0, len(data), 2)]
  hex_data = ''.join(hex_chunks) #add to one string
  
  #pad with zero if neccisarry
  padding_length = (4 - len(hex_data) % 4) % 4
  hex_data += '0' * padding_length
  return hex_data

def calculate_checksum(hex_string):
  '''takes a hex string of the psuedo header, udp_header and padded data, creates a checksum'''

  # Parse hexadecimal string into 16-bit chunks
  chunks = [int(hex_string[i:i+4], 16) for i in range(0, len(hex_string), 4)]
  
  # Sum up all 16-bit chunks
  total_sum = sum(chunks)
  
  # Add carry until it fits into a hextet
  while total_sum > 0xFFFF:
    total_sum = (total_sum & 0xFFFF) + (total_sum >> 16)
  
  # Take one's complement
  checksum_value = (~total_sum) & 0xFFFF
  
  return hex(checksum_value)[2:].zfill(4)

def write_datagram(datagram, data, datagram_filename):
  '''write datagram to a given file'''
  #create folder if it doesnt exist
  if not os.path.exists('Output') :
    os.makedirs('Output')

  #writing the characters as binary
  binary_data = bytes.fromhex(datagram)
  with open('Output/' + datagram_filename, 'wb') as file:
    file.write(binary_data)
    file.write(data)
  
def print_for_user(information):
  '''debugging method, displays all information being handled in the program'''

  print("Source port: ",information[0])
  print("Destination port: ",information[1])
  # print()
  # print("Big-endian IP:")
  print("Source IP:", information[2])
  print("Destination IP:", information[3])
  # # loop for bytes
  # x= 1
  # for i in range(0, len(information[4]), 2):
  #   substring = information[4][i:i+2]
  #   print(f"Source IP Byte{x}: {int(substring, 16)}")
  #   x += 1
  # x= 1
  # for i in range(0, len(information[5]), 2):
  #   substring = information[5][i:i+2]
  #   print(f"Destination IP Byte{x}: {int(substring, 16)}")
  #   x += 1
  print("file size (Byte without zero padding) ", information[6])
  print("total length(bytes): ", information[7])
  print("checksum: ", information[8])


def main():
  #get input from command line, has defaults
  data_filename = "PlainFiles/oddchars" if len(sys.argv) < 2 else sys.argv[1]
  src_ip_input = "192.168.52.4" if len(sys.argv) < 3 else sys.argv[2]
  dst_ip_input = "192.168.35.10" if len(sys.argv) < 4 else sys.argv[3]
  src_port_input = 2300 if len(sys.argv) < 5 else int(sys.argv[4])
  dst_port_input = 23540 if len(sys.argv) < 6 else int(sys.argv[5])
  datagram_filename = "datagram" if len(sys.argv) < 7 else sys.argv[6]
  
  #convert user input into operable format
  data, data_length = get_data_information(data_filename) #reads in raw data and its length
  total_length_hex = convert_udp_length(data_length) #length of the upd header in hex (data bytes + 8)
  data_hex = convert_data(data) #turns data into a 16 bit divisible hex string (padding and hex conversion)
  src_ip_hex = convert_ip(src_ip_input) #source ip in 32 bit hex 
  dst_ip_hex = convert_ip(dst_ip_input) #destination ip in 32 bit hex
  src_port_hex = convert_port(src_port_input) #source port in 16 bit hex
  dst_port_hex = convert_port(dst_port_input) #destination port in 16 bit hex
  
  #initialize psuedo header and checksum parts
  checksum = '0000' # initialize checksum as 0 in 16 bit hex 
  zeros = '00' #sets zeros
  protocol = '18' #
  psuedo_length = '000C' #000C for length of 12dec bytes
  
  #create a psuedo_header and the information needed for checksum
  psuedo_header = ''.join([src_ip_hex, dst_ip_hex, zeros, protocol, psuedo_length]) #create a string of the information contained in psuedo header
  checksum_data = ''.join([psuedo_header, src_port_hex, dst_port_hex, total_length_hex, checksum, data_hex]) #string for the information in psuedo header, udp header, data
  
  checksum = calculate_checksum(checksum_data) #calculate the checksum
  
  #create the datagram from source port, destination port, total length, checksum
  udp_datagram = ''.join([src_port_hex, dst_port_hex, total_length_hex, checksum]) 
  #write datagram to given file
  write_datagram(udp_datagram, data, datagram_filename)
  
  #for debugging and readout
  information = [src_port_input, dst_port_input, src_ip_input, dst_ip_input, src_ip_hex, dst_ip_hex, data_length, int(total_length_hex, 16), int(checksum, 16)]
  print_for_user(information)
                
if __name__ == "__main__":
  main()
  
