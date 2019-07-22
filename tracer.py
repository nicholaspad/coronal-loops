import matplotlib.pyplot as plt
import numpy as np

class Tracer(object):

	def __init__(self):
		self.fov_radius = 3.0
		self.o_vector = np.array([0,0])
		self.dy = 0
		self.dx = 0
		self.coefficients = np.array([0,0,0])

	def load_image(self, ar):
		self.img = ar
		self.dim_x = ar.shape[1]
		self.dim_y = ar.shape[0]
		self.blank = np.zeros(img.shape)

	def find_start_loc(self):
		# TODO: automated way to find a starting location for tracing
		self.x = 0
		self.y = 0

	def make_weighted_map(self):
		pass