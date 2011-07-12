"""

groups:
  subs
  torpedoes
  borders

  # find all sprites in the 'torpedo' group that collide with a submarine
  for torpedo in sprite.spritecollide(player, torpedoes, dokill=1):
      boom_sound.play()
      Explosion(torpedo, 0)

  >>> for alien in sprite.groupcollide(aliens, shots, 1, 1).keys()
  ...     boom_sound.play()
  ...     Explosion(alien, 0)
  ...     kills += 1



"""

import os
import sys

import pygame
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

from pygame.locals import *

from pygame.sprite import Sprite, OrderedUpdates

from multiprocessing import Process, Queue
from Queue import Empty, Full
from optparse import OptionParser

class OrderedSpriteList(OrderedUpdates):
    def __init__(self, *sprites):
        OrderedUpdates.__init__(self, *sprites)

    def __getitem__(self, slotno):
        return self._spritelist[slotno]

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound

class SubmarineSprite(Sprite):
    """  """

    HEADING_EAST, HEADING_WEST = range(2)

    _heading = HEADING_EAST

    def __init__(self, path_to_graphics):
        Sprite.__init__(self)
        self.theme = path_to_graphics

        # determine the appearance of the sprite
        image = pygame.image.load(os.path.join(self.theme, "submarine.png")).convert()
        colorkey = image.get_at( (0, 0) )
        image.set_colorkey(colorkey, pygame.RLEACCEL)
        self.image = image
        self.rect = self.image.get_rect()

        #self.state = ???

        #self.add(*groups) to groups

    @apply
    def heading():

        def fget(self):
            return self._heading

        def fset(self, direction):

            #if self._heading is self.HEADING_EAST and direction is self.HEADING_WEST:
            #    self.image = pygame.transform.flip(self.image, 1, 0)

            #if self._heading is self.HEADING_WEST and direction is self.HEADING_EAST:
            #    self.image = pygame.transform.flip(self.image, 1, 0)

            self._heading = direction

        return property(**locals())

    @apply
    def position():

        def fget(self):
            return self.rect.center

        def fset(self, (xpos, ypos)):
            self.rect.center = xpos, ypos

        return property(**locals())

    def update(self, *args):
        """Update the represention of the submarine based on its current state.

           The only two items to be changed are its:
             1) self.image
             2) self.rect
        """
        #if state is ???:
        #    self.do_this()
        #elif state is ???:
        #    self.do_that()

class Viewer(Process):
    """
    """

    def put(self, action, **kwargs):
        msg = Message(action, **kwargs)
        self.to_viewer.put(msg)

    def __init__(self, name, path_to_graphics, fullscreen=False):
        """  """
        Process.__init__(self, name=name)
        self.to_viewer = Queue(128)

        self.theme = path_to_graphics

        self.pygame_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if fullscreen:
            self.pygame_flags |= pygame.FULLSCREEN | pygame.NOFRAME

        self.submarines = OrderedSpriteList()

    def setup_background(self):
        pygame.display.set_caption('Submarine Challenge')

        # Set size of the screen from the dimensions of the background graphic
        self.background = pygame.image.load(os.path.join(self.theme, "background.png"))
        self.screen_size = (self.field_width, self.field_height) = self.background.get_rect().size

        # Open the screen to that size and use flags to control the type of screen,
        self.screen = pygame.display.set_mode(self.screen_size, self.pygame_flags)

        # convert the background image to that format,
        self.background = self.background.convert()

        # and then paint the background onto the screen.
        self.screen.blit(self.background, (0, 0))

    def handle_add_submarine(self, leftmost):
        """  """
        print "Adding submarine sprite"

        sub = SubmarineSprite(self.theme)

        if leftmost:
            sub.heading = sub.HEADING_EAST
            sub.position = 0, sub.rect.height
        else:
            sub.heading = sub.HEADING_WEST
            sub.position = self.field_width - 10, sub.rect.height

        self.submarines.add(sub)
        return sub

    def handle_place_submarine(self, leftmost, xpos, ypos):
        sub = self.submarines[leftmost==0]
        sub.position = xpos * self.field_width, ypos * self.field_height
        print "Moving submarine %d to %r" % (leftmost==0, sub.position)

    def run(self):
        """  """

        pygame.init()
        self.setup_background()
        pygame.display.flip()

        self.alive = True
        while self.alive:

            while 1:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()

                try:
                    msg = self.to_viewer.get(True, 1) # blocks for a msg
                except Empty:
                    continue

                if hasattr(self, 'handle_' + msg.action):
                    getattr(self, 'handle_' + msg.action)(**msg)

                if msg.action == 'end_game':
                    self.alive = False
                    continue

                #self.ballrect = self.ballrect.move(speed)
                #if self.ballrect.left < 0 or self.ballrect.right > self.width:
                #    speed[0] = -speed[0]
                #if self.ballrect.top < 0 or self.ballrect.bottom > self.height:
                #    speed[1] = -speed[1]
                #
                #self.screen.fill(black)
                #self.screen.blit(self.ball, self.ballrect)

                self.submarines.clear(self.screen, self.background)
                self.submarines.update()
                self.submarines.draw(self.screen)
                pygame.display.flip()

class Message(dict):
    """  """
    def __init__(self, action, **kwargs):
        self.action = action
        self.update(kwargs)

class Submarine:
    """  """

    xpos = ypos = 0

    def __init__(self, commander):
        self.commander = commander

    def leave_port(self, leftmost):
        self.heading = leftmost

        self.xpos = self.abs_to_rel_X(0)
        self.ypos = 0

        self.fuel = 100

        self.commander.leaving_port()

    def abs_to_rel_X(self, xpos):
        return float(self.heading) - xpos

    def rel_to_abs_X(self, xpos):
        return float(self.heading) - xpos

class Player(Process):
    """
    """

    def put(self, action, **kwargs):
        msg = Message(action, **kwargs)
        self.to_player.put(msg)

    def __init__(self, referee, commander, vessel=Submarine):
        Process.__init__(self, name=commander.name)

        self.to_player = Queue(8)
        self.referee = referee
        self.vessel = vessel(commander)

    def run(self):
        self.alive = True
        while self.alive:
            msg = self.to_player.get() # blocks for a msg
            if hasattr(self, 'handle_' + msg.action):
                getattr(self, 'handle_' + msg.action)(**msg)

            if msg.action == 'end_game':
                self.alive = False

    def handle_begin_game(self, leftmost):
        print "Game Beginning for Player %s" % self.name
        self.referee.put('ready')
        self.vessel.leave_port(leftmost)

    def handle_end_game(self):
        print "Player %s is told to quit" % self.name

    def handle_ping(self):
        print "Player %s is bring pinged" % self.name
        self.referee.put([42, None, 'hello from %s' % self.name])

    def handle_tick(self):
        print "*tick*"

class Referee(object):
    """
    """
    viewer = None
    oldtime = 0

    def put(self, action, **kwargs):
        msg = Message(action, **kwargs)
        self.to_ref.put(msg)

    def __init__(self, opts):
        self.to_ref = Queue(64)
        self.players = []
        self.opts = opts

    def add_viewer(self, viewer):
        self.viewer = viewer

    def add_player(self, player):
        self.players.append(player)

    def run_game(self):
        for slot, player in enumerate(self.players):
            if self.viewer:
                self.viewer.put('add_submarine', leftmost=(slot==0))
            player.put('begin_game', leftmost=(slot==0))

        ncmds = 0
        while True:

            for slot, player in enumerate(self.players):
                player.vessel.xpos += 1.0/30
                player.vessel.ypos += 1.0/50

            try:
                msg = self.to_ref.get(timeout=0.5)
                print msg

                ncmds += 1
                if ncmds > 20:
                    break
            except Empty:
                for slot, player in enumerate(self.players):
                    if self.viewer:
                        self.viewer.put('place_submarine', leftmost=(slot==0),
                                        xpos=player.vessel.xpos, ypos=player.vessel.ypos)
                    player.put('tick')

        [p.put('end_game') for p in self.players]

    def end_game(self):
        for player in self.players:
            player.put('end_game')
            player.close()

    def advance_simulation(self, newtime):
        """  """
        deltatime = newtime - oldtime

def main():
    usage = "usage: %prog <player1.py> <player2.py> [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-n", "--dry-run",
                      action="store_true", dest="dry_run", default=False,
                      help="skip any changes to files, just report on results")

    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    options, args = parser.parse_args()

    ref = Referee(options)

    viewer = Viewer('viewer', 'graphics')
    viewer.start()
    ref.add_viewer(viewer)

    # PlayerA = __import__(...)  set up player A from egg
    pmod = __import__('player1')
    ref.add_player(Player(ref, pmod.Commander()))

    # PlayerB = __import__(...)  set up player B from egg
    pmod = __import__('player2')
    ref.add_player(Player(ref, pmod.Commander()))

    [player.start() for player in ref.players]
    ref.run_game()
    [player.join(5) for player in ref.players]

if __name__ == "__main__":
    main()
