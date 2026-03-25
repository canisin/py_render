import pygame
import math

class Vector:
    def __init__( self, x, y, z ):
        self.x = x
        self.y = y
        self.z = z

    def __str__( self ):
        return f"[ { self.x }, { self.y }, { self.z } ]"

    def __add__( lhs, rhs ):
        return Vector( lhs.x + rhs.x, lhs.y + rhs.y, lhs.z + rhs.z )

    def __iadd__( self, other ):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __neg__( vector ):
        return Vector( -vector.x, -vector.y, -vector.z )

    def __sub__( lhs, rhs ):
        return Vector( lhs.x - rhs.x, lhs.y - rhs.y, lhs.z - rhs.z )

    def __isub__( self, other ):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__( vector, scalar ):
        return Vector( vector.x * scalar, vector.y * scalar, vector.z * scalar )

    def __rmul__( vector, scalar ):
        return Vector( vector.x * scalar, vector.y * scalar, vector.z * scalar )

    def __imul__( self, scalar ):
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    def __truediv__( vector, scalar):
        return Vector( vector.x / scalar, vector.y / scalar, vector.z / scalar )

    def __rtruediv__( vector, scalar ):
        return Vector( vector.x / scalar, vector.y / scalar, vector.z / scalar )

    def __itruediv__( self, scalar ):
        self.x /= scalar
        self.y /= scalar
        self.z /= scalar
        return self

    def dot( lhs, rhs ):
        return lhs.x * rhs.x + lhs.y * rhs.y + lhs.z * rhs.z

    def len_sq( self ):
        return Vector.dot( self, self )

    def len( self ):
        return math.sqrt( self.len_sq() )

    def is_normal( self):
        return self.len_sq() == 1

    def normalize( self ):
        self /= self.len()
        return self

    def cross( lhs, rhs ):
        return Vector(
            lhs.y * rhs.z - lhs.z * rhs.y,
            lhs.z * rhs.x - lhs.x * rhs.z,
            lhs.x * rhs.y - lhs.y * rhs.x
        )

class Sphere:
    def __init__( self, position, radius, color ):
        self.position = position
        self.radius = radius
        self.color = color

    def calc_normal( self, point ):
        return ( point - self.position ).normalize()

    def intersect( self, origin, direction ):
        position = self.position - origin

        a = direction.len_sq()
        b = Vector.dot( position, direction )
        c = position.len_sq() - self.radius * self.radius

        d = b * b - a * c
        if d < 0: return math.inf

        t2 = ( b - math.sqrt( d ) ) / a
        return t2 if t2 > 0 else math.inf

class Camera:
    position = Vector( 0, 0, 0 )
    forward = Vector( 0, 0, 1 )
    up = Vector( 0, 1, 0 )
    left = Vector( -1, 0, 0 )

    def translate_up():
        Camera.position += Camera.up

    def translate_down():
        Camera.position -= Camera.up

    def translate_forward():
        Camera.position += Camera.forward

    def translate_backward():
        Camera.position -= Camera.forward

    def translate_left():
        Camera.position += Camera.left

    def translate_right():
        Camera.position -= Camera.left

    rotation_cos = math.cos( math.pi / 8 )
    rotation_sin = math.sin( math.pi / 8 )

    def rotate_up():
        forward = Camera.forward
        Camera.forward = Camera.rotation_cos * Camera.forward + Camera.rotation_sin * Camera.up
        Camera.up = Camera.rotation_cos * Camera.up - Camera.rotation_sin * forward

    def rotate_down():
        forward = Camera.forward
        Camera.forward = Camera.rotation_cos * Camera.forward - Camera.rotation_sin * Camera.up
        Camera.up = Camera.rotation_cos * Camera.up + Camera.rotation_sin * forward

    def rotate_left():
        left = Camera.left
        Camera.left = Camera.rotation_cos * Camera.left - Camera.rotation_sin * Camera.forward
        Camera.forward = Camera.rotation_cos * Camera.forward + Camera.rotation_sin * left

    def rotate_right():
        left = Camera.left
        Camera.left = Camera.rotation_cos * Camera.left + Camera.rotation_sin * Camera.forward
        Camera.forward = Camera.rotation_cos * Camera.forward - Camera.rotation_sin * left

canvas_width = 480
canvas_height = 480
viewport_distance = 1
viewport_width = 1
viewport_height = 1
viewport_max = 1000

def canvas_to_viewport( cx, cy ):
    vx = viewport_width * ( cx - canvas_width / 2 ) / canvas_width
    vy = viewport_height * ( canvas_height / 2 - cy ) / canvas_height

    return Camera.position + viewport_distance * Camera.forward \
        - vx * Camera.left + vy * Camera.up

class Light:
    ambient = 0
    point = 1
    directional = 2

    def __init__( self, type, intensity ):
        self.type = type
        self.intensity = intensity

    def Ambient( intensity ):
        self = Light( Light.ambient, intensity )
        return self

    def Point( intensity, position ):
        self = Light( Light.point, intensity )
        self.position = position
        return self

    def Directional( intensity, direction ):
        self = Light( Light.directional, intensity )
        self.direction = direction.normalize()
        return self

    def calc_intensity( self, point, normal ):
        if self.type == Light.ambient:
            return self.intensity

        if self.type == Light.point:
            direction = self.position - point
        elif self.type == Light.directional:
            direction = self.direction

        dot_product = Vector.dot( normal, direction )
        if dot_product <= 0: return 0
        return self.intensity * dot_product / ( direction.len() if self.type == Light.point else 1 )

class Scene:
    background = Vector( 255, 255, 255 )
    objects = [
        Sphere( Vector( 0, -1, 3 ), 1, Vector( 255, 0, 0 ) ),
        Sphere( Vector( 2, 0, 4 ), 1, Vector( 0, 0, 255 ) ),
        Sphere( Vector( -2, 0, 4 ), 1, Vector( 0, 255, 0 ) ),
        Sphere( Vector( 0, -5001, 0 ), 5000, Vector( 255, 255, 0 ) ),
    ]
    lights = [
        Light.Ambient( 0.2 ),
        Light.Point( 0.6, Vector( 2, 1, 0 ) ),
        Light.Directional( 0.2, Vector( 1, 4, 4 ) ),
    ]

# normalize light intensities
total_intensity = sum( light.intensity for light in Scene.lights )
for light in Scene.lights:
    light.intensity /= total_intensity

def find_intersection( origin, direction, t_min, t_max ):
    closest_t = math.inf
    closest_object = None

    for object in Scene.objects:
        t = object.intersect( origin, direction )

        if t < t_min: continue
        if t > t_max: continue

        if t < closest_t:
            closest_t = t
            closest_object = object

    return closest_object, closest_t

def ray_trace( cx, cy ):
    point = canvas_to_viewport( cx, cy )
    origin = Camera.position
    direction = point - origin
    object, distance = find_intersection( origin, direction, viewport_distance, viewport_max )
    if not object: return Scene.background
    intersection = origin + distance * direction
    normal = object.calc_normal( intersection )
    light = sum( light.calc_intensity( intersection, normal ) for light in Scene.lights )
    return object.color * light

pygame.init()
display = pygame.display.set_mode( ( canvas_width, canvas_height ) )
pygame.display.set_caption( "py-render" )

clock = pygame.time.Clock()

def put_pixel( x, y, color ):
    display.set_at( ( x, y ), ( color.x, color.y, color.z ) )

def render():
    for cx in range( canvas_width ):
        for cy in range( canvas_height ):
            color = ray_trace( cx, cy )
            put_pixel( cx, cy, color )

def exit():
    pygame.quit()
    raise SystemExit

paused = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()
            elif event.key == pygame.K_w:
                Camera.translate_forward()
            elif event.key == pygame.K_s:
                Camera.translate_backward()
            elif event.key == pygame.K_a:
                Camera.translate_left()
            elif event.key == pygame.K_d:
                Camera.translate_right()
            elif event.key == pygame.K_LSHIFT:
                Camera.translate_up()
            elif event.key == pygame.K_LCTRL:
                Camera.translate_down()
            elif event.key == pygame.K_UP:
                Camera.rotate_up()
            elif event.key == pygame.K_DOWN:
                Camera.rotate_down()
            elif event.key == pygame.K_LEFT:
                Camera.rotate_left()
            elif event.key == pygame.K_RIGHT:
                Camera.rotate_right()
            elif event.key == pygame.K_p:
                paused = not paused
                if paused: print( "paused!" )
                else: print( "resuming.." )

    if not paused:
        render()
        print( "tick" )
        print( Camera.position )
    pygame.display.update()
    clock.tick( 60 )
