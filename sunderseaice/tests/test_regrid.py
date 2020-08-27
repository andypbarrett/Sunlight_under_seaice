import numpy as np
import matplotlib.pyplot as plt

from sunderseaice.maps.regrid import north_polar_stereo_to_ease_avhrr

def load_test_file():
    infile = '/home/apbarret/src/Examples/data/2020melt.int.304.448.new'
    
    melt_onset = np.fromfile(infile, dtype='int16').byteswap().reshape(448, 304)
    melt_onset = np.where(melt_onset > 0, melt_onset, np.nan)
    return melt_onset


def main():

    melt_onset = load_test_file()
    ease_onset = north_polar_stereo_to_ease_avhrr(melt_onset)

    fig, ax = plt.subplots()
    ax.imshow(ease_onset)
    plt.show()

    
if __name__ == "__main__":
    main()
    

