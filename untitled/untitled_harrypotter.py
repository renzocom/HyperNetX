from hypernetx import *
import matplotlib.pyplot as plt
from collections import OrderedDict, defaultdict
import scipy
from scipy.sparse import coo_matrix, issparse
import pandas as pd
import numpy as np
import itertools as it
import importlib as imp
import untitled_StaticEntity as us


class HarryPotter(object):

    def __init__(self):

        # Read dataset in using pandas. Fix index column or use default pandas index.
        harrydata = pd.read_csv('HarryPotter/datasets/Characters_edit.csv', encoding='unicode_escape').set_index('Id')
        self.harrydata = pd.DataFrame(harrydata)

        # Choose string to fill NaN. These will be set to 0 in system id = sid
        harry = harrydata[['House', 'Blood status', 'Species', 'Hair colour', 'Eye colour']].fillna("Unknown")
        for c in harry.columns:
            harry[c] = harry[c].apply(lambda x: x.replace('\xa0', ' ')).apply(lambda x: x.replace('Unknown', f'Unknown {c}'))
        self.dataframe = harry

        # Generate a counter for each column
        # - Assign a sid to each value in that column
        # - Create a reverse counter to grab name from sid

        # **Questions for Tony and Cliff**
        # - how should we index the objects?
        # - sids are whole numbers starting with column 0 and running through each column
        # - ldict and rdict are indexed starting with 0 representing missing values
        # - would we lose anything if we indexed these as -1 for missing values and then
        # compute the incidence matrix using only nonnegative indices?

        ctr = [HNXCount() for c in range(5)]
        ldict = OrderedDict()
        rdict = OrderedDict()
        for idx, c in enumerate(harry.columns):
            ldict[c] = defaultdict(ctr[idx])
            rdict[c] = OrderedDict()
            ldict[c][f'Unknown {c}']
            rdict[c][0] = f'Unknown {c}'
            for k in harry[c]:
                ldict[c][k]
                rdict[c][ldict[c][k]] = k
            ldict[c] = dict(ldict[c])
        self.dims = dims = tuple([len(ldict[c]) for c in harry.columns])

        # ### Create an array of tuples giving positions of 1's in incidence Tensor
        # - The tuples indicate one point across the possible node/edge assignments
        # - The dimensions of the tuple give the number of unique labels in potential nodes/columns

        m = len(harry)
        n = len(harry.columns)
        data = np.zeros((m, n), dtype=int)
        for rid in range(m):
            for cid in range(n):
                c = harry.columns[cid]
                data[rid, cid] = ldict[c][harry.iloc[rid][c]]

        self.data = data
        # Create incidence Tensor and labels
        imat = np.zeros(dims, dtype=int)
        for d in data:
            imat[tuple(d)] += 1
        self.imat = imat
        self.coo = coo_matrix(np.sum(imat, axis=(2, 3, 4)))

        slabels = OrderedDict()
        for cdx, c in enumerate(list(ldict.keys())):
            slabels.update({c: np.array(list(ldict[c].keys()))})
        self.labels = slabels

        self.entity = us.StaticEntity(imat, slabels)
        self.entityset = us.StaticEntitySet(imat, slabels, 0, 1)
        self.sparseentity = us.StaticEntitySet(self.coo, slabels, 0, 1)
