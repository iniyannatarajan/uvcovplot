import numpy as np
import pyrap.tables as pt
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import sys

lightspeed = 299792458.0 # speed of light in m/s

def get_blinfo():
    return dict([((x, y), np.where((ant1 == x) & (ant2 == y))[0]) \
            for x in ant_uniq for y in ant_uniq if y > x])

parser = argparse.ArgumentParser()
parser.add_argument('ms', help='Input Measurement Set name')
args = parser.parse_args()

# validate and clean inputs
args.ms = args.ms.rstrip('/')

# read info from MS
tab = pt.table(args.ms)
uvw = tab.getcol('UVW')
ant1 = tab.getcol('ANTENNA1')
ant2 = tab.getcol('ANTENNA2')
flag = tab.getcol('FLAG')
flag_row = tab.getcol('FLAG_ROW')
tab.close()

atab = pt.table(args.ms+'::ANTENNA')
station = atab.getcol('STATION')
atab.close()

spwtab = pt.table(args.ms+'::SPECTRAL_WINDOW')
chan_freq = spwtab.getcol('CHAN_FREQ').flatten()

# compute necessary quantities
ant_uniq = np.unique(np.hstack((ant1, ant2)))
bldict = get_blinfo()
wavelen = (lightspeed/chan_freq.mean())*1e9 # in Glambda
flag_final = np.logical_or(flag, flag_row[:,np.newaxis,np.newaxis])

# create legend labels
labels = {}
for bl in bldict.keys():
    labels[bl] = station[bl[0]]+'-'+station[bl[1]]

# start plotting
fig = plt.figure()
ax = fig.add_subplot(111)

# plot uv-coverage
for bl in bldict.keys():
  #for chan in range(chan_freq.shape[0]):
    flag_mask = np.logical_not(flag_final[bldict[bl],0,0])
    #wavelen = (lightspeed/chan_freq[chan])*1e9 # in Glambda
    wavelen = (lightspeed/chan_freq.mean())*1e9 # in Glambda
    u = uvw[bldict[bl][flag_mask], 0]/wavelen
    v = uvw[bldict[bl][flag_mask], 1]/wavelen
    ax.plot(np.hstack([u, np.nan, -u]), np.hstack([v, np.nan, -v]), '.', label=labels[bl])

#ax.set_xlim(ax.get_xlim()[::-1])
ax.set_xlim(10,-10)
ax.set_ylim(-10,10)

#plt.legend()
plt.savefig(args.ms.split('/')[-1]+'.png')
    
