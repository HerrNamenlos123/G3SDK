import struct

class BinaryFileBuilder:
    def __init__(self, binary_stream: bytearray = None):
        self.binary_stream = binary_stream

    def add_integer(self, value):
        # Pack the integer value into 4 bytes and append to the binary stream
        self.binary_stream.extend(struct.pack('i', value))

    def write_to_file(self):
        # Write the binary stream to the file
        with open(self.file_path, 'wb') as file:
            file.write(self.binary_stream)
        print("Binary file has been created successfully.")

    def parse_int(self):
        # Extract and remove the bytes for one integer from the binary stream
        if len(self.binary_stream) >= struct.calcsize('i'):
            integer = struct.unpack('i', self.binary_stream[:struct.calcsize('i')])[0]
            self.binary_stream = self.binary_stream[struct.calcsize('i'):]
            return integer
        else:
            raise ValueError("Not enough bytes in the binary stream to extract an integer.")
        
file = BinaryFileBuilder("4")