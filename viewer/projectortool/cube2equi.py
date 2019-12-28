import sys
from PIL import Image

from projection import *

def get_sample(xy, img_equi_size, face_size, img_faces):
	angles = angles_from_img_xy(xy, img_equi_size)
	direction = direction_from_angles(angles)
	face, face_xy = face_and_face_xy_from_direction(direction, face_size)
	faces_xy = to_faces_xy(face_xy, face, face_size)
	sample = img_faces.getpixel(faces_xy)
	return sample

def get_multisample(xy, img_equi_size, face_size, img_faces, samples):
	r,g,b = 0,0,0
	for sx in range(samples):
		for sy in range(samples):
			sample_xy = (float(xy[0]) + float(sx) / float(samples),
						 float(xy[1]) + float(sy) / float(samples))
			sample = get_sample(sample_xy, img_equi_size, face_size, img_faces)
			r += sample[0]
			g += sample[1]
			b += sample[2]
	return (r / (samples*samples),
			g / (samples*samples),
			b / (samples*samples))

def render_equi(img_faces, img_equi, face_size, samples):
	for y in range(img_equi.size[1]):
		if y % 100 == 0:
			print '{} percent rendered'.format(100*y/img_equi.size[1])
		for x in range(img_equi.size[0]):
			multisample = get_multisample((x,y), img_equi.size, face_size, img_faces, samples)
			img_equi.putpixel((x,y), multisample)

def cube_to_equi(faces_img_path, equi_img_path, equi_size, samples):
	faces_img = Image.open(faces_img_path)
	face_size = (faces_img.size[0]/4, faces_img.size[1]/3)
	equi_img = Image.new('RGB', equi_size, 'black')
	render_equi(faces_img, equi_img, face_size, samples)
	equi_img.save(equi_img_path)

if len(sys.argv) != 5:
	print 'Usage: {} <src_image> <dest_image> <dest_height> <samples>'.format(sys.argv[0])
	sys.exit(1)

cube_to_equi(
	sys.argv[1],
	sys.argv[2],
	(2*int(sys.argv[3]), int(sys.argv[3])),
	int(sys.argv[4])
)
print 'Done'