"""
@motjuste
Created: 26-08-2016

Utilities for working with labels
"""
import numpy as np
from collections import Iterable
from contextlib import contextmanager


class SequenceLabels(object):
    """ Base class for working with contiguous labels for sequences

    Supports normal slicing as in numpy, but the returned value will be another
    instance of the SequenceLabels class.

    FIXME: [A] update the doc for the with statement
    NOTE: You can get the properties `starts` and `ends` at a different
    sample-rate by passing a sample-rate other than the default value of 1 to
    `get_starts`, or setting the property `samplerate` to change the default.

    This class is not a monolith, but should be able to work with normal
    numpy tricks. Plus, you should extend it for specific data, etc.

    Plus, there is nice printing.

    TODO: [A] Check if something can be done about plotting it nicely too!
    """

    def __init__(self, starts_ends, labels, samplerate=1):
        assert all(isinstance(x, Iterable)
                   for x in [starts_ends, labels
                             ]), "starts_ends and labels should be iterable"
        assert len(starts_ends) == len(labels), "starts_ends and labels" + \
                                                " mismatch in length "

        self._starts_ends = np.array(starts_ends)
        self.labels = labels
        self._orig_samplerate = samplerate
        self._samplerate = self._orig_samplerate

    @property
    def samplerate(self):
        return self._orig_samplerate

    @property
    def starts_ends(self):
        return self._starts_ends * (self._samplerate / self._orig_samplerate)

    @property
    def starts(self):
        return self.starts_ends[:, 0]

    @property
    def ends(self):
        return self.starts_ends[:, 1]

    @contextmanager
    def samplerate_as(self, new_sr):
        self._samplerate = new_sr
        try:
            yield
        finally:
            self._samplerate = self._orig_samplerate

    def __len__(self):
        return len(self.starts_ends)

    def __getitem__(self, idx):
        se = self.starts_ends[idx]
        l = self.labels[idx]

        if not isinstance(l, Iterable):  # case with only one segment
            se = np.expand_dims(se, axis=0)  # shape (2,) to shape (1, 2)
            l = [l]

        sr = self.samplerate

        return SequenceLabels(se, l, sr)

    def __str__(self):
        s = self.__class__.__name__ + "\n with sample rate: " + str(
            self.samplerate)
        s += "\n"
        s += "{:8} - {:8} : {}\n".format("Start", "End", "Label")
        s += "\n".join("{:<8.4} - {:<8.4} : {}".format(s, e, str(l))
                       for (s, e), l in zip(self.starts_ends, self.labels))

        return s
