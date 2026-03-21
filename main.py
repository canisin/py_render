import pygame

pygame.init()
display = pygame.display.set_mode( (480, 480) )
display.fill( ( 255, 255, 255 ) )
pygame.display.set_caption( "py-render" )

clock = pygame.time.Clock()

def put_pixel( x, y, color ):
    display.set_at( ( x, y ), color )

for x in range( 20 ):
    put_pixel( 20 + x, 20, ( 255, 0, 0 ) )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    pygame.display.update()
    clock.tick( 60 )
