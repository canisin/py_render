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

class Sphere:
    def __init__( self, position, radius, color ):
        self.position = position
        self.radius = radius
        self.color = color

    # TODO: Can we assume that direction is a unit vector?
    # TODO: Can we return only the t with the smaller value, i.e. t2?
    def intersect( self, origin, direction ):
        position_to_origin = Vector.sub( origin, self.position )

        a = Vector.dot( direction, direction )
        b = 2 * Vector.dot( position_to_origin, direction )
        c = Vector.dot( position_to_origin, position_to_origin ) - self.radius * self.radius

        d = b * b - 4 * a * c
        if d < 0: return ( math.inf, math.inf )

        t1 = ( -b + math.sqrt( d ) ) / ( 2 * a )
        t2 = ( -b - math.sqrt( d ) ) / ( 2 * a )
        return ( t1, t2 )

canvas_width = 480
canvas_height = 480
camera_pos = Vector( 0, 0, 0 )
camera_dir = Vector( 0, 0, 1 )
viewport_distance = 1
viewport_width = 1
viewport_height = 1
viewport_max = 1000

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

for cx in range( canvas_width ):
    for cy in range( canvas_height ):
        p = canvas_to_viewport( cx, cy )

        closest_t = math.inf
        closest_object = None
        for object in scene:
            t1, t2 = object.intersect( camera_pos, Vector.sub( p, camera_pos ) )
            if t1 >= viewport_distance and t1 < viewport_max and t1 < closest_t:
                closest_t = t1
                closest_object = object
            if t2 >= viewport_distance and t2 < viewport_max and t2 < closest_t:
                closest_t = t2
                closest_object = object
        if closest_object:
            put_pixel( cx, cy, closest_object.color )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    pygame.display.update()
    clock.tick( 60 )
