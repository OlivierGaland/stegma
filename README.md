![image](https://github.com/user-attachments/assets/b841c32b-bcc7-4f6a-a5fd-2b73c75cae22)

# stegma

Steganography python library for learning.
You can hide a secret in an image protected with a password.

Important : This package should not (yet) used for production as it may strongly change from the current state, without backward compatibility for beta releases. Despite this warning If you want to use it, be sure to keep a repository image of the code to be sure to be able to retrieve the secret.

Planned enhancement (not implemented) :
- Decoy mode : This will not encode any header (storing data lenght) but need user to provide data length at decoding. Usage could be hiding an encryption key inside the image, if the password is wrong, a plausible but erroneous encryption key will be returned
- Media type : add other media or file format (audio, video)
- Refactoring to add other steganography method (currently only LSB)
- Pip package creation

# Usage

Currently in dev, the script create_stegano.py is an entry point showing class usage.
- feed INPUT_FILE, OUTPUT_FILE, PASSWORD, SECRET
- select codec/noise class by setting variables codec and noise

Once ran it will create the output png file and show a plot of the result (input, output, differences), ultimatly verifying the encoding/decoding is successfull

# Technical details

Input :

- generate/retrieve : Image to process (any format, output will be a RGBA png)
- generate/retrieve : Password
- generate/retrieve : Dispersion algo
- generate : Secret to hide (bitfield in string format)
- generate : Noise algo

Steganography logic :

- Converting input image into png RGBA 
- Using LSB (least significant bit) on channel R,G,B with 3 coding bit for a pixel (4*8 = 32 bits)
- Secret is crypted using password hash in xor schema

Offset codec logic :

- NaiveDispersion : Basic sequential data encoding, o(n+1) = o(n) + 1 % max_offset
- LinearDispersion : Same as sequential, but using a generated increment, o(n+1) = o(n) + i % max_offset  
- ZpStarDispersion : Using (Z/pZ)* group generator, o(n+1) = g*o(n) % prime   (prime <= max_offset)

Noise feature :

- NoNoiseGenerator : No noise
- RandomNoiseGenerator : Add random noise in non coding offsets

Determinist codec parameters :

- start_offset (All but ZpStarDispersion): from hash(HSB image fingerprint + password) converted to integer [0;max_offset] 
- start_offset (ZpStarDispersion): from hash(HSB image fingerprint + password) converted to integer [1;prime-1] 
- increment (LinearDispersion) : from hash(HSB image fingerprint + password) converted to integer [1;max_offset], nearest higher or equal integer matching gcd(increment,max_offset) = 1
- prime (ZpStarDispersion) : from hash(HSB image fingerprint + password) converted to integer [max_offset-max_offset//16;max_offset], nearest previous prime
- generator (ZpStarDispersion): from hash(HSB image fingerprint + password) converted to integer [1;prime-1], nearest higher generator of (Z/Zp)*

Secret encoding :

- Encode secret in following form : header + secret (as a bitfield)
- header format is following (support up to 4Gb data (512 MB))
    - first bit is 0 : 8 next bit is size-1 (max 256 bit)
    - first bits are 10 : 16 next bit is size-1 (max 65536 bit)
    - first bits are 110 : 24 next bit is size-1 (max 16777216 bit)
    - first bits are 111 : 32 next bit is size-1 (max 4294967296 bit)

# dependencies

pip : og_log, PIL, hashlib, sympy, numpy, matplotlib

# Screenshots

Console :
![image](https://github.com/user-attachments/assets/e87ee26d-3833-4828-bff7-e4304dbe3e53)

Encoding using NaiveDispersion (sequential data writing) :
![image](https://github.com/user-attachments/assets/bd64a81d-5814-4a0e-a8c4-ae1e33ccbf95)

Encoding using LinearDispersion (sequential data writing with interval) :
![image](https://github.com/user-attachments/assets/b62628da-d5e6-4ff8-b76a-3b3119179bc4)

Encoding using ZpStarDispersion (better concealed data writing using (Z/pZ)* schema) :
![image](https://github.com/user-attachments/assets/e448f795-d32c-42e1-8d11-334303abfc8b)

