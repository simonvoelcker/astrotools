import sys
from PIL import Image

from projection import *

def get_sample(xy, face_size, face, img_equi):
	direction = direction_from_face_xy(xy, face_size, face)
	angles = angles_from_direction(direction)
	equi_xy = img_xy_from_angles(angles, img_equi.size)
	sample = img_equi.getpixel(equi_xy)
	return sample

def get_multisample(xy, face_size, face, img_equi, samples):
	r,g,b = 0,0,0
	for sx in range(samples):
		for sy in range(samples):
			sample_xy = (float(xy[0]) + float(sx) / float(samples),
						 float(xy[1]) + float(sy) / float(samples))
			sample = get_sample(sample_xy, face_size, face, img_equi)
			r += sample[0]
			g += sample[1]
			b += sample[2]
	return (r / (samples*samples),
			g / (samples*samples),
			b / (samples*samples))

def render_faces(img_equi, img_faces, face_size, samples):
	for face in face_offsets.keys():
		print 'rendering face {}'.format(face)
		for y in range(face_size[0]):
			for x in range(face_size[1]):
				sample = get_multisample((x,y), face_size, face, img_equi, samples)
				faces_xy = to_faces_xy((x,y), face, face_size)
				img_faces.putpixel(faces_xy, sample)

def equi_to_cube(equi_img_path, faces_img_path, face_size, samples):
	equi_img = Image.open(equi_img_path)
	faces_img = Image.new('RGB', (4*face_size[0], 3*face_size[1]), 'black')	
	render_faces(equi_img, faces_img, face_size, samples)
	faces_img.save(faces_img_path)

if len(sys.argv) != 5:
	print 'Usage: {} <src_image> <dest_image> <face_height> <samples>'.format(sys.argv[0])
	sys.exit(1)

equi_to_cube(
	sys.argv[1],
	sys.argv[2],
	(int(sys.argv[3]), int(sys.argv[3])),
	int(sys.argv[4])
)
print 'Done'
