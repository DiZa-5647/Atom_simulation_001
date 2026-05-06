import pygame
from pygame.math import Vector3
from math import *
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))

is_show_forces = True

class Atom:
    def __init__(self,
                 pos=(0,0),
                 radius=10,
                 mass=1):
        self.pos = Vector3(pos[0], pos[1], 0)
        self.radius = radius
        self.mass = mass
        self.velocity = Vector3(0,0,0)
        self.acceleration = Vector3(0,0,0)
        if mass>0: self.color = (255,255,0)
        elif mass==0: self.color = (255,255,255)
        elif mass<0: self.color = (240,130,130)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        if is_show_forces:
            pygame.draw.line(surface, (255,255,255), (self.pos.x,self.pos.y), (self.pos.x+self.velocity.x,self.pos.y+self.velocity.y), width=1)
    
    def formula_01(self, other_atom):
        if other_atom.mass==0 or self.mass==0: return 0
        G=1000
        direction = other_atom.pos - self.pos
        distance = direction.length()
        if distance>500 or distance<0.2:return
        force_direction = direction.normalize()
        force_magnitude = -G*((self.mass * other_atom.mass)/distance**2)
        force = force_direction * force_magnitude
        self.acceleration+=force

    def formula_02(self, other_atom):
        if other_atom.mass==0 or self.mass==0: return 0
        A=1
        B=1
        G=1
        D=1
        direction = other_atom.pos - self.pos
        distance = D*direction.length()
        force_direction = direction.normalize()
        force_magnitude = G*((A/(distance**13))-(B/(distance**7)))+0.22416
        force = force_direction * force_magnitude
        self.acceleration+=force

    def lennard_jones_force(self, other_atom, epsilon, sigma):
        if other_atom.mass == 0 or self.mass == 0: 
            return Vector3(0,0,0)

        direction_vec = other_atom.pos - self.pos
        r = direction_vec.length()
        
        if r == 0:
            return Vector3(0,0,0)
            
        force_direction = direction_vec.normalize()
        sig_over_r = sigma / r
        # F = 24 * epsilon * [ 2*(sig/r)^13 - (sig/r)^7 ] * (1/r) * direction
        force_magnitude = 24.0 * epsilon * (2.0 * (sig_over_r ** 13) - (sig_over_r ** 7)) / r
        
        force = force_direction * force_magnitude
        
        # По Третьему закону Ньютона:
        self.acceleration += force / self.mass

    def apply_gravity(self, other_atom):
        direction = other_atom.pos - self.pos
        distance = direction.length()
        if distance < self.radius-other_atom.radius:return #==============
        # self.lennard_jones_force(other_atom,epsilon=0.2,sigma=3)
        self.formula_01(other_atom)

    def update(self, dt):
        K=1.0
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.velocity.x = -self.velocity.x * K
        
        if self.pos.x + self.radius > WIDTH:
            self.pos.x = WIDTH - self.radius
            self.velocity.x = -self.velocity.x * K
        
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.velocity.y = -self.velocity.y * K
        
        if self.pos.y + self.radius > HEIGHT:
            self.pos.y = HEIGHT - self.radius
            self.velocity.y = -self.velocity.y * K
        
        self.acceleration = Vector3(0,0,0)

atoms = [Atom(pos=(WIDTH//2 - 3, HEIGHT//2), mass=10),
         Atom(pos=(WIDTH//2, HEIGHT//2), mass=10)]
atoms[0].velocity=Vector3(0,0,0)

all_energy = 0

font = pygame.font.Font(None, 24)
running = True
clock = pygame.time.Clock()

pause = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                atoms.append(Atom(pos=event.pos, mass=10))
            elif event.button == 3:
                atoms.append(Atom(pos=event.pos, mass=-10))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                atoms = []
            elif event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
            elif event.key == pygame.K_SPACE:
                pause = not pause
            elif event.key == pygame.K_f:
                is_show_forces = not is_show_forces
    if not pause:
        screen.fill((0,0,0))
        
        for i, a in enumerate(atoms):
            for b in atoms[i+1:]:
                a.apply_gravity(b)
                b.apply_gravity(a)
        all_energy=0
        for atom in atoms:
            atom.update(dt)
            all_energy+=atom.velocity.length()
            atom.draw(screen)
        

        fps = int(clock.get_fps())
        info_text = f"FPS: {fps} | Energy: {int(all_energy)} | Count: {len(atoms)}"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()

pygame.quit()