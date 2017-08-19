from patcher import Patcher

if __name__ == '__main__':
    patcher = Patcher('hello.bin')

    bytes =  patcher.read(0x0,12, 'list') #[64, 344, 64, 1, 0, 184, 3, 328, 384, 0, 0, 32]
    print bytes
    bytes =  patcher.read(0x0,12, 'str') #040 158 040 001 000 0b8 003 148 180 000 000 020
    print bytes

    patcher.write(0x0, [1,2,3])
    patcher.write(0x3, '001 002 003')
    patcher.write(0x6, 0x0080203)
    patcher.write(0x9, 0x0010203)
    #patcher.asm(0xc, 'ei R00')
    #patcher.asm(0xe, 'ht')
    #patcher.asm(0xc, 'ei R00; ht')

    patcher.save('hello_patched.bin')

    '''
    > u
    0000000:                         0080203         adi.   R16, R00, 0x40
    0000003:                         0080203         adi.   R16, R00, 0x40
    0000006:                         0080203         adi.   R16, R00, 0x40
    0000009:                         0010203         adi.   R02, R00, 0x40
    000000c:                         28100           ei     R00
    000000e:                         280c0           ht
    0000010: Disassembly Error
    > db 0 15
    0000000: 001 002 003 001 002 003 001 002 003 081 000 003 - 100 140 0c0 140 020 080 145 148 100

    '''