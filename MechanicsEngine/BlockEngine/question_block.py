import pygame
import copy
import math

class _question_block:

	def __init__(self):

		self.question_block_trigger= False
		self.theta = 1
		self.step = .1
		self.question_block_object = None
		self.hit_state_path = './Assets/Platforms/question_block_states/question_block_hit_32x32.png'
	
	def main_loop(self,GameObjects,levelObjects,PlayerEngine):
		
		self.handle_question_blocks(GameObjects,levelObjects,PlayerEngine)
		
		if self.question_block_trigger:

			self.question_block_animation(self.question_block_object)
			self.question_block_hit(self.question_block_object)


	def handle_question_blocks(self,GameObjects,levelObjects,PlayerEngine):

		for objects in GameObjects:
			if objects.subClass == 'player':
				if objects.collisionUp and objects.collisionSubClass == 'platform':
					if "Question" in objects.collisionObject.imagePath:
						self.question_block_object = objects.collisionObject
						self.question_block_trigger = True

	def question_block_hit(self,questionBlock):
		questionBlock.imagePath = self.hit_state_path
		questionBlock._set_image()
		questionBlock.hit = True
	def question_block_animation(self,objects):

		objects.position[1] += 2*math.cos(self.theta*math.pi)
		self.theta -= self.step

		if self.theta <= 0:
			self.question_block_trigger = False
			self.theta = 1