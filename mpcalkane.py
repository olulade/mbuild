__author__ = 'sallai'

from alkane_tail import AlkaneTail
from alkane_body import AlkaneBody
from mbuild.compound import *
from methane import *
from mpcalkanebody import *

class MpcAlkane(Compound):
    @classmethod
    def create(cls, n, label=None):

        if n < 2:
            raise Exception('n must be 2 or more')

        m = super(MpcAlkane, cls).create(label)

        # bottom
        m.add(AlkaneBody.create(),'bottom_ch2')

        # n times the body CH_2
        last_part = m.bottom_ch2

        for body_count in range(2, n):
            if body_count % 20 == 0:
                this_part = MpcAlkaneBody.create(direction='left')
            elif body_count % 10 == 0:
                this_part = MpcAlkaneBody.create(direction='right')
            else:
                this_part = AlkaneBody.create()

            this_part.transform([(this_part.male_port, last_part.female_port)])
            m.add(this_part, 'body_'+str(body_count))
            last_part = this_part

        # top tail (CH_3)
        m.add(AlkaneTail.create(),'top_ch3')
        m.top_ch3.transform( [(m.top_ch3.male_port, last_part.female_port)])

        return m


if __name__ == "__main__":
    m = MpcAlkane.create(21)
    #print m.atoms()
    m.plot(labels=False, verbose=False)
    m.savexyz('mpcchain.xyz')