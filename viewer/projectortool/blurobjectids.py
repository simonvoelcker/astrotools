import sys
import math
from PIL import Image

from projection import *

class Vec3(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def cross(self, other):
		return Vec3(
			self.y * other.z - self.z * other.y,
			self.z * other.x - self.x * other.z,
			self.x * other.y - self.y * other.x)

	def length(self):
		return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

	def normalize(self):
		l = self.length()
		self.x = self.x / l
		self.y = self.y / l
		self.z = self.z / l

	def rotate(self, axis, angle):
		sin_a = sin(angle)
		cos_a = cos(angle)

def get_sample(xy, src_img, radius):
	angles = angles_from_img_xy(xy, src_img.size)
	direction = direction_from_angles(angles)
	samples_per_axis = radius
	for sx in range(-samples_per_axis/2, +samples_per_axis/2+1):
		for sy in range(-samples_per_axis/2, +samples_per_axis/2+1):
			# say sx,sy are angles (complete bullshit)
			look = Vec3(direction.x, direction.y, direction.z)
			look.normalize()
			# all vectors are normalized from here on
			up_axis = Vec3(0.0, 1.0, 0.0)
			right = up_axis.cross(look)
			up = right.cross(look)


	sample = src_img.getpixel(xy)
	return sample

def render_blurred(src_img, dest_img, radius):
	for y in range(src_img.size[1]):
		if y % 100 == 0:
			print '{} percent rendered'.format(100*y/src_img.size[1])
		for x in range(src_img.size[0]):
			sample = get_sample((x,y), src_img, radius)
			dest_img.putpixel((x,y), sample)

def blur_oids(src_img_path, dest_img_path, radius):
	src_img = Image.open(src_img_path)
	dest_img = Image.new('RGB', src_img.size, 'black')
	render_blurred(src_img, dest_img, radius)
	dest_img.save(dest_img_path)

if len(sys.argv) != 4:
	print 'Usage: {} <src_image> <dest_image> <radius>'.format(sys.argv[0])
	sys.exit(1)

blur_oids(sys.argv[1], sys.argv[2], int(sys.argv[3]))
print 'Done'