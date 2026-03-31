import numpy as np
import pygame
import pygame.surfarray
import math
import multiprocessing
import ctypes

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
    def __init__( self, position, radius, color, specular ):
        self.position = position
        self.radius = radius
        self.color = color
        self.specular = specular

    def calc_normal( self, point ):
        return ( point - self.position ).normalize()

    def intersect( self, origin, direction ):
        position = self.position - origin

        b = Vector.dot( position, direction )
        c = position.len_sq() - self.radius * self.radius

        d = b * b - c
        if d < 0: return math.inf

        t2 = b - math.sqrt( d )
        return t2 if t2 > 0 else math.inf

class Camera:
    def __init__( self ):
        self.position = Vector( 0, 0, 0 )
        self.forward = Vector( 0, 0, 1 )
        self.up = Vector( 0, 1, 0 )
        self.left = Vector( -1, 0, 0 )

    def translate_up( self ):
        self.position += self.up

    def translate_down( self ):
        self.position -= self.up

    def translate_forward( self ):
        self.position += self.forward

    def translate_backward( self ):
        self.position -= self.forward

    def translate_left( self ):
        self.position += self.left

    def translate_right( self ):
        self.position -= self.left

    rotation_cos = math.cos( math.pi / 8 )
    rotation_sin = math.sin( math.pi / 8 )

    def rotate_up( self ):
        forward = self.forward
        self.forward = self.rotation_cos * self.forward + self.rotation_sin * self.up
        self.up = self.rotation_cos * self.up - self.rotation_sin * forward

    def rotate_down( self ):
        forward = self.forward
        self.forward = self.rotation_cos * self.forward - self.rotation_sin * self.up
        self.up = self.rotation_cos * self.up + self.rotation_sin * forward

    def rotate_left( self ):
        left = self.left
        self.left = self.rotation_cos * self.left - self.rotation_sin * self.forward
        self.forward = self.rotation_cos * self.forward + self.rotation_sin * left

    def rotate_right( self ):
        left = self.left
        self.left = self.rotation_cos * self.left + self.rotation_sin * self.forward
        self.forward = self.rotation_cos * self.forward - self.rotation_sin * left

camera = Camera()

canvas_width = 480
canvas_height = 480
viewport_distance = 1
viewport_width = 1
viewport_height = 1
viewport_max = 1000

def canvas_to_viewport( cx, cy ):
    vx = viewport_width * ( cx - canvas_width / 2 ) / canvas_width
    vy = viewport_height * ( canvas_height / 2 - cy ) / canvas_height

    return camera.position + viewport_distance * camera.forward \
        - vx * camera.left + vy * camera.up

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

    def calc_intensity( self, point, normal, view_direction, specular ):
        if self.type == Light.ambient:
            return self.intensity

        if self.type == Light.point:
            direction = self.position - point
        elif self.type == Light.directional:
            direction = self.direction

        dot_product = Vector.dot( normal, direction )
        if dot_product <= 0: return 0
        divisor = direction.len() if self.type == Light.point else 1
        intensity = self.intensity * dot_product / divisor

        if specular > 0:
            reflection_direction = 2 * normal * dot_product - direction
            dot_product = Vector.dot( reflection_direction, view_direction )
            if dot_product <= 0: return intensity
            intensity += self.intensity * math.pow( dot_product / divisor, specular )

        return intensity

class Scene:
    background = Vector( 255, 255, 255 )
    objects = [
        Sphere( Vector( 0, -1, 3 ), 1, Vector( 255, 0, 0 ), 500 ),
        Sphere( Vector( 2, 0, 4 ), 1, Vector( 0, 0, 255 ), 500 ),
        Sphere( Vector( -2, 0, 4 ), 1, Vector( 0, 255, 0 ), 10 ),
        Sphere( Vector( 0, -5001, 0 ), 5000, Vector( 255, 255, 0 ), 1000 ),
    ]
    lights = [
        Light.Ambient( 0.2 ),
        Light.Point( 0.6, Vector( 2, 1, 0 ) ),
        Light.Directional( 0.2, Vector( 1, 4, 4 ) ),
    ]

    def normalize_lights():
        total_intensity = sum( light.intensity for light in Scene.lights )
        for light in Scene.lights:
            light.intensity /= total_intensity

Scene.normalize_lights()

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

def ray_trace( origin, point ):
    direction = ( point - origin ).normalize()
    object, distance = find_intersection( origin, direction, viewport_distance, viewport_max )
    if not object: return Scene.background
    intersection = origin + distance * direction
    normal = object.calc_normal( intersection )
    specular = object.specular
    light = sum( light.calc_intensity( intersection, normal, -direction, specular ) for light in Scene.lights )
    color = object.color * light
    color.x = min( color.x, 255 )
    color.y = min( color.y, 255 )
    color.z = min( color.z, 255 )
    return color

thread_count = 4
assert( canvas_width % thread_count == 0 )

def initialize():
    pygame.init()
    global display
    display = pygame.display.set_mode( ( canvas_width, canvas_height ) )
    pygame.display.set_caption( "py-render" )

    global surface_array
    surface_array = multiprocessing.Array( ctypes.c_uint8, canvas_width * canvas_height * 3, lock = False )

    global clock
    clock = pygame.time.Clock()

def initialize_thread( surface_array ):
    globals()[ "surface_array" ] = surface_array

def put_pixel( x, y, color ):
    offset = x * canvas_height + y
    offset *= 3
    surface_array[ offset + 0 ] = int( color.x )
    surface_array[ offset + 1 ] = int( color.y )
    surface_array[ offset + 2 ] = int( color.z )

def render( pool ):
    pool.map( render_thread, ( ( index, camera ) for index in range( thread_count ) ) )
    pygame.surfarray.blit_array( display, 
        np.frombuffer( surface_array, dtype = ctypes.c_uint8 ) 
          .reshape( canvas_width, canvas_height, 3, copy = False ) )

def render_thread( tuple ):
    ( index, camera ) = tuple
    globals()[ "camera" ] = camera
    for cx in range( canvas_width // thread_count ):
        cx += index * canvas_width // thread_count
        for cy in range( canvas_height ):
            origin = camera.position
            point = canvas_to_viewport( cx, cy )
            color = ray_trace( origin, point )
            put_pixel( cx, cy, color )

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            handle_inputs( event.key )

def handle_inputs( key ):
    match key:
        case pygame.K_ESCAPE:
            exit()
        case pygame.K_w:
            camera.translate_forward()
        case pygame.K_s:
            camera.translate_backward()
        case pygame.K_a:
            camera.translate_left()
        case pygame.K_d:
            camera.translate_right()
        case pygame.K_LSHIFT:
            camera.translate_up()
        case pygame.K_LCTRL:
            camera.translate_down()
        case pygame.K_UP:
            camera.rotate_up()
        case pygame.K_DOWN:
            camera.rotate_down()
        case pygame.K_LEFT:
            camera.rotate_left()
        case pygame.K_RIGHT:
            camera.rotate_right()
        case pygame.K_p:
            toggle_pause()

def toggle_pause():
    paused = not paused
    if paused: print( "paused!" )
    else: print( "resuming.." )

def exit():
    pygame.quit()
    raise SystemExit

if __name__ == "__main__":
    initialize()
    # The ( surface_array, ) syntax is something about arguments expansion or something
    with multiprocessing.Pool( thread_count, initialize_thread, ( surface_array, ) ) as pool:
        paused = False
        while True:
            handle_events()
            if not paused:
                render( pool )
                print( "tick" )
                print( camera.position )
                print( clock.get_rawtime() )
            pygame.display.update()
            clock.tick( 60 )
