import sys
import os

'''Takes an IP and converts it into a 32 bit hex string'''
def convert_ip(ip):
  octets = ip.split('.') #split into octets
  
  # Convert each octet to hexadecimal and join them together
  hex_ip = ''.join(format(int(octet), '02x') for octet in octets)
  return hex_ip

def read_datagram(datagram_filename):
  with open(datagram_filename, 'rb') as file:
    data_hex = file.read(8)
    data_hex = data_hex.hex()
    
    file.seek(8)
    data = file.read()
  return data, data_hex

def calculate_checksum(hex_string):
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

def test_checksum(checksum_incoming, checksum_test, datagram_info):
  if checksum_incoming == checksum_test :
    print(f"Datagram from source-address {datagram_info[0]} source-port {datagram_info[1]} to to dest-address {datagram_info[2]} dest-port {datagram_info[3]}; Length {datagram_info[4]} bytes.")
    return True
  else:
    print("Checksum Error")
    print(checksum_test)
    return False

def convert_to_decimal(hex_num):
  converted_num = int(hex_num, 16)
  return converted_num

def trim_data(data, length):
  length_dec = (int(length, 16) - 8) #remove header bytes
  data_length = len(data)//2 #account for 2 hex per char

  if not length_dec == data_length: #compare expected size, to current size
    padding = data_length - length_dec #calculate difference in sizes
    data = data[:-2*padding] #string trim every two characters per difference in size
  
  return data

def write_data(data):
  #create folder if it doesnt exist
  if not os.path.exists('Output') :
    os.makedirs('Output')
    
  with open('Output/output file', 'wb') as file:
    file.write(data)

def convert_data(data):
  '''takes in a raw binary data file and converts it into a 16 bit divisible hex string (pads with 0 if not even number of byte)'''

  #deliniate out every two characters
  hex_chunks = [hex(int.from_bytes(data[i:i+2], byteorder='big'))[2:] for i in range(0, len(data), 2)]
  hex_data = ''.join(hex_chunks) #add to one string
  
  #pad with zero if neccisarry
  padding_length = (4 - len(hex_data) % 4) % 4
  hex_data += '00' * padding_length
  return hex_data

def main():
  #get input from command line, has defaults
  src_ip_input = "192.168.52.4" if len(sys.argv) < 2 else sys.argv[1]
  dst_ip_input = "192.168.35.10" if len(sys.argv) < 3 else sys.argv[2]
  datagram_name = "Output/datagram" if len(sys.argv) < 4 else sys.argv[3]
  
  #read data
  data, datagram_hex = read_datagram(datagram_name)
  
  #get in hex format
  src_ip_hex = convert_ip(src_ip_input)
  dst_ip_hex = convert_ip(dst_ip_input)
  data_hex = convert_data(data)
  src_port_hex = datagram_hex[:4]
  dst_port_hex = datagram_hex[4:8]
  udp_length_hex = datagram_hex[8:12]
  checksum_incoming_hex = datagram_hex[12:16]
  
  #initialize psuedo header
  checksum_test = '0000'
  zeros = '00' #sets zeros
  protocol = '18' #
  psuedo_length = '000C' #000C for length of 12dec bytes
  
  #create a psuedo_header and the information needed for checksum
  psuedo_header = ''.join([src_ip_hex, dst_ip_hex, zeros, protocol, psuedo_length]) #create a string of the information contained in psuedo header
  checksum_data = ''.join([psuedo_header, src_port_hex, dst_port_hex, udp_length_hex, checksum_test, data_hex]) #string for the information in psuedo header, udp header, data
  
  #calculate the checksum of the recieved data
  checksum_test = calculate_checksum(checksum_data)
  
  #convert information to user readable
  src_port_dec = convert_to_decimal(src_port_hex)
  dst_port_dec = convert_to_decimal(dst_port_hex)
  udp_length_dec = convert_to_decimal(udp_length_hex)
  datagram_information = [src_ip_input, dst_ip_input, src_port_dec, dst_port_dec, udp_length_dec]
  
  #test that the checksums match and print corrisponding output
  if(test_checksum(checksum_incoming_hex, checksum_test, datagram_information)) :
    data_trimmed = trim_data(data, udp_length_hex)
    write_data(data_trimmed)
  else:
    write_data(b'Fail')
  
if __name__ == "__main__":
  main()