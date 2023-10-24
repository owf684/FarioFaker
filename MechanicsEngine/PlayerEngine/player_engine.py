import copy
import math
import sys

sys.path.append('./GameObjects')
sys.path.append('./AnimationSystem')
import anim_util
import block_object
import fire_power


class PlayerEngine(anim_util.AnimUtil):

    def __init__(self):
        super().__init__()
        self.gravity = 9.8 * 150
        self.y_displacement = 0
        self.x_displacement = 0
        self.x_direction = 0
        self.x_decelleration = 0.1
        self.screen_width = 1280
        self.scroll_level = False
        self.x_acceleration = 0
        self.total_y_displacement = 0
        self.reached_max_height = False
        self.max_walk_velocity = 150
        self.max_run_velocity = 300
        self.superMario = False
        self.jump_latch = False
        self.runningFactor = 1
        self.supressDamage = False
        self.latch = False
        self.shoot_limit = 3
        self.shots_taken = 0
        self.delay_power = False
        self.time_after_shot = False
        self.shoot_delay_milliseconds = 500 # used to reset shots_taken after shots exceeds limit
        self.shoot_reset_milliseconds = 250 # used to reset shots_taken if shots do not exceed limit
        self.triggerJumpFX = False
        self.triggerFlowerPowerAudio = False
        self.triggerPowerUpAudio = False
        self.triggerBlockBreakAudio = False
        self.triggerDeathAudio = False
        self.triggerPowerDownAudio = False

    def main_loop(self, objects, delta_t, d_inputs, o_collision_engine, o_level_handler,l_game_objects):
        try:

            if objects.subClass == 'player':

                if not o_level_handler.pause_for_damage and not o_level_handler.trigger_death_animation and not o_level_handler.trigger_powerup_animation:
                
                    self.horizontal_movement(objects, delta_t, d_inputs, o_collision_engine, o_level_handler)
                    self.jump(objects, delta_t, d_inputs)
                    self.onEnemy(objects, d_inputs, o_level_handler)
                    self.handle_damage(objects, o_level_handler)
                    self.handle_flower_power_action(objects,d_inputs,o_level_handler,l_game_objects)
                    if self.time_after_shot:
                        self.shoot_reset()
                    if self.delay_power:
                        self.delay_flower_power()
            
                self.handle_power_ups(objects, o_level_handler)
            
                if o_level_handler.pause_for_damage or o_level_handler.trigger_death_animation or o_level_handler.trigger_powerup_animation:
                    self.scroll_level = False

            if isinstance(objects,fire_power.FirePower):
                self.handle_flower_power_object(objects)   

        except Exception as Error:

            print("runtime error in PlayerEngine.py::Function main_loop(): ", Error)

    def shoot_reset(self):
        if self.determine_time_elapsed() > self.shoot_reset_milliseconds and not self.delay_power:
            self.time_after_shot = False
            self.shots_taken = 0

    def delay_flower_power(self):
        try:

            if self.determine_time_elapsed() > self.shoot_delay_milliseconds:
                
                self.delay_power = False 
                self.shots_taken = 0

        except Exception as Error:

            print("runtime error in PlayerEngine.py::Function delay_flower_power(): ", Error)

    def handle_flower_power_object(self,objects):
        try:

            if objects.collisionDown:
            
                objects.velocityY = 150
            
        except Exception as Error:

            print("runtime error in PlayerEngine.py::handle_flower_power(): ", Error)

    def handle_power_ups(self, objects, o_level_handler):
        try:

            if objects.powerUp and not o_level_handler.pause_for_damage:
            
                if "super_mushroom" in objects.powerType and objects.power_up < 1:
                    objects.powerUp = False
                    o_level_handler.trigger_powerup_animation = True
                    objects.powerType = ''
                    self.triggerPowerUpAudio = True
                    objects.power_up = 1
                    self.superMario = True
                    objects.collisionObject.isHit = True
            
                if "flower_power" in objects.powerType and not objects.power_up == 2:
                    objects.powerUp = False
                    o_level_handler.trigger_powerup_animation = True
                    objects.powerType = ''
                    self.triggerPowerUpAudio = True
                    objects.collisionObject.isHit = True
                    objects.power_up = 2
                    self.superMario = True

        except Exception as Error:

            print("runtime error in PlayerEngine.py::Function handle_power_ups(): ", Error)

    def handle_flower_power_action(self,objects,d_inputs,o_level_handler, o_game_objects):
        try:
            if d_inputs['attack'] == '1' and not self.latch and objects.power_up == 2 and not self.delay_power:
                self.shots_taken += 1
                
                self.latch =   True
                self.triggerFlowerPowerAudio = True
                if self.shots_taken > self.shoot_limit:
                    self.delay_power = True
                    self.reset_time_variables()
                    self.last_frame_time_2 = self.determine_time_elapsed()
                else:
                    self.reset_time_variables()
                    self.last_frame_time_2 = self.determine_time_elapsed()
                    self.time_after_shot = True
                    # Create FirePower Object
                    firePowerObject = fire_power.FirePower()
                    firePowerObject.velocityX = 300
                    firePowerObject.velocityY = 50
                    firePowerObject.position = copy.deepcopy(objects.position)
                    firePowerObject.imagePath = './Assets/PlayerSprites/FlowerPowerMario/fire_ball.png'                
                    firePowerObject._set_image()
                    firePowerObject._set_sprite_size(firePowerObject.image)
                    firePowerObject._set_rect(firePowerObject.sprite_size)
                    firePowerObject.isRendered = True
                    firePowerObject.jumping = True
                    firePowerObject.x_direction = objects.x_direction
                    firePowerObject.position[1] += 10
                
                    # handle direction and position accordingly
                    if firePowerObject.x_direction == 1:
                        firePowerObject.position[0] += 37
                    else:
                        firePowerObject.position[0] -= 10
               
                   # add to GameObjects to be processed in Render Buffer later
                    o_game_objects.append(firePowerObject)
            
            elif d_inputs['attack'] == '0' and self.latch:
                
                self.latch = False

        except Exception as Error:
            
            print("runtime error in PlayerEngine.py::Function handle_power(): ", Error)

    def handle_damage(self, objects, o_level_handler):
        try:

            if objects.isHit:
            
                if objects.power_up == 0:
                    o_level_handler.trigger_death_animation = True
                    self.triggerDeathAudio = True
                    objects.jumping = True
                    objects.velocityY = 0
            
                if objects.power_up > 0:
                    objects.isHit = False
                    o_level_handler.pause_for_damage = True
                    self.superMario = False
                    self.triggerPowerDownAudio = True

                elif objects.power_up == 0 and not o_level_handler.freeze_damage and not o_level_handler.trigger_death_animation:
                    o_level_handler.load_level = True
                    o_level_handler.edit_mode = True
        
            elif objects.position[1] > self.screen_width:
                o_level_handler.load_level = True
                o_level_handler.edit_mode = True
                self.triggerDeathAudio = True
        
            if objects.power_up == 0 and not objects.powerUp:
                self.superMario = False

            if o_level_handler.decrease_power:
                objects.power_up = 0
                o_level_handler.decrease_power = False

        except Exception as Error:
            
            print("runtime error in PlayerEngine.py::Function handle_damage(): ", Error)
    
    def onEnemy(self, objects,d_inputs, o_level_handler):
        try:
        
            if objects.subClass == 'player':
            
                if objects.onEnemy:
                    objects.velocityY = 250
                    objects.velocityX = 125
                    objects.jumping = True            
                    objects.onEnemy = False

        except Exception as Error:

            print("runtime error in PlayerEngine.py::Function onEnemy(): ", Error)

    def jump(self, objects, delta_t, d_inputs):
        try:

            if d_inputs['up'] == '1' and not self.reached_max_height:
                objects.velocityY = 300
                objects.jumping = True
                self.triggerJumpFX = True

            self.total_y_displacement += objects.y_displacement
        
            if self.total_y_displacement >= 90:
                self.reached_max_height = True

            if objects.collisionUp:
                self.reached_max_height = True
            
                if objects.velocityY > 0:
                    objects.velocityY *= -0.5
            
                self.total_y_displacement = 0
                objects.jumping = False
                self.triggerJumpFX = False
            if objects.collisionDown and objects.velocityY < 0:
            
                self.total_y_displacement = 0
                objects.jumping = False
                self.triggerJumpFX = False
                if self.reached_max_height:
                
                    if d_inputs['up'] == '0':
                        self.reached_max_height = False

        except Exception as Error:

            print("runtime Error in PlayerEngine.py::Function jump(): ", Error)

    def horizontal_movement(self, objects, delta_t, d_inputs, o_collision_engine, o_level_handler):
        try:

            self.set_scroll_state(objects, d_inputs, o_level_handler)

            if d_inputs['right'] == '1':
                objects.x_direction = 1

                if objects.velocityX >= 100*self.runningFactor:
                    objects.velociyX = 100 * self.runningFactor
                else:
                    objects.velocityX += 10 * self.runningFactor

            elif d_inputs['left'] == '-1':
                objects.x_direction = -1

                if objects.velocityX > 100*self.runningFactor:
                    objects.velocityX = 100 *self.runningFactor
                else:
                    objects.velocityX += 10 * self.runningFactor

            else:
                if objects.velocityX > 20:
                    objects.velocityX -= 300*delta_t
                elif objects.velocityX < -20:
                    objects.velocityX += 300*delta_t
                else:
                    objects.velocityX = 0
            if d_inputs['l-shift'] == '1':
                self.runningFactor = 1.5
            else:
                self.runningFactor = 1

            self.x_displacement = objects.x_displacement
            self.x_direction = objects.x_direction

        except Exception as Error:
            
            print("runtime Error in PlayerEngine.py::Function horizontal_movement(): ", Error)
    
    def set_scroll_state(self, objects, d_inputs, o_level_handler):
        try:

            # handle level scrolling left
            if objects.position[0] >= self.screen_width / 2 and self.x_direction > 0 and (d_inputs['right'] == '1' or objects.onEnemy):
                self.scroll_level = True
                objects.scrolling = True
            # handle level scrolling right
            elif objects.position[0] < self.screen_width / 2 and self.x_direction < 0 and (d_inputs[
                'left'] == '-1' or objects.onEnemy) and o_level_handler.scroll_offset > 0:
                self.scroll_level = True
                objects.scrolling = True
            else:
                self.scroll_level = False
                objects.scrolling = False

        except Exception as Error:
            
            print("runtime error in PlayerEngine.py::Function set_scroll_state(): ", Error)