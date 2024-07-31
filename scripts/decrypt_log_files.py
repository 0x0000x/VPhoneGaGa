from binascii import unhexlify 
from Crypto.Cipher import ARC4 
import os, re

pat = re. compile ( '^(\[\d+\]){2}\[(\d\d:){2}\d\d.\d{3}\]: ' , re.M)

for  dir , _, files in os.walk( r"C:\Users\amgad\Desktop\Reverse Engineering\vphone_gaga\3.0.0\logs\instance1-cracked" ):
    for file in map ( lambda x: os.path.join( dir , x), files):         
        rc = ARC4.new(unhexlify( '206DEA86C313F2E3' )) 
        if file.endswith( '.log' ):             
            data = rc.decrypt( open (file, 'rb' ).read()).decode( 'utf-8' )             
            data = pat.sub( '' , data) 
            open (file, 'w' , encoding= 'utf-8' ).write(data)
     

        


            