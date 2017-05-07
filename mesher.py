import os
import struct

import bf2

# https://github.com/ByteHazard/BfMeshView/blob/master/source/modStdMesh.bas

def LoadBF2Mesh(filepath):
    with open(filepath, 'rb') as meshfile:
        file_extension = os.path.splitext(filepath)[1].lower()

        isSkinnedMesh = (file_extension == '.skinnedmesh')
        isBundledMesh = (file_extension == '.bundledmesh')
        isStaticMesh = (file_extension == '.staticmesh')
        
        vmesh = StdMesh(isSkinnedMesh, isBundledMesh, isStaticMesh)
        vmesh.load_file_data(meshfile)
    return vmesh

class bf2lod:
    def __init__(self, fo, version):
        # some internals
        self.version = version
        
        self.min = None
        self.max = None
        self.pivot = None
        self.nodenum = None

        self.node = []
        self.polycount = 0
        self.matnum = None
        self.mat = []

class bf2mat:
    def __init__(self, fo, isSkinnedMesh, version):
        self.alphamode = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   alphamode: {}'.format(self.alphamode))
        self.fxfile = self.__get_string(fo)
        print('   fxfile: {}'.format(self.fxfile))
        self.technique = self.__get_string(fo)
        print('   technique: {}'.format(self.technique))
        self.mapnum = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   mapnum: {}'.format(self.mapnum))
        self.map = self.__get_maps(fo)
        self.vstart = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   vstart: {}'.format(self.vstart))
        self.istart = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   istart: {}'.format(self.istart))
        self.inum = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   inum: {}'.format(self.inum))
        self.vnum = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        print('   vnum: {}'.format(self.vnum))
        self.u4 = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        self.u5 = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        if not isSkinnedMesh and version == 11:
            self.nmin = tuple(struct.Struct('3f').unpack(fo.read(struct.calcsize('3f'))))
            self.nmax = tuple(struct.Struct('3f').unpack(fo.read(struct.calcsize('3f'))))
        
    def __get_string(self, fo):
        string_len = struct.Struct('l').unpack(fo.read(struct.calcsize('l')))[0]
        string_fmt = str(string_len) + 's'
        return struct.Struct(string_fmt).unpack(fo.read(struct.calcsize(string_fmt)))[0]
    
    def __get_maps(self, fo):
        mapnames = []
        for i in range(self.mapnum):
            mapname = self.__get_string(fo)
            mapnames.append(mapname)
            print('    {}'.format(mapname))
        return mapnames
            

class bf2head:
    def __init__(self, fo, offset):
        # some internals
        self._fmt = ('5l')
        self._size = struct.calcsize(self._fmt)

        # reading bin
        data = struct.Struct(self._fmt).unpack(fo.read(self._size))
        self.u1 = data[0]
        self.version = data[1]
        self.u3 = data[2]
        self.u4 = data[3]
        self.u5 = data[4]
    
    def __eq__(self, other):
        if self.u1 != other.u1: return False
        if self.version != other.version : return False
        if self.u3 != other.u3: return False
        if self.u4 != other.u4: return False
        if self.u5 != other.u5: return False
        return True

class bf2geom:
    def __init__(self, fo):
        # some internals
        self._fmt = ('l')
        self._size = struct.calcsize(self._fmt)
        
        # reading bin
        data = struct.Struct(self._fmt).unpack(fo.read(self._size))
        self.lodnum = data[0]
        self.lod = []

class vertattrib:
    def __init__(self, fo):
        # some internals
        self._fmt = ('4h')
        self._size = struct.calcsize(self._fmt)

        # reading bin
        data = struct.Struct(self._fmt).unpack(fo.read(self._size))
        self.flag = data[0]
        self.offset = data[1]
        self.vartype = data[2]
        self.usage = data[3]

    def __str__(self):
        return str((self.flag, self.offset, self.vartype, self.usage))
    
    def __eq__(self, other_tuple):
        if (self.flag, self.offset, self.vartype, self.usage) == other_tuple:
            return True
        else:
            return False



class StdMesh:

    def __init__(self, isSkinnedMesh=False, isBundledMesh=False, isStaticMesh=False):
        # setting some internals
        self.isSkinnedMesh = False
        self.isBundledMesh = False
        self.isStaticMesh = False
        self._tail = 0

        # mesh data
        self.head = None
        self.u1 = None
        self.geomnum = None
        self.geoms = None
        self.vertattribnum = None
        self.vertattrib = None
        self.vertformat = None
        self.vertstride = None
        self.vertnum = None
        self.vertices = None
        self.indexnum = None
        self.index = None
        self.u2 = None
        
    def load_file_data(self, fo):
        # it will read everything nb4
        self._read_materials(fo)

    #-----------------------------
    # READING FILEDATA
    #-----------------------------
    def _read_head(self, fo):
        self.head = bf2head(fo, self._tail)
        self._tail = fo.tell()
        print('head ends at {}'.format(fo.tell()))
    
    def _read_u1_bfp4f_version(self, fo):
        self._read_head(fo)
        _fmt = 'b'
        _size = struct.calcsize(_fmt)

        self.u1 = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()

    def _read_geomnum(self, fo):
        self._read_u1_bfp4f_version(fo)
        print('geomtable starts at {}'.format(fo.tell()))
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.geomnum = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail += _size
    
    def _read_geoms(self, fo):
        self._read_geomnum(fo)
        self.geoms = [bf2geom(fo) for i in range(self.geomnum)]
        self._tail = fo.tell()
        print('geomtable ends at {}'.format(fo.tell()))
    
    def _read_vertattribnum(self, fo):
        self._read_geoms(fo)
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.vertattribnum = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()
        print('attribtable starts at {}'.format(fo.tell()))

    def _read_vertext_attribute_table(self, fo):
        self._read_vertattribnum(fo)
        self.vertattrib = [vertattrib(fo) for i in range(self.vertattribnum)]
        self._tail = fo.tell()
        print('attribtable ends at {}'.format(fo.tell()))
        
    def _read_vertformat(self, fo):
        self._read_vertext_attribute_table(fo)
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.vertformat = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()
        
    def _read_vertstride(self, fo):
        self._read_vertformat(fo)
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.vertstride = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()
        
    def _read_vertnum(self, fo):
        self._read_vertstride(fo)
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.vertnum = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()
    
    def _read_vertex_block(self, fo):
        self._read_vertnum(fo)
        _vertices_num = int(self.vertstride/self.vertformat * self.vertnum)
        _fmt = '{}f'.format(_vertices_num)
        _size = struct.calcsize(_fmt)
        
        self.vertices = struct.Struct(_fmt).unpack(fo.read(_size))
        self._tail = fo.tell()
        print('vertex block ends at {}'.format(fo.tell()))
    
    def _read_indexnum(self, fo):
        self._read_vertex_block(fo)
        _fmt = 'l'
        _size = struct.calcsize(_fmt)

        self.indexnum = struct.Struct(_fmt).unpack(fo.read(_size))[0]
        self._tail = fo.tell()

    def _read_index_block(self, fo):
        self._read_indexnum(fo)
        _fmt = '{}h'.format(self.indexnum)
        _size = struct.calcsize(_fmt)
        
        self.index = struct.Struct(_fmt).unpack(fo.read(_size))
        self._tail = fo.tell()
        print('index block ends at {}'.format(fo.tell()))

    def _read_u2(self, fo):
        if not self.isSkinnedMesh:
            self._read_index_block(fo)
            _fmt = 'l'.format(self.indexnum)
            _size = struct.calcsize(_fmt)
            
            self.u2 = struct.Struct(_fmt).unpack(fo.read(_size))[0]
            self._tail = fo.tell()
    
    def _read_nodes(self, fo):
        self._read_u2(fo)
        for geomnum in range(self.geomnum):
            for lodnum in range(self.geoms[geomnum].lodnum):
                self.geoms[geomnum].lod.insert(lodnum, bf2lod(fo, self.head.version))
                self.__read_lod_node_table(fo, self.geoms[geomnum].lod[lodnum])
        self._tail = fo.tell()
    
    def _read_materials(self, fo):
        self._read_nodes(fo)

        print('geom block starts at {}'.format(fo.tell()))
        def _read_matnum(fo, lod):
            _fmt = 'l'
            _size = struct.calcsize(_fmt)

            data = struct.Struct(_fmt).unpack(fo.read(_size))
            lod.matnum = data[0]

        for geomnum in range(self.geomnum):
            for lodnum in range(self.geoms[geomnum].lodnum):
                print(' mesh {} start at {}'.format(lodnum, fo.tell()))
                _read_matnum(fo, self.geoms[geomnum].lod[lodnum])
                print(' matnum: {}'.format(self.geoms[geomnum].lod[lodnum].matnum))
                #for matnum in range(self.geoms[geomnum].lod[lodnum].matnum):
                self.__read_lod_material(fo, self.geoms[geomnum].lod[lodnum])
                print(' mesh {} end at {}'.format(lodnum, fo.tell()))
        self._tail = fo.tell()
        print('geom block ends at {}'.format(fo.tell()))

    #-----------------------------
    # WRITING FILEDATA
    #-----------------------------
    def _write_header(self, filepath):
        with open(filepath, 'wb+') as fo:
            dataset = (self.head.u1,
                    self.head.version,
                    self.head.u3,
                    self.head.u4,
                    self.head.u5)
            fo.write(struct.Struct(self.head._fmt).pack(*dataset))
            return fo.tell()

    def _write_u1_bfp4f_version(self, filepath):
        with open(filepath, 'ab+') as fo:
            fmt = 'b'
            fo.write(struct.Struct(fmt).pack(self.u1))
            return fo.tell()


    def _write_geomnum(self, filepath):
        self._write_u1_bfp4f_version(filepath)
        with open(filepath, 'ab+') as fo:
            fmt = 'l'
            fo.write(struct.Struct(fmt).pack(self.geomnum))
            return fo.tell()

    #-----------------------------
    # PRIVATE
    #-----------------------------
    
    def __read_lod_node_table(self, fo, lod):
        print('nodes chunk start at  {}'.format(fo.tell()))

        def _read_bounds(fo, lod):
            _fmt = '6f'
            _size = struct.calcsize(_fmt)
            _data = struct.Struct(_fmt).unpack(fo.read(_size))
            
            lod.min = tuple(_data[0:3])
            lod.max = tuple(_data[3:6])
        
        def _read_pivot(fo, lod):
            if lod.version <= 6:
                _fmt = '3f'
                _size = struct.calcsize(_fmt)
                _data = struct.Struct(_fmt).unpack(fo.read(_size))

            lod.pivot = tuple(_data)

        def _read_nodenum(fo, lod):
            _fmt = 'l'
            _size = struct.calcsize(_fmt)
            _data = struct.Struct(_fmt).unpack(fo.read(_size))

            lod.nodenum = int(_data[0])
        
        _read_bounds(fo, lod)
        if self.head.version <= 6:
            _read_pivot(fo, lod)
        _read_nodenum(fo, lod)

        # reading nodes
        for i in range(lod.nodenum):
            for j in range(16):
                _fmt = 'f'
                _size = struct.calcsize(_fmt)
                _data = struct.Struct(_fmt).unpack(fo.read(_size))
                lod.node.append(_data[0])
        print('nodes chunk end at {}'.format(fo.tell()))

    def __read_lod_material(self, fo, lod):
        for i in range(lod.matnum):
            print('  mat {} start at {}'.format(i, fo.tell()))
            material = bf2mat(fo, self.isSkinnedMesh, self.head.version)
            print('  mat {} ends at {}'.format(i, fo.tell()))
            lod.mat.insert(i, material)
            lod.polycount = lod.polycount + material.inum / 3











