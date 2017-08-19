import binascii 
#import clamenddi  # assembler module


class Patcher():
    buf = ''
    b8 = lambda self, x: '{:08b}'.format(x)
    b9 = lambda self, x: '{:09b}'.format(x)
    f = None
    size = None
    def __init__(self,file_name):
        self.f = open(file_name, 'rb')
        self.buf = self.f.read()
        if not self.buf:
            self.buf = '\x00'*0x100
        self.size = len(self.buf)
        
    def int2bytes(self,inp):
        X = inp >> 18 & 0x1ff
        Y = inp >> 9 & 0x1ff
        Z = inp >> 0 & 0x1ff
        return [Y,X,Z]

    def read(self, offset, size, ret_type='str'):
        header_bit_offset = offset * 9
        header_byte_offset = header_bit_offset / 8
        header_byte = self.buf[header_byte_offset]
        header_bits = self.b8(ord(header_byte))
        
        tail_bit_offset = offset * 9 + size * 9
        tail_byte_offset = tail_bit_offset / 8
        tail_byte = self.buf[tail_byte_offset]
        tail_bits = self.b8(ord(tail_byte))
        
        header_bit_from = header_bit_offset % 8
        tail_bit_to = 8-tail_bit_offset % 8
    
        #bytes to binary
        bytes = self.buf[header_byte_offset:tail_byte_offset+1]
        bytes_bits = ''
        if bytes:
            bytes_bits = ('{:0%db}'%(len(bytes)*8)).format(int(bytes.encode('hex'),16))
            bytes_bits = bytes_bits.rjust(len(bytes) * 2, '0') #padding
        
        #header bits + middle bits + tail bits
        bits = bytes_bits[header_bit_from:-tail_bit_to]
        if len(bits) % 9:
            raise 'not 9 bit '
        bytes = [bits[i:i+9] for i in range(0, len(bits),9)]
        if ret_type == 'str':
            bytes = map(lambda x: '%03x'%int(x,2),bytes)
            bytes = ' '.join(bytes) 
        else:
            bytes = map(lambda x: int(x,2),bytes)
        return bytes


    def write(self, offset, bytes):
        '''
        result

        > db 0 12
        0000000: 001 002 003 001 002 003 001 002 003 081 000 003 - 002 122 000 140 020 080

        > u
        0000000:                         0080203         adi.   R16, R00, 0x40
        0000003:                         0080203         adi.   R16, R00, 0x40
        0000006:                         0080203         adi.   R16, R00, 0x40
        0000009:                         0010203         adi.   R02, R00, 0x40
        '''

        bits = ''

        if type(bytes) == int:   #0x0080203 -> [1,2,3]
            bytes = self.int2bytes(bytes)

        if type(bytes) == str: #001 002 003
            bytes = bytes.split()
            for byte in bytes:
                bits += self.b9(int(byte,16))
        elif type(bytes) == list:# [1,2,3]
            for byte in bytes:
                bits += self.b9(byte)

        header_bit_offset = offset * 9
        header_byte_offset = header_bit_offset / 8
        header_byte = self.buf[header_byte_offset]
        header_bits = self.b8(ord(header_byte))
        
        tail_bit_offset = offset * 9 + len(bytes) * 9
        tail_byte_offset = tail_bit_offset / 8
        tail_byte = self.buf[tail_byte_offset]
        tail_bits = self.b8(ord(tail_byte))
        
        header_bit_to = header_bit_offset % 8
        tail_bit_from = tail_bit_offset % 8

        #header bits + patch bits + tail bits
        bits = header_bits[:header_bit_to] + bits + tail_bits[tail_bit_from:]
        if len(bits) % 8:
            raise 'not 8 bit '

        #binary to bytes
        patch_bytes = '%x' % int(bits,2)
        patch_bytes = patch_bytes.rjust(len(bits) / 8 * 2, '0').decode('hex')
        
        #concat(modify file bytes)
        self.buf = self.buf[:header_byte_offset] + patch_bytes + self.buf[header_byte_offset + len(patch_bytes):]
        if len(self.buf) != self.size:
            raise 'file size changed'
        return len(bytes)

    def assemble(self, instructions, delim=';'):
        return [0]
        #input code

        #instructions = instructions.split(delim)
        #bytes = clamenddi.assemble(instructions)
        #bytes = map(lambda x: '%03x'%int(x,2), [bytes[i:i+9] for i in range(0,len(bytes),9)])
        #bytes = ' '.join(bytes)
        #return bytes

    def asm(self, offset, instructions, delim=';'):

        '''
        :result 

        before
        > db 0 12
        0000000: 040 158 040 001 000 0b8 003 148 180 000 000 020 - 002 122 000 140 020 080
        > u
        0000000:                         2b0402000002b8  ldt    R01, [R00 + 0x57, 3]

        after
        > db 0 12
        0000000: 100 140 0c0 140 000 0b8 003 148 180 000 000 020 - 002 122 000 140 020 080
        > u
        0000000:                         28100           ei     R00
        0000002:                         280c0           ht
        0000004: Disassembly Error
        '''
        bytes = self.assemble(instructions, delim)
        self.write(offset, bytes)
        return len(bytes)
        
    def save(self,file_name):
        out = open(file_name, 'wb')
        out.write(self.buf)
        out.close()
        return len(self.buf)

    def close(self):
        self.f.close()

