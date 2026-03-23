import pygame
import math

class Vector:
    def __init__( self, x, y, z ):
        self.x = x
        self.y = y
        self.z = z

    def add( lhs, rhs ):
        return Vector( lhs.x + rhs.x, lhs.y + rhs.y, lhs.z + rhs.z )

    def sub( lhs, rhs ):
        return Vector( lhs.x - rhs.x, lhs.y - rhs.y, lhs.z - rhs.z )

    def mult( vector, scalar ):
        return Vector( vector.x * scalar, vector.y * scalar, vector.z * scalar )

    def dot( lhs, rhs ):
        return lhs.x * rhs.x + lhs.y * rhs.y + lhs.z * rhs.z

    def len_sq( self ):
        return Vector.dot( self, self )

    def len( self ):
        return math.sqrt( self.len_sq() )

class Sphere:
    def __init__( self, position, radius, color ):
        self.position = position
        self.radius = radius
        self.color = color

    def intersect( self, origin, direction ):
        position = Vector.sub( self.position, origin )

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
viewport_distance = 1
viewport_width = 1
viewport_height = 1
viewport_max = 1000

# TODO: This only works if the camera is at the origin looking down the z axis
def canvas_to_viewport( cx, cy ):
    return Vector (
        ( cx - canvas_width / 2 ) * viewport_width / canvas_width, 
        -( cy - canvas_height / 2 ) * viewport_height / canvas_height, 
        viewport_distance )

pygame.init()
display = pygame.display.set_mode( ( canvas_width, canvas_height ) )
display.fill( ( 255, 255, 255 ) )
pygame.display.set_caption( "py-render" )

clock = pygame.time.Clock()

def put_pixel( x, y, color ):
    display.set_at( ( x, y ), color )

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

for cx in range( canvas_width ):
    for cy in range( canvas_height ):
        p = canvas_to_viewport( cx, cy )
        object = find_intersection( camera_pos, Vector.sub( p, camera_pos), viewport_distance, viewport_max )
        if object: put_pixel( cx, cy, object.color )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    pygame.display.update()
    clock.tick( 60 )
