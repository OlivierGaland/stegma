# stegma

Steganography python library for learning.
You can hide a secret in an image protected with a password.



# Usage

Currently in dev, the script create_stegano.py is an entry point showing class usage.
- feed INPUT_FILE, OUTPUT_FILE, PASSWORD, SECRET
- select codec/noise class by setting variables codec and noise

Once ran it will create the output png file and show a plot of the result (input, output, differences), ultimatly verifying the encoding/decoding is successfull

# Technical details

Input :

- Image to process (any format, output will be a RGBA png)
- Password
- Secret to hide (bitfield in string format)

Steganography logic :

- Converting input image into png RGBA 
- Using LSB (least significant bit) on channel R,G,B with 3 coding bit for a pixel (4*8 = 32 bits) 

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


Encoding using NaiveDispersion (sequential data writing) :


Encoding using LinearDispersion (sequential data writing with interval) :


Encoding using ZpStarDispersion (better concealed data writing using (Z/pZ)* schema) :


