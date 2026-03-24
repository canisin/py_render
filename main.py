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

    def __div__( vector, scalar):
        return Vector( vector.x / scalar, vector.y / scalar, vector.z / scalar )

    def __rdiv__( vector, scalar ):
        return Vector( vector.x / scalar, vector.y / scalar, vector.z / scalar )

    def __idiv__( self, scalar ):
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

    def intersect( self, origin, direction ):
        position = self.position - origin

        a = direction.len_sq()
        b = Vector.dot( position, direction )
        c = position.len_sq() - self.radius * self.radius

        d = b * b - a * c
        if d < 0: return math.inf

        t2 = ( b - math.sqrt( d ) ) / a
        return t2 if t2 > 0 else math.inf

canvas_width = 480
canvas_height = 480
camera_pos = Vector( 0, 0, 0 )
camera_dir = Vector( 0, 0, 1 )
camera_up = Vector( 0, 1, 0 )
viewport_distance = 1
viewport_width = 1
viewport_height = 1
viewport_max = 1000
background = ( 255, 255, 255 )

def canvas_to_viewport( cx, cy ):
    vx = viewport_width * ( cx - canvas_width / 2 ) / canvas_width
    vy = viewport_height * ( canvas_height / 2 - cy ) / canvas_height

    viewport_right = Vector.cross( camera_dir, camera_up )
    viewport_up = Vector.cross( viewport_right, camera_dir )
    return camera_pos + viewport_distance * camera_dir + vx * viewport_right + vy * viewport_up

scene = [
    Sphere( Vector( 0, -1, 3 ), 1, ( 255, 0, 0 ) ),
    Sphere( Vector( 2, 0, 4 ), 1, ( 0, 0, 255 ) ),
    Sphere( Vector( -2, 0, 4 ), 1, ( 0, 255, 0 ) ),
]

def find_intersection( origin, direction, t_min, t_max ):
    closest_t = math.inf
    closest_object = None

    for object in scene:
        t = object.intersect( origin, direction )

        if t < t_min: continue
        if t > t_max: continue

        if t < closest_t:
            closest_t = t
            closest_object = object

    return closest_object

def ray_trace( cx, cy ):
    p = canvas_to_viewport( cx, cy )
    d = p - camera_pos
    object = find_intersection( camera_pos, d, viewport_distance, viewport_max )
    return object.color if object else background

pygame.init()
display = pygame.display.set_mode( ( canvas_width, canvas_height ) )
pygame.display.set_caption( "py-render" )

clock = pygame.time.Clock()

def put_pixel( x, y, color ):
    display.set_at( ( x, y ), color )

def render():
    for cx in range( canvas_width ):
        for cy in range( canvas_height ):
            put_pixel( cx, cy, ray_trace( cx, cy ) )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    render()
    pygame.display.update()
    clock.tick( 60 )
    print( "tick" )
    camera_pos -= camera_dir
    print( camera_pos )
