__author__ = 'sallai'
import pdb
import sys
import os

from mbuild.compound import Compound
from mbuild.port import Port
from mbuild.mol2file import load_mol2
from mbuild.coordinate_transform import *

class Methyl(Compound):
    """ """
    def __init__(self):
        Compound.__init__(self)

        # Look for data file in same directory as this python module.
        current_dir = os.path.dirname(os.path.realpath(sys.modules[__name__].__file__))
        new_path = os.path.join(current_dir, 'methyl.mol2')
        load_mol2(new_path, component=self)
        carbon = self.C_1

        # transform(self, Translation(-carbon.pos))
        translate(self, -carbon)

        self.add(Port(), 'up')
        rotate_around_z(self.up, np.pi)
        translate(self.up, np.array([0,-0.7,0]))
        self.up.add(carbon, 'C_1', containment=False)

        self.add(Port(), 'down')
        translate(self.down, np.array([0,-0.7,0]))
        self.down.add(carbon, 'C_1', containment=False)

if __name__ == '__main__':
    methyl = Methyl()

    from mbuild.plot import Plot
    Plot(methyl, verbose=True, atoms=True, bonds=True, angles=False, dihedrals=False).show()

