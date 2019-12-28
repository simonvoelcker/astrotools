from math import atan2, sqrt, pi, sin, cos
from collections import namedtuple

from enum import Enum

Direction = namedtuple('Direction', ['x', 'y', 'z'])

class Face(Enum):
    neg_x = 1
    pos_x = 2
    neg_y = 3
    pos_y = 4
    neg_z = 5
    pos_z = 6

face_offsets = {
    Face.neg_x: (1,1), Face.pos_x: (3,1),
    Face.neg_y: (1,0), Face.pos_y: (1,2),
    Face.neg_z: (2,1), Face.pos_z: (0,1)
}

def to_faces_xy((x,y), face, face_size):
    return (
        x + face_offsets[face][0] * face_size[0],
        y + face_offsets[face][1] * face_size[1]
    )

class Angles(object):
    def __init__(self, altitude, azimuth):
        self.altitude = altitude
        self.azimuth = azimuth

def img_xy_from_angles(angles, size):
    logical_x = angles.azimuth / (2.0 * pi)
    logical_y = angles.altitude / pi + 0.5
    pixel_x = max(0, min(size[0]-1, int(round(size[0] * logical_x))))
    pixel_y = max(0, min(size[1]-1, int(round(size[1] * logical_y))))
    return (pixel_x, pixel_y)

def angles_from_img_xy(img_xy, size):
    logical_x = float(img_xy[0]) / float(size[0]-1)
    logical_y = float(img_xy[1]) / float(size[1]-1)
    return Angles(altitude=(logical_y - 0.5) * pi, azimuth=2.0 * pi * logical_x)

def angles_from_direction(d):
	# catch altitude special cases
    if d.x == 0 and d.z == 0:
    	if d.y == 0:
    		# null vector case: safe fallback
    		return Angles(altitude=0, azimuth=0)
    	elif d.y < 0:
    		# again save fallback for azimuth
    		return Angles(altitude=-pi/2.0, azimuth=0)
    	else:
    		# again save fallback for azimuth
    		return Angles(altitude=+pi/2.0, azimuth=0)

    altitude = atan2(d.y, sqrt(d.x*d.x + d.z*d.z))

    # catch azimuth special case
    if d.x == 0:
		return Angles(altitude=altitude, azimuth=-pi/2.0 if d.z < 0 else +pi/2.0)

	# general case
    azimuth = atan2(d.z, d.x)	# outputs [-pi;pi]
    if azimuth < 0.0:
    	azimuth += 2.0*pi	 	# map to [0;2pi]
    angles = Angles(altitude=altitude, azimuth=azimuth)
    return angles

def direction_from_angles(angles):
    x, y, z = 1.0, 0.0, 0.0
    x, y = (x * cos(angles.altitude) - y * sin(angles.altitude),
            x * sin(angles.altitude) + y * cos(angles.altitude))
    x, z = (x * cos(angles.azimuth) - z * sin(angles.azimuth),
            x * sin(angles.azimuth) + z * cos(angles.azimuth))
    return Direction(x, y, z)

def direction_from_face_xy(xy, size, face):
    u = float(xy[0]) / float(size[0] - 1)
    v = float(xy[1]) / float(size[1] - 1)

    if face == Face.neg_x:
        return Direction(-1, 2*v-1, -(2*u-1))
    if face == Face.pos_x:
        return Direction(+1, 2*v-1, 2*u-1)
    if face == Face.neg_y:
        return Direction(-(2*v-1), -1, -(2*u-1))
    if face == Face.pos_y:
        return Direction(2*v-1, +1, -(2*u-1))
    if face == Face.neg_z:
        return Direction(2*u-1, 2*v-1, -1)
    if face == Face.pos_z:
        return Direction(-(2*u-1), 2*v-1, +1)

    return None


def face_and_face_xy_from_direction(direction, size):
    max_xyz = max(abs(direction.x), abs(direction.y), abs(direction.z))
    x, y, z = (direction.x / max_xyz, direction.y / max_xyz, direction.z / max_xyz)

    to_face_xy = lambda x, y: (
        int((x + 1.0) / 2.0 * float(size[0] - 1)),
        int((y + 1.0) / 2.0 * float(size[1] - 1))
    )

    if x == -1.0:
        return Face.neg_x, to_face_xy(-z, +y)
    if x == +1.0:
        return Face.pos_x, to_face_xy(+z, +y)
    if y == -1.0:
        return Face.neg_y, to_face_xy(-z, -x)
    if y == +1.0:
        return Face.pos_y, to_face_xy(-z, +x)
    if z == -1.0:
        return Face.neg_z, to_face_xy(+x, +y)
    if z == +1.0:
        return Face.pos_z, to_face_xy(-x, +y)

    return None