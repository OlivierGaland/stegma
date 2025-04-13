from og_log import LOG,LEVEL

from src.img import SteganoImgWriter, SteganoImgReader
from src.dispersion import NaiveDispersion,LinearDispersion,ZpStarDispersion
from src.noise import NoNoiseGenerator, RandomNoiseGenerator

from src.tools import show_pictures_diff,show_pictures_diff_alt,encode_string,decode_string


INPUT_FILE = "./test/pics/fantasy.jpg" 
OUTPUT_FILE = "./test/output/fantasy.out.png" 

#INPUT_FILE = "./test/pics/cat000.png"
#OUTPUT_FILE = "./test/output/cat000.out.png" 

PASSWORD = 'vR7#pZ1m$Lq@X9tD'

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

def main():

    data = encode_string(SECRET)
    LOG.info("Data to hide : "+str(data))   #256 bit

    out = decode_string(data)
    LOG.info("Decoded data : "+str(out))

    #codec = NaiveDispersion
    #codec = LinearDispersion
    codec = ZpStarDispersion
    LOG.info("Codec : "+str(codec))
    #noise = NoNoiseGenerator
    noise = RandomNoiseGenerator
    LOG.info("Noise : "+str(noise))

    print("Encoding secret with codec "+str(codec).__class__.__name__+" and noise "+str(noise.__class__.__name__))
    f = SteganoImgWriter(codec,noise,PASSWORD,INPUT_FILE,data)
    LOG.info("Factory : "+str(f))
    f.embed_data_lsb(OUTPUT_FILE)

    print("Reading secret with codec "+str(codec.__class__.__name__))
    g = SteganoImgReader(codec,PASSWORD,OUTPUT_FILE)
    LOG.info("Factory : "+str(g))

    if f.data != g.data: raise Exception("Data corrupted")
    print("Verifying data with success : "+str(decode_string(g.data)))

    LOG.info("Data extracted : "+str(decode_string(g.data)))

    #show_pictures_diff_alt(INPUT_FILE,OUTPUT_FILE)
    show_pictures_diff(INPUT_FILE,OUTPUT_FILE)

if __name__ == "__main__":
    #LOG.start()
    LOG.info("Start")
    LOG.level(LEVEL.info)
    main()

