import enum

USED = 0
UNUSED = 255

# copypasta from DX SDK 'Include/d3d9types.h' enum _D3DDECLTYPE to address
# vert attribute vartype variable
class D3DDECLTYPE(enum.IntEnum):
    FLOAT1 = 0  # 1D float expanded to (value, 0., 0., 1.)
    FLOAT2 = 1  # 2D float expanded to (value, value, 0., 1.)
    FLOAT3 = 2  # 3D float expanded to (value, value, value, 1.)
    FLOAT4 = 3  # 4D float
    D3DCOLOR = 4  # 4D packed unsigned bytes mapped to 0. to 1. range
    # Input is in D3DCOLOR format (ARGB) expanded to (R, G, B, A)

    # UBYTE4 doesnt seems to be used anywhere in bf2 meshes
    # TODO: test PR meshes if it does
    #UBYTE4 = 5  # 4D unsigned byte
    UNUSED = 17,  # When the type field in a decl is unused.

    def __len__(self):
        return {
            self.FLOAT1: len([0.,]),
            self.FLOAT2: len([0., 0.]),
            self.FLOAT3: len([0., 0., 0.]),
            self.FLOAT4: len([0., 0., 0., 0.]),
            self.D3DCOLOR: len([0.,]),
            self.UNUSED : len([])
        }[self]


# copypasta from DX SDK 'Include/d3d9types.h' enum _D3DDECLUSAGE to
# address vert attribute usage variable
class D3DDECLUSAGE(enum.IntEnum):
    POSITION = 0
    BLENDWEIGHT = 1
    BLENDINDICES = 2
    NORMAL = 3
    PSIZE = 4
    UV1 = 5  # TEXCOORD in d3d9 enums
    TANGENT = 6
    BINORMAL = 7
    TESSFACTOR = 8
    POSITIONT = 9
    COLOR = 10
    FOG = 11
    DEPTH = 12
    SAMPLE = 13
    # bf2 enums for additional UVs much larger than dx to avoid collisions?
    UV2 = 261
    UV3 = 517
    UV4 = 773
    UV5 = 1029