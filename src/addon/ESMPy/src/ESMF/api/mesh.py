# $Id$

"""
The Mesh API
"""

#### IMPORT LIBRARIES #########################################################

from copy import copy, deepcopy

from ESMF.api.constants import *
from ESMF.interface.cbindings import *
from ESMF.util.decorators import initialize

from ESMF.api.esmpymanager import *
from ESMF.util.slicing import get_formatted_slice, get_none_or_slice, get_none_or_bound_list

import warnings

#### Mesh class ###############################################################
[node, element] = [0, 1]

class Mesh(object):
    """
    The Mesh class is a Python wrapper object for the ESMF Mesh.
    The individual values of all coordinate and mask arrays are referenced to those of the
    underlying Fortran ESMF object.

    The ESMF library provides a class for representing unstructured grids called the Mesh. Fields can be created
    on a Mesh to hold data. Fields created on a Mesh can also be used as either the source or destination or both
    of a regrididng operation which allows data to be moved between unstructured grids.  A Mesh is constructed of
    nodes and elements. A node, also known as a vertex or corner, is a part of a Mesh which represents a single
    point. Coordinate information is set in a node. An element, also known as a cell, is a part of a mesh which
    represents a small region of space. Elements are described in terms of a connected set of nodes which represent
    locations along their boundaries. Field data may be located on either the nodes or elements of a Mesh.

    For more information about the ESMF Mesh class, please see the `ESMF Mesh documentation
    <http://www.earthsystemmodeling.org/esmf_releases/public/last/ESMF_refdoc/node5.html#SECTION050100000000000000000>`_.

    """

    @property
    def area(self):
        """
        :return: the Mesh area represented as a numpy array of floats of the same number of entries as Mesh elements
        """
        return self._area

    @property
    def coords(self):
        """
        :return: a 2 element list containing numpy arrays of the coordinates of the nodes and elements of the Mesh
        """
        return self._coords

    @property
    def element_area(self):
        return self._element_area

    @property
    def element_conn(self):
        return self._element_conn

    @property
    def element_coords(self):
        return self._element_coords

    @property
    def element_count(self):
        return self._element_count

    @property
    def element_ids(self):
        return self._element_ids

    @property
    def element_mask(self):
        return self._element_mask

    @property
    def element_types(self):
        return self._element_types

    @property
    def finalized(self):
        return self._finalized

    @property
    def mask(self):
        """
        :return: A 2 element list of numpy arrays representing the masked values on the nodes and elements of the Mesh
        """
        return self._mask

    @property
    def meta(self):
        return self._meta

    @property
    def node_coords(self):
        return self._node_coords

    @property
    def node_count(self):
        return self._node_count

    @property
    def node_ids(self):
        return self._node_ids

    @property
    def node_owners(self):
        return self._node_owners

    @property
    def parametric_dim(self):
        return self._parametric_dim

    @property
    def rank(self):
        """
        :return: the rank of the Mesh, (i.e. the number of dimensions of the coordinate arrays (always 1)
        """
        return self._rank

    @property
    def singlestagger(self):
        return self._singlestagger

    @property
    def size(self):
        """
        :return: a 2 element list containing the number of nodes and elements in the Mesh on the current processor
        """
        return self._size

    @property
    def size_owned(self):
        """
        :return: a 2 element list containing the number of owned nodes and elements in the Mesh on the current processor
        """
        return self._size_owned

    @property
    def spatial_dim(self):
        return self._spatial_dim

    @property
    def struct(self):
        return self._struct

    @initialize
    def __init__(self, parametric_dim=None,
                 spatial_dim=None,
                 filename=None,
                 filetype=None,
                 convert_to_dual=None,
                 add_user_area=None,
                 meshname="",
                 mask_flag=None,
                 varname=""):
        """
        Create an unstructured Mesh. This can be done two different ways, 
        as a Mesh in memory, or from a SCRIP formatted or CF compliant UGRID 
        file. The argument for each type of Mesh creation are outlined below. \n
            Mesh in memory: \n
                The in-memory Mesh can be created manually in 3 steps: \n
                    1. create the Mesh (specifying parametric_dim and spatial_dim), \n
                    2. add nodes, \n
                    3. add elements. \n
                    Required arguments for a Mesh in memory: \n
                        parametric_dim: the dimension of the topology of the Mesh (e.g.
                            a Mesh composed of squares would have a parametric dimension of
                            2 and a Mesh composed of cubes would have a parametric dimension
                            of 3). \n
                        spatial_dim: the number of coordinate dimensions needed to
                            describe the locations of the nodes making up the Mesh.  For a
                            manifold the spatial dimension can be larger than the parametric
                            dimension (e.g. the 2D surface of a sphere in 3D space), but it
                            cannot be smaller. \n
                    Optional arguments for creating a Mesh in memory: \n
                        None \n
            Mesh from file: \n
                Note that Meshes created from file do not have the parametric_dim and
                spatial dim set.  \n
                Required arguments for creating a Mesh from file: \n
                    filename: the name of NetCDF file containing the Mesh. \n
                    filetype: the input file type of the Mesh. \n
                        Argument values are: \n
                            FileFormat.SCRIP \n
                            FileFormat.ESMFMESH \n
                            FileFormat.UGRID \n
                Optional arguments for creating a Mesh from file: \n
                    convert_to_dual: a boolean value to specify if the dual
                        Mesh should be calculated.  Defaults to False.  This
                        argument is only supported with filetype FileFormat.SCRIP.\n
                    add_user_area: a boolean value to specify if an area
                        property should be added to the mesh.  This argument is only
                        supported for filetype FileFormat.SCRIP or FileFormat.ESMFMESH.
                        Defaults to False. \n
                    meshname: a string value specifying the name of the
                        Mesh metadata variable in a UGRID file.  This argument is only
                        supported with filetype FileFormat.UGRID.  Defaults to the empty string. \n
                    mask_flag: an enumerated integer that, if specified, tells whether
                        a mask in a UGRID file should be defined on the nodes (MeshLoc.NODE)
                        or the elements (MeshLoc.ELEMENT) of the Mesh.  This argument is only
                        supported with filetype FileFormat.UGRID.  Defaults to no masking. \n
                    varname: a string to specify a variable name for the mask in a UGRID file
                        if mask_flag is specified.  This argument is only supported for
                        filetype FileFormat.UGRID.  Defaults to the empty string. \n
            Returns: \n
                Mesh \n
        """

        # handle input arguments
        fromfile = False
        # in memory
        if (parametric_dim is not None) or (spatial_dim is not None):
            # parametric_dim and spatial_dim are required for in-memory mesh creation
            if (parametric_dim is None) or (spatial_dim is None):
                warning.warn("both parametric_dim and spatial_dim must be specified")
            # raise warnings for the from-file options
            if filename is not None:
                warning.warn("filename is only used for meshes created from file, this argument will be ignored.")
            if filetype is not None:
                warning.warn("filetype is only used for meshes created from file, this argument will be ignored.")
            if convert_to_dual is not None:
                warning.warn("convert_to_dual is only used for meshes created from file, this argument will be ignored.")
            if add_user_area is not None:
                warning.warn("add_user_area is only used for meshes created from file, this argument will be ignored.")
            if meshname is not "":
                warning.warn("meshname is only used for meshes created from file, this argument will be ignored.")
            if mask_flag is not None:
                warning.warn("mask_flag is only used for meshes created from file, this argument will be ignored.")
            if varname is not "":
                warning.warn("varname is only used for meshes created from file, this argument will be ignored.")
        # filename and filetype are required for from-file mesh creation
        elif (filename is None) or (filetype is None):
            raise MeshArgumentError ("must supply either parametric_dim and spatial_dim for an in-memory mesh or filename and filetype for a from-file mesh")
        # from file
        else:
            fromfile = True
            #raise warnings for all in-memory grid options
            if parametric_dim is not None:
                warning.warn("parametric_dim is only used for meshes created in memory, this argument will be ignored.")
            if spatial_dim is not None:
                warning.warn("spatial_dim is only used for meshes created in memory, this argument will be ignored.")
        
        # ctypes stuff
        self._struct = None
    
        # bookkeeping
        self._size = [None, None]
        self._size_owned = [None, None]
        self._parametric_dim = None
        self._spatial_dim = None
        self._rank = 1
        self._coords = None
        self._mask = [None, None]
        self._area = None

        if not fromfile:
            # initialize not fromfile variables
            self._element_count = None
            self._element_ids = None
            self._element_types = None
            self._element_conn = None
            self._element_mask = None
            self._element_area = None
            self._element_coords = None
            self._node_count = None
            self._node_ids = None
            self._node_coords = None
            self._node_owners = None
            
            # call into ctypes layer
            self._struct = ESMP_MeshCreate(parametricDim=parametric_dim,
                                          spatialDim=spatial_dim)
            self._parametric_dim = parametric_dim
            self._spatial_dim = spatial_dim
        else:
            # call into ctypes layer
            self._struct = ESMP_MeshCreateFromFile(filename, filetype,
                                                  convert_to_dual, 
                                                  add_user_area, meshname, 
                                                  mask_flag, varname)
            # get the sizes
            self._size[node] = ESMP_MeshGetLocalNodeCount(self)
            self._size_owned[node] = ESMP_MeshGetOwnedNodeCount(self)
            self._size[element] = ESMP_MeshGetLocalElementCount(self)
            self._size_owned[element] = ESMP_MeshGetOwnedElementCount(self)

            # link the coords here for meshes created from file, in add_elements for others
            self._link_coords_()
            # NOTE: parametric_dim is set in the _link_coords_ call for meshes created from file

        # for arbitrary metadata
        self._meta = {}

        # register with atexit
        import atexit; atexit.register(self.__del__)
        self._finalized = False

        # set the single stagger flag
        self._singlestagger = False

    # manual destructor
    def destroy(self):
        """
        Release the memory associated with a Mesh. \n
        Required Arguments: \n
            None \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """
        if hasattr(self, '_finalized'):
            if not self._finalized:
                ESMP_MeshDestroy(self)
                self._finalized = True

    def __del__(self):
        """
        Release the memory associated with a Mesh. \n
        Required Arguments: \n
            None \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """
        self.destroy()

    def __repr__(self):
        """
        Return a string containing a printable representation of the object
        """
        string = ("Mesh:\n"
                  "    rank = %r\n"
                  "    size = %r\n"
                  "    size_owned = %r\n" 
                  "    coords = %r\n"
                  %
                  (
                   self.rank,
                   self.size,
                   self.size_owned,
                   self.coords))

        return string

    def _copy_(self):
        # shallow copy
        ret = copy(self)
        # don't call ESMF destructor twice on the same shallow Python object
        # NOTE: the ESMF Mesh destructor is particularly unsafe in this situation
        ret._finalized = True

        return ret

    def __getitem__(self, slc):
        if pet_count() > 1:
            raise SerialMethod

        slc = get_formatted_slice(slc, self.rank)
        ret = self._copy_()

        # TODO: cannot get element coordinates, so the slice has them set to None
        ret._coords = [[get_none_or_slice(get_none_or_slice(get_none_or_slice(self.coords, 0), coorddim), slc) for
                       coorddim in range(self.parametric_dim)], [None for x in range(self.parametric_dim)]]

        # size is "sliced" by taking the shape of the coords
        ret._size = [get_none_or_bound_list(get_none_or_slice(ret.coords, stagger), 0) for stagger in range(2)]
        ret._size_owned = ret.size

        return ret

    def _preslice_(self, meshloc):
        # to be used to slice off one stagger location of a grid for a specific field
        ret = self._copy_()
        ret._coords = get_none_or_slice(self.coords, meshloc)

        # preslice the size to only return the meshloc of this field
        ret._size = get_none_or_slice(self.size, meshloc)
        ret._size_owned = ret.size

        ret._singlestagger = True

        return ret

    def _slice_onestagger_(self, slc):
        if pet_count() > 1:
            raise SerialMethod

        # to be used to slice the single stagger grid, one that has already been presliced
        slc = get_formatted_slice(slc, self.rank)
        ret = self._copy_()

        ret._coords = [get_none_or_slice(get_none_or_slice(self.coords, x), slc) for x in range(self.parametric_dim)]

        # size is "sliced" by taking the shape of the coords
        ret._size = get_none_or_bound_list(ret.coords, 0)
        ret._size_owned = ret.size

        return ret

    def add_elements(self, element_count,
                     element_ids,
                     element_types,
                     element_conn,
                     element_mask=None,
                     element_area=None,
                     element_coords=None):
        """
        Add elements to a Mesh, this must be done after adding nodes. \n
        Required Arguments: \n
            element_count: the number of elements to add to the Mesh. \n
            element_ids: a numpy array (internally cast to 
                dtype=numpy.int32) to specify the element_ids. \n
                    type: numpy.array \n
                    shape: (element_count, 1) \n
            element_types: a numpy array (internally cast to 
                dtype=numpy.int32) to specify the element_types. \n
                    type: numpy.array \n
                    shape: (element_count, 1) \n
                Argument values are: \n
                    MeshElemType.TRI \n
                    MeshElemType.QUAD \n
                    MeshElemType.TETRA \n
                    MeshElemType.HEX \n
            element_conn: a numpy array (internally cast to 
                dtype=numpy.int32) to specify the connectivity 
                of the Mesh.  The connectivity array is 
                constructed by concatenating
                the tuples that correspond to the 
                element_ids.  The connectivity tuples are
                constructed by listing the node_ids of each 
                element in COUNTERCLOCKWISE order. \n
                    type: numpy.array \n
                    shape: (sum(element_types[:], 1) \n
        Optional Arguments: \n
            element_mask: a numpy array (internally cast to 
                dtype=numpy.int32) containing integer values to 
                specify masked elements.  The specific values that are masked
                are specified in the Regrid() constructor.\n
                    type: numpy.array \n
                    shape: (element_count, 1) \n
            element_area: a numpy array (internally cast to 
                dtype=numpy.float64) to specify the areas of the 
                elements. \n
                    type: numpy.array \n
                    shape: (element_count, 1) \n
            element_coords: a numpy array (internally cast to 
                dtype=numpy.float64) to specify the coordinates of the
                elements. \n
                    type: numpy.array \n
                    shape: (element_count, 1) \n
        Returns: \n
            None \n
        """

        # initialize not fromfile variables
        self._element_count = element_count
        if element_ids.dtype is not np.int32:
            self._element_ids = np.array(element_ids, dtype=np.int32)
        else:
            self._element_ids = element_ids
        if element_types.dtype is not np.int32:
            self._element_types = np.array(element_types, dtype=np.int32)
        else:
            self._element_types = element_types
        if element_conn.dtype is not np.int32:
            self._element_conn = np.array(element_conn, dtype=np.int32)
        else:
            self._element_conn = element_conn
        if element_mask is not None:
            if element_mask.dtype is not np.int32:
                self._element_mask = np.array(element_mask, dtype=np.int32)
            else:
                self._element_mask = element_mask
            self._mask[1] = self._element_mask
        if element_area is not None:
            if element_area.dtype is not np.float64:
                self._element_area = np.array(element_area, dtype=np.float64)
            else:
                self._element_area = element_area
            self._area = self._element_area
        if element_coords is not None:
            if element_coords.dtype is not np.float64:
                self._element_coords = np.array(element_coords, dtype=np.float64)
            else:
                self._element_coords = element_coords

        # call into ctypes layer
        ESMP_MeshAddElements(self, self.element_count, self.element_ids, 
                             self.element_types, self.element_conn, 
                             self.element_mask, self.element_area,
                             self.element_coords)
        
        # get the sizes
        self.size[node] = ESMP_MeshGetLocalNodeCount(self)
        self.size_owned[node] = ESMP_MeshGetOwnedNodeCount(self)
        self.size[element] = ESMP_MeshGetLocalElementCount(self)
        self.size_owned[element] = ESMP_MeshGetOwnedElementCount(self)
        
        # link the coords here for meshes not created from file
        self._link_coords_()

    def add_nodes(self, node_count,
                  node_ids,
                  node_coords,
                  node_owners):
        """
        Add nodes to a Mesh, this must be done before adding elements. \n
        Required Arguments: \n
            node_count: the number of nodes to add to the Mesh. \n
            node_ids: a numpy array (internally cast to 
                dtype=numpy.int32) to specify the node_ids. \n
                    type: numpy.array \n
                    shape: (node_count, 1) \n
            node_coords: a numpy array (internally cast to 
                dtype=numpy.float64) to specify the coordinates 
                of the Mesh.  The array should be constructed by 
                concatenating the coordinate tuples into a numpy array 
                that correspond to node_ids. \n
                    type: numpy.array \n
                    shape: (spatial_dim*node_count, 1) \n
            node_owners: a numpy array (internally cast to 
                dtype=numpy.int32) to specify the rank of the
                processor that owns each node. \n
                    type: numpy.array \n
                    shape: (node_count, 1) \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """

        self._node_count = node_count
        if node_ids.dtype is not np.int32:
            self._node_ids = np.array(node_ids, dtype=np.int32)
        else:
            self._node_ids = node_ids
        if node_coords.dtype is not np.float64:
            self._node_coords = np.array(node_coords, dtype=np.float64)
        else:
            self._node_coords = node_coords
        if node_owners.dtype is not np.int32:
            self._node_owners = np.array(node_owners, dtype=np.int32)
        else:
            self._node_owners = node_owners
 
        # call into ctypes layer
        ESMP_MeshAddNodes(self, self.node_count, self.node_ids, 
                          self.node_coords, self.node_owners)
        # can't get the sizes until mesh is "committed" in element call

    def free_memory(self):
        """
        Free memory associated with the creation of a Mesh which is no 
        longer needed. \n
        Required Arguments: \n
            None \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """
        # call into ctypes layer
        ESMP_MeshFreeMemory(self)

    def get_coords(self, coord_dim, meshloc=node):
        """
        Return a numpy array of coordinates at a specified Mesh 
        location (coordinates can only be returned for the Mesh NODES 
        at this time). The returned array is NOT a copy, it is
        directly aliased to the underlying memory allocated by ESMF.\n
        Required Arguments: \n
           coord_dim: the dimension number of the coordinates to return:
                       e.g. [x, y, z] = (0, 1, 2), or [lat, lon] = (0, 1) \n
        Optional Arguments: \n
             meshloc: the mesh location of the coordinates. \n
                Argument values are: \n
                    node=0 (default) \n
                    element=1 (not implemented) \n
        Returns: \n
            A numpy array of coordinate values at the specified meshloc. \n
        """

        ret = None
        # only nodes for now
        if not self._singlestagger:
            assert(self.coords[meshloc][coord_dim] is not None)
            ret = self.coords[meshloc][coord_dim]
        else:
            assert(self.coords[coord_dim] is not None)
            ret = self.coords[coord_dim]

        return ret

    def _write_(self, filename):
        """
        Write the Mesh to a vtk formatted file. \n
        Required Arguments: \n
            filename: the name of the file, .vtk will be appended. \n
        Optional Arguments: \n
            None \n
        Returns: \n
            None \n
        """

        # call into ctypes layer
        ESMP_MeshWrite(self, filename)

    def _link_coords_(self):
        elemcoords = True

        # get the pointer to the underlying ESMF data array for coordinates
        coords_interleaved, num_nodes, num_dims = ESMP_MeshGetCoordPtr(self)
        try:
            coords_elem, num_elems, num_dims_e = ESMP_MeshGetElemCoordPtr(self)
            assert num_dims == num_dims_e
        except:
            warnings.warn("Mesh element coordinates are not available")
            elemcoords = False

        if not self.parametric_dim:
            self._parametric_dim = num_dims

        try:
            pass
            # TODO: removed connectivity because the hardcoded array allocation is
            #       eating up too much memory on some systems, this method can be
            #       added back in after mesh connectivity retrieval has been fixed the
            #       C interface
            # self._connectivity, self._nodes_per_elem = ESMP_MeshGetConnectivityPtr(self)
        except:
            warnings.warn("Mesh connectivity could not be read")

        # initialize the coordinates structures
        # index order is [meshloc][coord_dim]
        self._coords = [[None for a in range(num_dims)] \
                        for b in range(2)]

        # alias the coordinates to the mesh
        self._coords[node][0] = np.array([coords_interleaved[2*i] for i in range(num_nodes)])
        self._coords[node][1] = np.array([coords_interleaved[2*i+1] for i in range(num_nodes)])
        if num_dims == 3:
            self._coords[node][2] = np.array([coords_interleaved[2*i+2] for i in range(num_nodes)])

        if elemcoords:
            self._coords[element][0] = np.array([coords_elem[2 * i] for i in range(num_elems)])
            self._coords[element][1] = np.array([coords_elem[2 * i + 1] for i in range(num_elems)])
            if num_dims == 3:
                self._coords[element][2] = np.array([coords_elem[2 * i + 2] for i in range(num_elems)])
