__author__ = 'sallai'
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import pdb

from mbuild.coordinate_transform import *

from mbuild.atom import *


class Compound(object):
    @classmethod
    def create(cls, label=None):
        m = cls()
        m._components = {}
        if label is not None:
            m._label = label
        return m

    def add(self, what, label=None):
        if label is None:
            label = what.label()
        if label in self._components.keys():
            raise Exception("label " + label + " already exists in " + str(what))
        self._components[label] = what
        setattr(self, label, what)

    def label(self):
        if hasattr(self, '_label'):
            return self._label
        else:
            return str(self.__class__.__name__) + '_' + str(id(self))

    def createEquivalenceTransform(self, equiv):
        """
        Compute an equivalence transformation that transforms this point cloud to another's coordinate system.
        :param other: the other point cloud
        :param equiv: list of equivalent points
        :returns: the coordinatetransform object that transforms this point cloud to the other point cloud's coordinates system
        """

        self_points = array([])
        self_points.shape = (0, 3)
        other_points = array([])
        other_points.shape = (0, 3)

        for pair in equiv:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise Exception('Equivalence pair not a 2-tuple')
            if not ((isinstance(pair[0], Compound) and isinstance(pair[1], Compound)) or (
                    isinstance(pair[0], Atom) and isinstance(pair[1], Atom))):
                raise Exception(
                    'Equivalence pair type mismatch: pair[0] is a ' + str(type(pair[0])) + ' and pair[1] is a ' + str(
                        type(pair[1])))

            if isinstance(pair[0], Atom):
                self_points = vstack([self_points, pair[0].pos])
                other_points = vstack([other_points, pair[1].pos])
            if isinstance(pair[0], Compound):
                for label0, atom0 in pair[0].atoms().iteritems():
                    atom1 = pair[1].component(label0)
                    self_points = vstack([self_points, atom0.pos])
                    other_points = vstack([other_points, atom1.pos])

        T = CoordinateTransform.compute(self_points, other_points)
        return T

    def transform(self, equiv):
        """
        Transform this point cloud to another's coordinate system.
        :param other: the other point cloud
        :param equiv: list of equivalent points
        :returns: the matrix that transforms this point cloud to the other point cloud's coordinates system
        """
        T = self.createEquivalenceTransform(equiv)

        # transform the contained atoms recursively
        self.applyTransformation(T)

        return self

    def applyTransformation(self, T):
        for label, component in self._components.iteritems():
            component.applyTransformation(T)


    def atoms(self):
        atoms = {} # empty dict
        for label, component in self._components.iteritems():
            # add local atoms
            if isinstance(component, Atom):
                atoms[label] = component
                # add atoms in sub-components recursively
            if isinstance(component, Compound):
                for sublabel, subatom in component.atoms().iteritems():
                    atoms[label + '.' + sublabel] = subatom
        return atoms

    def savexyz(self, fn, print_ports=False):
        with open(fn, 'w') as f:
            if print_ports:
                f.write(str(self.atoms().__len__()) + '\n\n')
            else:
                i = 0
                for key, value in self.atoms().iteritems():
                    if value.atomType != 'G':
                        i += 1
                f.write(str(i) + '\n\n')
            for key, value in self.atoms().iteritems():
                if print_ports:
                    f.write(value.atomType + '\t' +
                            str(value.pos[0]) + '\t' +
                            str(value.pos[1]) + '\t' +
                            str(value.pos[2]) + '\n')
                else:
                    if value.atomType != 'G':
                        f.write(value.atomType + '\t' +
                                str(value.pos[0]) + '\t' +
                                str(value.pos[1]) + '\t' +
                                str(value.pos[2]) + '\n')



    def component(self, component_path):
        dot_pos = component_path.find('.')
        if dot_pos > -1:
            subcomponent_path = component_path[:dot_pos]
            subpath = component_path[dot_pos + 1:]
            if subcomponent_path in self._components.keys():
                return self._components[subcomponent_path].component(subpath)
            else:
                return None
        else:
            if component_path in self._components.keys():
                return self._components[component_path]
            else:
                return None

    def boundingbox(self, excludeG=True):
        minx = float('inf')
        miny = float('inf')
        minz = float('inf')
        maxx = float('-inf')
        maxy = float('-inf')
        maxz = float('-inf')

        for label, a in self.atoms().iteritems():
            if excludeG and a.atomType == 'G':
                continue
            if a.pos[0] < minx:
                minx = a.pos[0]
            if a.pos[0] > maxx:
                maxx = a.pos[0]
            if a.pos[1] < miny:
                miny = a.pos[1]
            if a.pos[1] > maxy:
                maxy = a.pos[1]
            if a.pos[2] < minz:
                minz = a.pos[2]
            if a.pos[2] > maxz:
                maxz = a.pos[2]

        return (minx, miny, minz), (maxx, maxy, maxz)

    def plot(self, verbose=False, labels=True):

        from mayavi import mlab
        from tvtk.api import tvtk
        import numpy as np

        x = []
        y = []
        z = []
        r = []
        g = []
        b = []
        rgb = []

        # sort atoms by type
        d = dict()

        for (label, atom) in self.atoms().items():
            if atom.atomType != 'G' or verbose:
                if not atom.atomType in d.keys():
                    d[atom.atomType] = [atom]
                else:
                    d[atom.atomType].append(atom);

        for (atomType,atomList) in d.items():
            x = []
            y = []
            z = []
            r = []
            for atom in atomList:
                x.append(atom.pos[0])
                y.append(atom.pos[1])
                z.append(atom.pos[2])
                # TODO: should we do the sizing by the wdv radius???
                r.append(atom.vdw_radius)
                # r.append(1)
            fig = mlab.points3d(x,y,z,r,color=atomList[0].colorRGB, scale_factor=1, scale_mode='scalar')
            #fig.glyph.glyph.clamping = False
        mlab.show()



    def plot2(self, verbose=False, labels=False):
        fig = pyplot.figure()
        ax = fig.add_subplot(111, projection='3d', aspect='equal')
        coord_min = inf
        coord_max = -inf
        for (label, atom) in self.atoms().items():
            if atom.atomType != 'G' or verbose:
                # print atom
                if labels:
                    atom.plot(ax, str(atom))
                else:
                    atom.plot(ax, None)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(self.label())

        pyplot.show()