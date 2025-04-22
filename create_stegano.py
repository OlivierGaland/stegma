from src.core.writer import SteganoWriter
from src.core.reader import SteganoReader
from src.media.image import Image
from src.codec.std import Standard
from src.codec.decoy import Decoy
from src.algo.lsb import Lsb

from src.dispersion.linear import LinearDispersion 
from src.dispersion.naive import NaiveDispersion
from src.dispersion.zp_star import ZpStarDispersion
from src.dispersion.chained_hash import ChainedHashDispersion

from src.noise.random import RandomNoiseGenerator
from src.noise.none import NoNoiseGenerator

from og_log import LOG,LEVEL

from src.tools import encode_string,decode_string


SECRET = """
It is not the critic who counts; not the man who points out how the strong man stumbles,
or where the doer of deeds could have done them better. The credit belongs to the man
who is actually in the arena, whose face is marred by dust and sweat and blood;
who strives valiantly; who errs, who comes short again and again, because there is no
effort without error and shortcoming; but who does actually strive to do the deeds;
who knows great enthusiasms, the great devotions; who spends himself in a worthy cause;
who at the best knows in the end the triumph of high achievement, and who at the worst,
if he fails, at least fails while daring greatly, so that his place shall never be with
those cold and timid souls who neither know victory nor defeat.

It is not the critic who counts, nor the man who sits idly by and casts stones at those
who are trying to make a difference. The true measure of success lies not in avoiding failure,
but in the courage to continue despite it. The man in the arena, covered in the dust of battle,
is the one who is truly living, who is truly making a difference, and who is writing his own story.
It is easy to stand on the sidelines, to point fingers and to offer empty critiques, but it is the
individual who steps forward and takes action, who dares to risk it all, who deserves the honor
and the glory of his efforts. And while the arena is filled with danger and uncertainty, it is
also where the greatest triumphs are won, where dreams are realized, and where legacies are built.
"""

if __name__ == '__main__':
    LOG.start()
    LOG.level(LEVEL.warning)
    LOG.info("Start")

    INPUT_DIR = "./media/image/"
    OUTPUT_DIR = "./media/output/"

    INPUT_FILENAME = [ "beavers.png" ,"fantasy_micro.png" , "fantasy_mini.jpg" , "fantasy.jpg" , "cat000.png"][0]
    INPUT_FILE = INPUT_DIR + INPUT_FILENAME
    OUTPUT_FILE = OUTPUT_DIR + INPUT_FILENAME
    PASSWORD = 'el653CWrON!N3ihw'

    MEDIA = [Image][0]
    CODEC = [Standard , Decoy][0]
    ALGO = [Lsb][0]
    DISPERSION = [NaiveDispersion , LinearDispersion ,ZpStarDispersion, ChainedHashDispersion][3]
    NOISE = [NoNoiseGenerator , RandomNoiseGenerator][1]
    data = encode_string(SECRET)

    # encode
    w = SteganoWriter()    
    w.register_media(MEDIA,file=INPUT_FILE,summary=True)
    w.register_codec(CODEC,password=PASSWORD,encode=data)
    w.register_algo(ALGO,pattern="RGB",coding_bits=1)
    w.register_dispersion(DISPERSION)
    w.register_noise(NOISE)
    w.encode()
    if CODEC == Decoy:   #Decoy codec (no header) needs user to know size to recover the secret
        secret_size = len(w.codec.output)
        print("Size of secret to hide :",secret_size) 
    w.write(OUTPUT_FILE)

    # verify
    d = SteganoReader()
    d.register_media(MEDIA,file=OUTPUT_FILE)
    if CODEC == Decoy: d.register_codec(CODEC,password=PASSWORD,size=secret_size)   #size is mandatory if CODEC is Decoy
    else: d.register_codec(CODEC,password=PASSWORD)
    d.register_algo(ALGO,pattern="RGB",coding_bits=1)
    d.register_dispersion(DISPERSION)
    d.decode()

    print("Decoded data :",decode_string(d.retrieve_data()))

    if SECRET != decode_string(d.retrieve_data()):
        raise Exception("Failure : Decoded data does not match original data")

    LOG.info("End")
