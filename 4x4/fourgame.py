import pygame
import pygame.font
import pygame.sysfont
from pygame.surface import Surface
from pygame.color import Color
from typing import Tuple, Union, Sequence
import copy
import random
import math
import time
from map_data.map1 import get_map1
from map_data.map2 import get_map2
from map_data.map3 import get_map3

pygame.init()

display_size = [900, 700]
dis = pygame.display.set_mode(display_size, pygame.SRCALPHA)
dis_flip = pygame.Surface(display_size, pygame.SRCALPHA)
pygame.display.set_caption("4x4")
pygame.mixer.music.load("music/Sunburst_NCS.mp3")
pygame.mixer.music.set_volume(1)

player_dis = pygame.Surface((100, 100), pygame.SRCALPHA)
ball_dis = pygame.Surface((100, 100), pygame.SRCALPHA)
pause_dis = pygame.Surface(display_size, pygame.SRCALPHA)
laser_dis = pygame.Surface((100, 900), pygame.SRCALPHA)
font = pygame.sysfont.SysFont('arial', 30)

class Draw(object):
    def Board():
        for col in range(5):
            pygame.draw.line(dis, white, (display_size[0]//2-200+100*col, display_size[1]//2-200),
                             (display_size[0]//2-200+100*col, display_size[1]//2+200), 5)
        for row in range(5):
            pygame.draw.line(dis, white, (display_size[0]//2-200, display_size[1]//2-200+100*row),
                             (display_size[0]//2+200, display_size[1]//2-200+100*row), 5)

    def Player():
        global player_alpha, player_hp_minus, player_hp_stack
        for r in range(10):
            player_alpha -= r/9*255
            if player_hp_minus:
                player_alpha += abs(abs(100-player_hp_stack)-100)/5
            if player_alpha < 0:
                player_alpha = 0
            if player_alpha > 255:
                player_alpha = 255
            
            pygame.draw.circle(player_dis, (player_color[0], player_color[1], player_color[2], 255-player_alpha), (50, 50), 33-r)
            player_alpha += r/9*255
        if hitbox:
            pygame.draw.lines(player_dis, yellow, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)
        player_painting = pygame.transform.rotate(player_dis, 0)
        dis.blit(player_painting, player_painting.get_rect(center=(player_pos[0], player_pos[1])))

    def Pause():
        pygame.draw.rect(pause_dis, (0, 0, 0, 130), (0, 0, display_size[0], display_size[1]))
        if player_hp > 0:
            Draw.Text(pause_dis, pause_text, pause_text_color, (display_size[0]//2, display_size[1]//2-100), 70, 0, True)
            if hitbox:
                pass
                #Draw.Text(pause_dis, "HITBOX : ON", black, (display_size[0]//2, display_size[1]//2-100), 70, 0, True)
            if not hitbox:
                pass
                #Draw.Text(pause_dis, "HITBOX : OFF", black, (display_size[0]//2, display_size[1]//2-100), 70, 0, True)
        else:
            Draw.Text(pause_dis, "G A M E  O V E R", red, (display_size[0]//2, display_size[1]//2-100), 70, 0, True)
        pause_painting = pygame.transform.rotate(pause_dis, 0)
        dis.blit(pause_painting, pause_painting.get_rect(center=(display_size[0]//2, display_size[1]//2)))

    def Text(
        surface: Surface,
        text: str,
        color: Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]],
        text_pos: Tuple[int, int],
        text_size: int = 20,
        text_angle: int = 0,
        center: bool = False
        ):
        global font
        font = pygame.sysfont.SysFont('arial', text_size)
        text_surface = font.render(text, True, color)
        text_t = pygame.transform.rotate(text_surface, text_angle)
        if center:
            surface.blit(text_t, text_t.get_rect(center=text_pos))
        else:
            surface.blit(text_t, (text_pos[0], text_pos[1]))

class enermy():
    def Ball():
        for objs in map_list[:map_level]:
            if len(objs) > 0:
                for obj in objs:
                    if isinstance(obj, Ball):
                        if not pause:
                            obj.Move()
                        obj.Show()
                    if isinstance(obj, VBall):
                        if not pause:
                            obj.Move()
                        obj.Show()
                    if isinstance(obj, Zoom):
                        if not pause:
                            obj.Move()
                    if isinstance(obj, Rotate):
                        if not pause:
                            obj.Move()
                for obj in range(len(objs)-1, -1, -1):
                    if objs[obj] != 4 and objs[obj] != 2:
                        if not isinstance(objs[obj], Laser):
                            if not isinstance(objs[obj], TBall):
                                if objs[obj].Delete():
                                    objs.pop(obj)
        for balls in map_list[:map_level+8]:
            if len(balls) > 0:
                for ball in balls:
                    if isinstance(ball, TBall):
                        if not pause:
                            ball.Move()
                        ball.Show()
                for ball in range(len(balls)-1, -1, -1):
                    if balls[ball] != 4:
                        if isinstance(balls[ball], TBall):
                            if balls[ball].Delete():
                                balls.pop(ball)
        for lasers in map_list[:map_level+16]:
            if len(lasers) > 0:
                for laser in lasers:
                    if isinstance(laser, Laser):
                        if not pause:
                            laser.Move()
                        laser.Show()
                for laser in range(len(lasers)-1, -1, -1):
                    if isinstance(lasers[laser], Laser):
                        if lasers[laser].Delete():
                            lasers.pop(laser)


class Ball(object):
    def Set(
        self,
        position: Tuple[int, int],
        speed: Tuple[int, int]
        ):
        self.pos = position
        self.speed = speed
        self.ball_dis = ball_dis

    def Move(
        self
        ):
        global player_hp_minus
        self.pos = (self.pos[0]+self.speed[0], self.pos[1]+self.speed[1])
        if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-20, self.pos[1]-20), (self.pos[0]+20, self.pos[1]+20))):
            if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                player_hp_minus = True

    def Delete(
        self
        ) -> bool:
        if not -500 < self.pos[0] < display_size[0]+500 or not -400 < self.pos[1] < display_size[1]+400:
            return True
        return False

    def Show(
        self
        ):
        self.ball_dis.fill(pygame.SRCALPHA)
        for r in range(10):
            pygame.draw.circle(self.ball_dis, (255, 255, 255, r/9*255), (50, 50), 33-r)
        if hitbox:
            pygame.draw.lines(self.ball_dis, red, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)
        self.ball_painting = pygame.transform.rotate(ball_dis, 0)
        dis.blit(self.ball_painting, self.ball_painting.get_rect(center=self.pos))

class TBall(object):
    def Set(
        self,
        position: Tuple[int, int, int],
        length: int,
        speed: int = 3,
        turn: int = 1
        ):
        self.position = position[0:2]
        self.pos = position[0:2]
        self.angle = position[2]
        self.length = length
        self.speed = speed/length
        self.turn = turn+position[2]
        self.ball_dis = ball_dis
        self.stage = 0
        self.delay = 100
        self.delete = False

    def Move(
        self
        ):
        global player_hp_minus
        if self.stage == 0:
            self.pos = [math.cos(self.angle)*self.length+self.position[0], math.sin(self.angle)*self.length+self.position[1]]
            self.delay -= 2
            if self.delay <= 0:
                self.delay = 100
                self.stage = 1
        if self.stage == 1:
            self.pos = [math.cos(self.angle)*self.length+self.position[0], math.sin(self.angle)*self.length+self.position[1]]
            self.angle += self.speed
            if self.angle >= self.turn:
                self.delete = True
            if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-20, self.pos[1]-20), (self.pos[0]+20, self.pos[1]+20))):
                if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                    player_hp_minus = True
    
    def Delete(
        self
        ) -> bool:
        if self.delete:
            return True
        return False

    def Show(
        self
        ):
        self.ball_dis.fill(pygame.SRCALPHA)
        if self.stage == 0:
            pygame.draw.arc(self.ball_dis, red, (50-33, 50-33, 66, 66), math.pi/2, math.pi/2-self.delay/100*math.pi*2, 5)
            Draw.Text(self.ball_dis, "!", red, (50, 50), 50, 0, True)
        if self.stage == 1:
            for r in range(10):
                pygame.draw.circle(self.ball_dis, (200, 200, 255, r/9*255), (50, 50), 33-r)
            if hitbox:
                pygame.draw.lines(self.ball_dis, red, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)
        self.ball_paint = pygame.transform.rotate(ball_dis, 0)
        self.ball_painting = pygame.transform.flip(self.ball_paint, True, False)
        dis.blit(self.ball_painting, self.ball_painting.get_rect(center=self.pos))

class VBall(object):
    def Set(
        self,
        position: Tuple[int, int],
        face: int,
        max_move: int,
        speed: int
        ):
        self.pos = position
        self.face = face
        self.speed = speed
        self.spp = -1/(5*(max_move*0.4+1+(face%2-1)*0.4))
        self.ball_dis = ball_dis

    def Move(
        self
        ):
        global player_hp_minus
        if self.face == 0:
            self.speed = (self.speed[0], self.speed[1]+self.spp)
        if self.face == 1:
            self.speed = (self.speed[0]-self.spp, self.speed[1])
        if self.face == 2:
            self.speed = (self.speed[0], self.speed[1]-self.spp)
        if self.face == 3:
            self.speed = (self.speed[0]+self.spp, self.speed[1])
        self.pos = (self.pos[0]+self.speed[0], self.pos[1]+self.speed[1])
        if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-20, self.pos[1]-20), (self.pos[0]+20, self.pos[1]+20))):
            if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                player_hp_minus = True

    def Delete(
        self
        ) -> bool:
        if not -500 < self.pos[0] < display_size[0]+500 or not -400 < self.pos[1] < display_size[1]+400:
            return True
        return False

    def Show(
        self
        ):
        self.ball_dis.fill(pygame.SRCALPHA)
        for r in range(10):
            pygame.draw.circle(self.ball_dis, (255, 200, 200, r/9*255), (50, 50), 33-r)
        if hitbox:
            pygame.draw.lines(self.ball_dis, red, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)
        self.ball_painting = pygame.transform.rotate(self.ball_dis, 0)
        dis.blit(self.ball_painting, self.ball_painting.get_rect(center=self.pos))

class Laser(object):
    def Set(
        self,
        position: Tuple[int, int],
        face: int
        ):
        self.pos = position
        self.face = face
        self.stage = 0
        self.speed = 6.28
        self.delay = 0
        self.delete = False
        self.laser_dis = laser_dis
    
    def Move(
        self
        ):
        global player_hp_minus
        if self.stage == 0:
            if self.face == 0:
                self.pos = [self.pos[0], self.pos[1]+self.speed]
                if self.pos[1] >= display_size[1]//2-300:
                    self.stage = 1
            if self.face == 1:
                self.pos = [self.pos[0]-self.speed, self.pos[1]]
                if self.pos[0] <= display_size[0]//2+300:
                    self.stage = 1
            if self.face == 2:
                self.pos = [self.pos[0], self.pos[1]-self.speed]
                if self.pos[1] <= display_size[1]//2+300:
                    self.stage = 1
            if self.face == 3:
                self.pos = [self.pos[0]+self.speed, self.pos[1]]
                if self.pos[0] >= display_size[0]//2-300:
                    self.stage = 1
            self.speed -= 0.1
            self.delay = 20
        
        if self.stage == 1:
            self.delay -= 1
            if self.delay <= 0:
                self.delay = 50
                self.stage = 2
        
        if self.stage == 2:
            self.delay -= 1
            if self.face == 0:
                if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-25, self.pos[1]+45), (self.pos[0]+25, self.pos[1]+945))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
                if Crash(((player_pos[0], player_pos[1]), (player_pos[0], player_pos[1])), ((self.pos[0]-25, self.pos[1]+45), (self.pos[0]+25, self.pos[1]+945))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
            if self.face == 1:
                if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-45, self.pos[1]-25), (self.pos[0]-945, self.pos[1]+25))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
                if Crash(((player_pos[0], player_pos[1]), (player_pos[0], player_pos[1])), ((self.pos[0]-945, self.pos[1]-25), (self.pos[0]-45, self.pos[1]+25))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
            if self.face == 2:
                if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]-25, self.pos[1]-945), (self.pos[0]+25, self.pos[1]-45))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
                if Crash(((player_pos[0], player_pos[1]), (player_pos[0], player_pos[1])), ((self.pos[0]-25, self.pos[1]-945), (self.pos[0]+25, self.pos[1]-45))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
            if self.face == 3:
                if Crash(((player_pos[0]-20, player_pos[1]-20), (player_pos[0]+20, player_pos[1]+20)), ((self.pos[0]+945, self.pos[1]-25), (self.pos[0]+45, self.pos[1]+25))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
                if Crash(((player_pos[0], player_pos[1]), (player_pos[0], player_pos[1])), ((self.pos[0]+45, self.pos[1]-25), (self.pos[0]+945, self.pos[1]+25))):
                    if not player_hp_minus and (abs(player_move[0]) != 30 and abs(player_move[1]) != 30):
                        player_hp_minus = True
            if self.delay <= 0:
                self.stage = 3
        
        if self.stage == 3:
            if self.face == 0:
                self.pos = [self.pos[0], self.pos[1]-self.speed]
                if self.pos[1] <= display_size[1]//2-400:
                    self.delete = True
            if self.face == 1:
                self.pos = [self.pos[0]+self.speed, self.pos[1]]
                if self.pos[0] >= display_size[0]//2+500:
                    self.delete = True
            if self.face == 2:
                self.pos = [self.pos[0], self.pos[1]+self.speed]
                if self.pos[1] >= display_size[1]//2+400:
                    self.delete = True
            if self.face == 3:
                self.pos = [self.pos[0]-self.speed, self.pos[1]]
                if self.pos[0] <= display_size[0]//2-500:
                    self.delete = True
            self.speed += 0.1
    
    def Delete(
        self
        ) -> bool:
        if self.delete:
            return True
        return False
    
    def Show(
        self
        ):
        self.laser_dis.fill(pygame.SRCALPHA)
        if self.stage == 2:
            for r in range(20):
                pygame.draw.rect(self.laser_dis, (255, 100, 100, r/19*255), (25+r, 90, 50-r*2, 900))
            if hitbox:
                pygame.draw.lines(self.laser_dis, red, True, ((25, 95), (75, 95), (75, 995), (25, 995)), 1)
        for r in range(10):
            pygame.draw.circle(self.laser_dis, (255, 255, 255, r/9*255), (50, 50), 40-r, 35-r*2)
            pygame.draw.rect(self.laser_dis, (255, 255, 255, r/9*255), (20+r, 65+r, 60-r*2, 30-r*2))
        if hitbox:
            pygame.draw.lines(self.laser_dis, black, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)
        self.laser_painting = pygame.transform.rotate(self.laser_dis, -90*self.face)
        dis.blit(self.laser_painting, self.laser_painting.get_rect(center=(self.pos[0]+self.face%2*(self.face//2*2-1)*400, self.pos[1]-abs(self.face%2-1)*(self.face//2*2-1)*400)))

class Zoom(object):
    def Set(
        self,
        size: int = 1,
        speed: int = 1
        ):
        self.size = size
        if dis_change[3] > size:
            self.speed = speed*-1
        else:
            self.speed = speed
        self.delete = False
    
    def Move(
        self
        ):
        dis_change[3] += self.speed
        dis_change[4] += self.speed
        if dis_change[3] <= self.size and self.speed < 0:
            dis_change[3] = self.size
            dis_change[4] = self.size
            self.delete = True
        if dis_change[3] >= self.size and self.speed > 0:
            dis_change[3] = self.size
            dis_change[4] = self.size
            self.delete = True
    
    def Delete(
        self
        ) -> bool:
        if self.delete:
            return True
        return False

class Rotate(object):
    def Set(
        self,
        angle: int = 0,
        speed: int = 360
        ):
        self.angle = angle
        self.speed = speed
        self.delete = False
    
    def Move(
        self
        ):
        dis_change[0] += self.speed
        if dis_change[0] <= self.angle and self.speed < 0:
            dis_change[0] = self.angle
            self.delete = True
        if dis_change[0] >= self.angle and self.speed > 0:
            dis_change[0] = self.angle
            self.delete = True
    
    def Delete(
        self
        ) -> bool:
        if self.delete:
            return True
        return False

class Flip(object):
    def Set(
        self,
        flip_x: int = False,
        flip_y: int = False
        ):
        dis_change[1] = flip_x
        dis_change[2] = flip_y
        self.delete = True
    
    def Delete(
        self
        ) -> bool:
        if self.delete:
            return True
        return False
            





def setballs(
    stage: int
    ):
    global map_list, map_set
    if stage_choice == 1:
        map_list, map_set = get_map1(Ball, TBall, VBall, Laser)
    if stage_choice == 2:
        map_list, map_set = get_map2(Ball, TBall, VBall, Laser)
    if stage_choice == 3:
        map_list, map_set = get_map3(Ball, TBall, VBall, Laser, Zoom, Rotate)

def setb(
    map_level: int
    ):
    global map_list, map_set, map_max
    objs = map_list[map_level]
    obj_pos = map_set[map_level]
    for obj in range(len(objs)):
        if objs[obj] == 1 or isinstance(objs[obj], Ball):
            objs[obj] = Ball()
            if len(objs) > len(obj_pos):
                obj_pos.insert(len(obj_pos), [1, 0])
        if objs[obj] == 3 or isinstance(objs[obj], VBall):
            objs[obj] = VBall()
            if len(objs) > len(obj_pos):
                obj_pos.insert(len(obj_pos), [1, 0, 0])
        if objs[obj] == 11 or isinstance(objs[obj], Zoom):
            objs[obj] = Zoom()
            if len(objs) > len(obj_pos):
                obj_pos.insert(len(obj_pos), [1, 1])
        if objs[obj] == 12 or isinstance(objs[obj], Rotate):
            objs[obj] = Rotate()
            if len(objs) > len(obj_pos):
                obj_pos.insert(len(obj_pos), [0, 360])
        if objs[obj] == 13 or isinstance(objs[obj], Flip):
            objs[obj] = Flip()
            if len(objs) > len(obj_pos):
                obj_pos.insert(len(obj_pos), [False, False])
    for obj in range(len(objs)):
        if isinstance(objs[obj], Ball):
            if obj_pos[obj][0] == 0:
                objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2-400), (0, 5))
            if obj_pos[obj][0] == 1:
                objs[obj].Set((display_size[0]//2+500, display_size[1]//2-250+100*obj_pos[obj][1]), (-5, 0))
            if obj_pos[obj][0] == 2:
                objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2+400), (0, -5))
            if obj_pos[obj][0] == 3:
                objs[obj].Set((display_size[0]//2-500, display_size[1]//2-250+100*obj_pos[obj][1]), (5, 0))
        if isinstance(objs[obj], VBall):
            if obj_pos[obj][0] == 0:
                objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2-400), 0, obj_pos[obj][2], (0, 10))
            if obj_pos[obj][0] == 1:
                objs[obj].Set((display_size[0]//2+500, display_size[1]//2-250+100*obj_pos[obj][1]), 1, obj_pos[obj][2], (-10, 0))
            if obj_pos[obj][0] == 2:
                objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2+400), 2, obj_pos[obj][2], (0, -10))
            if obj_pos[obj][0] == 3:
                objs[obj].Set((display_size[0]//2-500, display_size[1]//2-250+100*obj_pos[obj][1]), 3, obj_pos[obj][2], (10, 0))
        if isinstance(objs[obj], Zoom):
            objs[obj].Set(obj_pos[obj][0], obj_pos[obj][1])
        if isinstance(objs[obj], Rotate):
            objs[obj].Set(obj_pos[obj][0], obj_pos[obj][1])
    
    if map_level+8 < map_max:
        objs = map_list[map_level+8]
        obj_pos = map_set[map_level+8]
        for obj in range(len(objs)):
            if objs[obj] == 1 or isinstance(objs[obj], Ball):
                objs[obj] = Ball()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 0])
            if objs[obj] == 2 or isinstance(objs[obj], TBall):
                objs[obj] = TBall()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [display_size[0]//2, display_size[1]//2, 0, 250, 3, math.pi*2])
            if objs[obj] == 3 or isinstance(objs[obj], VBall):
                objs[obj] = VBall()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 0, 0])
            if objs[obj] == 11 or isinstance(objs[obj], Zoom):
                objs[obj] = Zoom()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 1])
            if objs[obj] == 12 or isinstance(objs[obj], Rotate):
                objs[obj] = Rotate()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [0, 360])
            if objs[obj] == 13 or isinstance(objs[obj], Flip):
                objs[obj] = Flip()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [False, False])
            for obj in range(len(objs)):
                if isinstance(objs[obj], TBall):
                    objs[obj].Set(obj_pos[obj][0], obj_pos[obj][1], obj_pos[obj][2], obj_pos[obj][3])
    
    if map_level+16 < map_max:
        objs = map_list[map_level+16]
        obj_pos = map_set[map_level+16]
        for obj in range(len(objs)):
            if objs[obj] == 1 or isinstance(objs[obj], Ball):
                objs[obj] = Ball()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 0])
            if objs[obj] == 2 or isinstance(objs[obj], TBall):
                objs[obj] = TBall()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [display_size[0]//2, display_size[1]//2, 0, 250, 3, math.pi*2])
            if objs[obj] == 3 or isinstance(objs[obj], VBall):
                objs[obj] = VBall()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 0, 0])
            if objs[obj] == 4 or isinstance(objs[obj], Laser):
                objs[obj] = Laser()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 0])
            if objs[obj] == 11 or isinstance(objs[obj], Zoom):
                objs[obj] = Zoom()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [1, 1])
            if objs[obj] == 12 or isinstance(objs[obj], Rotate):
                objs[obj] = Rotate()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [0, 360])
            if objs[obj] == 13 or isinstance(objs[obj], Flip):
                objs[obj] = Flip()
                if len(objs) > len(obj_pos):
                    obj_pos.insert(len(obj_pos), [False, False])
        for obj in range(len(objs)):
            if isinstance(objs[obj], Laser):
                if obj_pos[obj][0] == 0:
                    objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2-400), obj_pos[obj][0])
                if obj_pos[obj][0] == 1:
                    objs[obj].Set((display_size[0]//2+500, display_size[1]//2-250+100*obj_pos[obj][1]), obj_pos[obj][0])
                if obj_pos[obj][0] == 2:
                    objs[obj].Set((display_size[0]//2-250+100*obj_pos[obj][1], display_size[1]//2+400), obj_pos[obj][0])
                if obj_pos[obj][0] == 3:
                    objs[obj].Set((display_size[0]//2-500, display_size[1]//2-250+100*obj_pos[obj][1]), obj_pos[obj][0])



def Crash(
    pos1: Tuple[Tuple[int, int], Tuple[int, int]],
    pos2: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> bool:
    for count2 in range(2):
        for count1 in range(2):
            if pos2[0][0] <= pos1[count1][0] <= pos2[1][0] and pos2[0][1] <= pos1[count2][1] <= pos2[1][1]:
                return True
    return False




white = (255, 255, 255)
gray = (100, 100, 100)
black = (0, 0, 0)
red = (255, 10, 10)
orange = (255, 150, 10)
yellow = (255, 255, 10)
green = (10, 255, 10)
blue = (170, 170, 255)

pause_text = "start with space"
pause_text_color = orange
game_base = "loby"
stage_choice = 1

Restart = True
pause = False
pause_time = 100
hitbox = False
blackbox = False


while Restart:
    dis_change = [0, False, False, 1, 1]

    player_pos = [display_size[0]//2-50, display_size[1]//2-50]
    player_move_stack = 0
    player_move = [0, 0]
    player_color = (10, 255, 10)
    player_alpha = 255
    player_hp = 3
    player_hp_minus = False
    player_hp_stack = 200

    score = 0
    clock = pygame.time.Clock()
    tick = 60

    Running = True
    Restart = False

    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(1)
    if game_base != "game":
        pygame.mixer.music.set_volume(0.3)
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player_move_stack == 0:
                    if player_pos[1] > display_size[1]//2-150:
                        player_move = [0, -10]
                    else:
                        player_move = [0, 30]
                    player_move_stack = 10
                elif event.key == pygame.K_s and player_move_stack == 0:
                    if player_pos[1] < display_size[1]//2+150:
                        player_move = [0, 10]
                    else:
                        player_move = [0, -30]
                    player_move_stack = 10
                elif event.key == pygame.K_a and player_move_stack == 0:
                    if player_pos[0] > display_size[0]//2-150:
                        player_move = [-10, 0]
                    else:
                        player_move = [30, 0]
                    player_move_stack = 10
                elif event.key == pygame.K_d and player_move_stack == 0:
                    if player_pos[0] < display_size[0]//2+150:
                        player_move = [10, 0]
                    else:
                        player_move = [-30, 0]
                    player_move_stack = 10
                if event.key == pygame.K_h:
                    hitbox = not hitbox
                if event.key == pygame.K_b:
                    blackbox = not blackbox
            keys = pygame.key.get_pressed()
            if game_base == "loby":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                            if player_pos[0] == 400 and player_pos[1] == 200:
                                if 0 < stage_choice < 4:
                                    game_base = "game"
                                    setballs(stage_choice)
                                    pause = True
                                    map_level = 0
                                    map_max = len(map_list)
                                    map_delay = 0
                                    pause_time = 100
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.play(1)
                                    pygame.mixer.music.set_volume(1)
                            if player_pos[0] == 600 and player_pos[1] == 300:
                                if stage_choice > 1:
                                    stage_choice -= 1
                                    if stage_choice == 1:
                                        pygame.mixer.music.load("music/Sunburst_NCS.mp3")
                                    if stage_choice == 2:
                                        pygame.mixer.music.load("music/DaDiDuDonut.mp3")
                                    if stage_choice == 3:
                                        pygame.mixer.music.load("music/MintParfait.mp3")
                                    if stage_choice == 4:
                                        pygame.mixer.music.load("music/SmokedTurkeyRag.mp3")
                                    if stage_choice == 5:
                                        pygame.mixer.music.load("music/Butterfly.mp3")
                                    if stage_choice == 6:
                                        pygame.mixer.music.load("music/MyLittleHero.mp3")
                                    pygame.mixer.music.play(-1)
                            if player_pos[0] == 600 and player_pos[1] == 500:
                                if stage_choice < 6:
                                    stage_choice += 1
                                    if stage_choice == 1:
                                        pygame.mixer.music.load("music/Sunburst_NCS.mp3")
                                    if stage_choice == 2:
                                        pygame.mixer.music.load("music/DaDiDuDonut.mp3")
                                    if stage_choice == 3:
                                        pygame.mixer.music.load("music/MintParfait.mp3")
                                    if stage_choice == 4:
                                        pygame.mixer.music.load("music/SmokedTurkeyRag.mp3")
                                    if stage_choice == 5:
                                        pygame.mixer.music.load("music/Butterfly.mp3")
                                    if stage_choice == 6:
                                        pygame.mixer.music.load("music/MyLittleHero.mp3")
                                    pygame.mixer.music.play(-1)
            if game_base == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        Restart = True
                        Running = False
                        setballs(stage_choice)
                        pause_text = "P A U S E"
                        map_level = 0
                        map_max = len(map_list)
                        map_delay = 0
                        print("Restart game")
                        pygame.mixer.music.stop()
                        pygame.mixer.music.play(1)
                        pygame.mixer.music.set_volume(1)
                    else:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                            pause = not pause
                    if pause_text == "P E R F E C T" or pause_text == "G R E A T" or pause_text == "G O O D" or pause_text == "B A D":
                        if event.key == pygame.K_SPACE:
                            game_base = "loby"
                            pause_text = "P A U S E"
                            pause_text_color = orange
                            Running = False
                            Restart = True
                if event.type == pygame.KEYUP:
                    if game_base == "game":
                        if event.key == pygame.K_ESCAPE:
                            pause_time = 100
        if game_base == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and pause:
                pause_time -= 1
                if pause_time <= 0:
                    game_base = "loby"
                    Running = False
                    Restart = True
        
        if game_base == "loby":
            dis.fill(gray)
            Draw.Board()
            Draw.Text(dis, "start", green, (400, 200), 50, 0, True)
            Draw.Text(dis, "<", blue, (600, 300), 100, -90, True)
            Draw.Text(dis, "stage", white, (500, 400), 40, 0, True)
            Draw.Text(dis, f"{stage_choice}", white, (600, 400), 70, 0, True)
            Draw.Text(dis, ">", blue, (600, 500), 100, -90, True)

            Draw.Player()
            # player 움직이기
            player_pos[0] += player_move[0]
            player_pos[1] += player_move[1]
            if player_move_stack != 0:
                player_move_stack -= 1
            if player_move_stack == 0:
                player_move = [0, 0]
            
            # 노래
            stage_song_name = ["Sunburst", "DaDiDu Donut", "Mint Parfait", "Smoked Turkey Rag", "Butterfly", "My Little Hero"]
            stage_song_made = ["NCS", "a_hisa", "a_hisa", "a_hisa", "a_hisa", "a_hisa"]
            Draw.Text(dis, f"{stage_song_name[stage_choice-1]}", orange, (450, 600), 50, 0, True)
            pygame.draw.line(dis, white, (450-len(stage_song_name[stage_choice-1])*7, 630), (450+len(stage_song_name[stage_choice-1])*7, 630), 5)
            Draw.Text(dis, f"{stage_song_made[stage_choice-1]}", black, (450, 650), 30, 0, True)

        if game_base == "game":
            if pause:
                pygame.mixer.music.pause()
                dis.fill(gray)
                Draw.Board()
                Draw.Player()
                enermy.Ball()
                if player_hp > 0:
                    pygame.draw.rect(dis, black, (195, 5, 510, 25), 0, 10)
                else:
                    pygame.draw.rect(dis, white, (195, 5, 510, 25), 0, 10)
                pygame.draw.rect(dis, player_color, (200, 10, score, 15), 0, 10)
                if blackbox:
                    pygame.draw.rect(dis, black, (0, 0, 100, display_size[1]))
                    pygame.draw.rect(dis, black, (display_size[0]-100, 0, 100, display_size[1]))
                

                Draw.Pause()
                pygame.draw.arc(dis, red, (10, 10, 50, 50), math.pi/2, math.pi/2-pause_time/100*math.pi*2)
                if player_hp == 0:
                    player_color = black

            if not pause:
                pygame.mixer.music.unpause()
                # player 움직이기
                player_pos[0] += player_move[0]
                player_pos[1] += player_move[1]
                if player_move_stack != 0:
                    player_move_stack -= 1
                if player_move_stack == 0:
                    player_move = [0, 0]

                if player_hp_minus:
                    player_hp_stack -= 2
                    if player_hp == 3:
                        player_color = yellow
                    if player_hp == 2:
                        player_color = red
                    if player_hp == 1:
                        player_hp = 0
                        #pause = True
                    if player_hp == 0:
                        player_color = black
                else:
                    player_alpha = 255
                if player_hp_stack <= 0:
                    player_hp -= 1
                    player_hp_minus = False
                    player_hp_stack = 200

                # 배경 그리기
                dis.fill(gray)
                Draw.Board()

                # player 그리기
                Draw.Player()

                # 장해물 그리기
                if pause_text != "P E R F E C T" and pause_text != "G R E A T" or pause_text != "G O O D" or pause_text != "B A D":
                    map_delay -= 1
                if map_delay <= 0:
                    if map_level == map_max:
                        map_clear = True
                        for balls in map_list:
                            if len(balls) > 0:
                                map_clear = False
                        if map_clear:
                            map_delay = 1
                            pause = True
                            pause_text_color = green
                            if player_hp == 3:
                                pause_text = "P E R F E C T"
                            if player_hp == 2:
                                pause_text = "G R E A T"
                            if player_hp == 1:
                                pause_text = "G O O D"
                            if player_hp == 0:
                                pause_text = "B A D"
                    else:
                        setb(map_level)
                        map_level += 1
                        map_delay = 5
                enermy.Ball()
        
        dis_flip = pygame.transform.flip(dis, dis_change[1], dis_change[2])
        dis_flip = pygame.transform.scale(dis_flip, (display_size[0]*abs(dis_change[3]), display_size[1]*abs(dis_change[4])))
        dis_flip = pygame.transform.rotate(dis_flip, dis_change[0])
        dis.fill(gray)
        dis.blit(dis_flip, dis_flip.get_rect(center=(display_size[0]/2, display_size[1]/2)))
        if game_base == "game":
            #스코어
            if not pause:
                if map_level < map_max and player_hp > 0:
                    score += 1/(map_max*5)*500
                if map_level+1 == map_max:
                    score += 1/(map_max*5)*500
            if player_hp > 0:
                pygame.draw.rect(dis, black, (195, 5, 510, 25), 0, 10)
            else:
                pygame.draw.rect(dis, white, (195, 5, 510, 25), 0, 10)
            pygame.draw.rect(dis, player_color, (200, 10, score, 15), 0, 10)

            if blackbox:
                pygame.draw.rect(dis, black, (0, 0, 100, display_size[1]))
                pygame.draw.rect(dis, black, (display_size[0]-100, 0, 100, display_size[1]))

            #게임 이탈
            pygame.draw.arc(dis, red, (10, 10, 50, 50), math.pi/2, math.pi/2-pause_time/100*math.pi*2)
        pygame.display.update()
        clock.tick(tick)
    pygame.mixer.music.stop()
pygame.quit()
print("Quit game")

