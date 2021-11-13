#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import io
import math
import urllib.request
import pygame
import time
import traceback
import utils


def init_display(size=(None, None), pos=(None, None), hideMouse=True, clearScreen=False,
                 icon=None, caption=None, framed=True, resizable=False, aot=False):
    " Initializes a new pygame screen using the framebuffer "
    # Based on "Python GUI in Linux frame buffer"
    # http://www.karoltomala.com/blog/?p=679

    pygame.init()

    archOS = platform.platform()
    print("System Architecture Family:", archOS)
    interpreter = str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])
    print("Python interpreter version: %s" % interpreter)
    disp_no = os.getenv("DISPLAY")
    if disp_no:
        print("X Display = {0}".format(disp_no), " - ", end="")
    else:
        print("Display driver: ", end="")

    # Check which frame buffer drivers are available
    if "Linux" in archOS:
        if "arm" in archOS:
            # Raspberry Pi. Start with fbcon since directfb hangs with composite output
            # I added 'x11' because new Raspbian Stretch seems to use it instead of fbcon
            drivers = ['x11', 'fbcon', 'directfb', 'svgalib']
        else:
            drivers = ['x11', 'dga', 'fbcon', 'directfb', 'ggi', 'vgl', 'svgalib', 'aalib']
    elif "Darwin" in archOS:
        drivers = ['foo']  # No driver required (WARNING: not tested on an actual Darwin system)
    elif "Windows" in archOS:
        drivers = ['windib', 'directx']
    else:
        drivers = ['foo', 'x11', 'dga', 'fbcon', 'directfb', 'ggi', 'vgl', 'svgalib', 'aalib', 'windib', 'directx']
    found = False
    for driver in drivers:
        if driver != 'foo':
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print('Driver: {0} failed.'.format(driver))
            continue
        found = True
        print(driver)
        break

    if not found:
        raise Exception('No suitable video driver found!')

    screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    windowed = True
    if size is None or (type(size) == tuple and
                        (size[0] is None or size[1] is None or
                         size[0] >= screen_size[0] or size[1] >= screen_size[1])):
        windowed = False
        size = screen_size
    print("Monitor Resolution: %dx%d" % screen_size, "/", "Window Size: %dx%d" % size)

    if icon is not None:
        try:
            iconW = pygame.image.load(utils.resource_path(icon))
            pygame.display.set_icon(iconW)
        except:
            print("Main icon not found!")
            print(traceback.format_exc())

    if caption is not None:
        pygame.display.set_caption(caption, caption[:8] + caption[-7:])

    if windowed:
        params = 0
        if not framed:
            params = pygame.NOFRAME
        if resizable:
            params += pygame.RESIZABLE

        xpos = int((screen_size[0] - size[0]) / 2)
        ypos = 50
        if pos is not None and type(pos) == tuple:
            if pos[0] is not None:
                xpos = pos[0]
            if pos[1] is not None and pos[1] != 0:
                ypos = pos[1]
        pos = (xpos, ypos)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % pos
        screen = pygame.display.set_mode(size, params)
        x, y, w, h = utils.get_screen_pos(caption)
        border_width = abs(pos[0] - x)
        titlebar_height = abs(pos[1] - y)
        hideMouse = False
        fullscreen = False
    else:
        size = screen_size
        pos = (0, 0)
        border_width = 0
        titlebar_height = 0
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        fullscreen = True

    if aot:
        if "Windows" in archOS:
            win_on_top(aot)
        else:
            print("WARNING: Always-on-Top not allowed on non-Win OSs. Use HomeKey+RightMouse to set window properties")

    if hideMouse:
        pygame.mouse.set_visible(False)

    if clearScreen:
        screen.fill((0, 0, 0))
        pygame.display.update()

    return screen, size[0], size[1], fullscreen, \
           pos[0], pos[1], border_width, titlebar_height, \
           str(sys.version_info[0]) + "." + str(sys.version_info[1]), archOS


def win_on_top(aot=False):
    # https://stackoverflow.com/questions/25381589/pygame-set-window-on-top-without-changing-its-position/49482325 (kmaork)

    from ctypes import windll
    SetWindowPos = windll.user32.SetWindowPos

    NOSIZE = 1
    NOMOVE = 2
    TOPMOST = -1
    NOT_TOPMOST = -2

    zorder = (NOT_TOPMOST, TOPMOST)[aot]  # choose a flag according to bool
    hwnd = pygame.display.get_wm_info()['window']  # handle to the window
    SetWindowPos(hwnd, zorder, 0, 0, 0, 0, NOMOVE | NOSIZE)

    return


def pg_get_screen_pos(name):
    # Position doesn't takes into account border width and title bar height

    if pygame.version.vernum >= (2, 0):
        from pygame._sdl2.video import Window

        window = Window.from_display_module()
        x, y = window.position
        w, h = window.size

    else:
        x, y, w, h = utils.get_screen_pos(name)

    return x, y, w, h


def play_music(song, loops=0):
    # Initialize music player (if not yet initialized)
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    # Stop previous playback before playing anything else
    pygame.mixer.music.stop()
    playing = False
    # Use song=None to stop previous playback and not continue playing anything
    if song is not None:
        # Load song
        pygame.mixer.music.load(song)
        # Play music (loops represents value+1 times to be played. Set to -1 for infinite loop)
        pygame.mixer.music.play(loops=loops)
        playing = True
    else:
        pygame.mixer.quit()

    return playing


def load_font(folder, font, fsize, fbold=0):
    # Initialise font support if needed
    if not pygame.font.get_init(): pygame.font.init()

    if folder: folder = utils.resource_path(folder)

    try:
        # Load custom font
        fontObj = pygame.font.Font(folder + font, fsize)
    except:
        # Load system font (if available, or default instead)
        sys_font = font.split(".")[0]
        fontObj = pygame.font.SysFont(sys_font, fsize, fbold)

        if pygame.font.match_font(sys_font) is None:
            # Warn and list available fonts
            print("Font " + folder + font + " not available! Falling back to default font: " + pygame.font.get_default_font())
            print("Other available Fonts: ", pygame.font.get_fonts())

    return fontObj


def load_icon(code, folder, extension=".png"):
    icon = None

    try:
        # Use .convert_alpha() if you find troubles with transparency
        icon = pygame.image.load(utils.resource_path(folder) + str(code) + extension)
    except:
        print("Error loading icon. Loading default icon instead. Code:", folder + code)
        print(traceback.format_exc())

    return icon


def load_url_image(url, headers='', timeout=10):
    image = None

    try:
        with urllib.request.urlopen(url, timeout=timeout) as pic:
            image_str = pic.read()
            image_file = io.BytesIO(image_str)
            # Use .convert_alpha() if you find troubles with transparency
            image = pygame.image.load(image_file)
    except:
        print("Error getting image from URL", url)
        print(traceback.format_exc())

    return image


def draw_text(screen, text, font, fcolor=pygame.Color("white"), blit=False, x=0, y=0, outline=None, owidth=0,
              ocolor=(64, 64, 64), oalpha=64):

    rtext = font.render(text, True, fcolor)
    rtx, rty = rtext.get_size()

    if blit:

        if outline == "Outline":
            otext = font.render(text, True, ocolor)
            otext.set_alpha(oalpha)  # Worked once, but now it doesn't... don't know why
            if owidth == 0: owidth = int(max(2, rtx / max(len(text), 1) * 0.03, 1))
            screen.blit(otext, (x - owidth, y - owidth))
            screen.blit(otext, (x - owidth, y + owidth))
            screen.blit(otext, (x + owidth, y - owidth))
            screen.blit(otext, (x + owidth, y + owidth))
            # These next four blits are not strictly necessary, though look better (comment to improve CPU usage)
            screen.blit(otext, (x - owidth, y))
            screen.blit(otext, (x + owidth, y))
            screen.blit(otext, (x, y - owidth))
            screen.blit(otext, (x, y + owidth))

        elif outline == "Outrect":
            dim(screen, oalpha, ocolor, (x - owidth, y - owidth, rtx + owidth * 2, rty + owidth))

        elif outline == "Shadow":
            otext = font.render(text, True, ocolor)
            otext.set_alpha(oalpha)  # Worked once, but now it doesn't... don't know why
            screen.blit(otext, (x + owidth, y + owidth))

        elif outline == "FadeIn":
            rect = (x, y, rtx, rty)
            srf = pygame.Surface((rect[2], rect[3]))
            srf.fill(ocolor)
            srf.blit(rtext, (0, 0))
            img = screenshot(srf, (0, 0, rect[2], rect[3]))
            fade_in(screen, img, rect, color_filter=(ocolor))

        elif outline == "FadeOut":
            rect = (x, y, rtx, rty)
            srf = pygame.Surface((rect[2], rect[3]))
            srf.fill(ocolor)
            srf.blit(rtext, (0, 0))
            img = screenshot(srf, (0, 0, rect[2], rect[3]))
            fade_out(screen, img, rect, color_filter=(ocolor))

        if outline != "FadeOut":
            screen.blit(rtext, (x, y))

    rtx += owidth * 2
    rty += owidth

    return rtx, rty


def fade_in(screen, img, rect, period=1.2, color_filter=(0, 0, 0)):
    clock = pygame.time.Clock()
    darken_factor = 255
    darken_step = 25.5
    fadeFps = int((255 / darken_step) / period)

    while darken_factor > 0:
        clock.tick(fadeFps)
        screen.blit(img, (rect[0], rect[1]))
        dim(screen, darken_factor, color_filter, rect, True)
        darken_factor = int(darken_factor - (darken_step / period))
        default_event_loop()

    screen.blit(img, (rect[0], rect[1]))
    pygame.display.update(rect)

    return


def fade_out(screen, img, rect, period=1, color_filter=(0, 0, 0)):
    clock = pygame.time.Clock()
    darken_factor = 0
    darken_step = 25.5
    fadeFps = int((255 / darken_step) / period)

    while darken_factor < 255:
        clock.tick(fadeFps)
        screen.blit(img, (rect[0], rect[1]))
        dim(screen, darken_factor, color_filter, rect, True)
        darken_factor = int(darken_factor + (darken_step / period))
        default_event_loop()

    pygame.draw.rect(screen, color_filter, rect)
    pygame.display.update(rect)

    return


"""
        # FadeIn/FadeOut EXAMPLE
        # MUST use a different Surface to blit the text/image first, then fade it on main Surface
        srf = pygame.Surface( (rect[2], rect[3]) )
        pygame.draw.rect( srf, nBkg, (0,0,rect[2],rect[3]) )
        font = pygame.font.SysFont( self.fn, size, bold)
        rtext = font.render( "Texto de prueba para FadeIn / FadeOut", True, white )
        srf.blit( rtext, (0,0) )
        img = Screenshot( srf, (0, 0, rect[2], rect[3])
        while True:
            FadeIn( self.screen, img, rect, 2, nBkg )
            sleep(5)
            FadeOut( self.screen, img, rect, 2, nBkg )
"""


####################################################################
# Based on the work from Gunny26
# < https://github.com/gunny26/pygame/blob/master/ScrollText.py >
# Thanks, man for your work and, specially, for sharing!!!
class ScrollText(object):
    """Simple 2d Scrolling Text"""

    def __init__(self, surface, text, hpos, color, fontObj, size):
        self.surface = surface
        appendix = " " * int(self.surface.get_width() / size * 2)
        self.text = appendix + text
        self.text_surface = ''
        self.hpos = hpos
        self.position = 0
        self.font = fontObj

        i = 1
        while self.text_surface == '':
            try:
                self.text_surface = self.font.render(self.text, True, color)
            except:
                print(i, len(text), "News text too large to render... shortening")
                self.text = appendix + text[:-(int(len(text) * 0.1 * i))]
                i += 1
        (self.tx, self.ty) = self.text_surface.get_size()

    def __del__(self):
        """ Destructor to make sure resources are released """

    def update(self, surface=None):
        # update every frame
        if surface is not None:
            self.surface = surface
        self.surface.blit(self.text_surface,
                          (0, self.hpos),
                          (self.position, 0, self.tx, self.ty)
                          )
        if self.position < self.tx:
            # Save CPU setting this variable. Lower values will consume more. Higher ones may produce text flickering
            self.position += 3
        else:
            self.position = 0


def draw_analog_clock(screen, hour, minute, x, y, radius, edgeSize, handsSize, edgeColor, handsColor, bkgColor=None):

    # Draw clock background, edge and hands center
    if bkgColor is not None:
        pygame.draw.circle(screen, bkgColor, (x, y), radius - edgeSize + 1, 0)
    pygame.draw.circle(screen, edgeColor, (x, y), radius, edgeSize)
    pygame.draw.circle(screen, handsColor, (x, y), edgeSize, 0)

    # Calculate hands angles
    mangle = int(minute) * (360 / 60)
    hangle = int(hour) * (360 / 12) + mangle / 60

    # Draw hours
    endx = x + radius / 2 * math.sin(math.radians(hangle))
    endy = y + radius / 2 * (-1) * math.cos(math.radians(hangle))
    pygame.draw.line(screen, handsColor, (x, y), (endx, endy), handsSize)

    # Draw minutes
    endx = x + radius * 0.8 * math.sin(math.radians(mangle))
    endy = y + radius * 0.8 * (-1) * math.cos(math.radians(mangle))
    pygame.draw.line(screen, handsColor, (x, y), (endx, endy), handsSize)

    return


def brightness(screen, image):
    # Way too slow...

    value = []
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = screen.get_at((x, y))
            color = (color[0] + color[1] + color[2]) / 3
            value.append(color)

    return sum(value) / len(value)


def dim(screen, darken_factor=64, color_filter=(0, 0, 0), rect=None, updateD=False):
    if rect is not None:
        (x, y, w, h) = rect
        w = int(w)
        h = int(h)
        darken = pygame.Surface((w, h))
    else:
        x, y = 0, 0
        darken = pygame.Surface(screen.get_size())
    darken.fill(color_filter)
    darken.set_alpha(darken_factor)
    screen.blit(darken, (x, y))
    if updateD:
        if rect is not None:
            pygame.display.update(rect)
        else:
            pygame.display.update()

    return


def screenshot(screen, rect):
    img = pygame.Surface((rect[2], rect[3]))
    img.blit(screen, (0, 0), rect)

    return img


def prepare_area(screen, img, rect):
    if not img:
        # Capture "area" background (if not already captured and showBkg)
        img = screenshot(screen, rect)
    else:
        # ... or blit "area" to erase previous values
        screen.blit(img, rect)

    return img


def default_event_loop():

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            # On windowed mode, exit when clicking the "x" (close window)
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYUP:
            key = event.key
            mods = pygame.key.get_mods()

            if key in (pygame.K_q, pygame.K_ESCAPE) or (mods and pygame.KMOD_CTRL and event.key == pygame.K_c):
                # On 'q' or Escape or Ctl-C pressed, quit the program.
                pygame.quit()
                sys.exit()

    return


def get_input_box_value(screen, rect, back_color=pygame.Color('black'), line_color=pygame.Color('white'),
                        line_thickness=2,
                        font="freesans", font_size=32, text='', text_color=pygame.Color('white'),
                        init_text='Enter text',
                        init_text_color=pygame.Color('gray55')):
    end_value, event_box, in_box = input_box(screen=screen, rect=rect, back_color=back_color, line_color=line_color,
                                             line_thickness=line_thickness, font=font, font_size=font_size, text=text,
                                             text_color=text_color, init_text=init_text,
                                             init_text_color=init_text_color,
                                             draw=True, capture=False)
    done = False
    draw = False
    capture = True

    final_event = event_box

    while not done:

        if event_box.get("Type") == pygame.KEYDOWN:
            if event_box.get("Key") == pygame.K_RETURN:
                break
            elif event_box.get("Key") == pygame.K_TAB:
                break
            elif event_box.get("Key") == pygame.K_ESCAPE:
                end_value = str(text)
                draw = True
                capture = False
                done = True
        elif event_box.get("Type") == pygame.MOUSEBUTTONDOWN:
            if not in_box.collidepoint(event_box.get("Pos")):
                draw = True
                capture = False
                done = True

        end_value, event_box, in_box = input_box(screen=screen, rect=rect, back_color=back_color,
                                                 line_color=line_color,
                                                 line_thickness=line_thickness, font=font, font_size=font_size,
                                                 text=str(end_value),
                                                 text_color=text_color, init_text="", init_text_color=init_text_color,
                                                 draw=draw, capture=capture)
        if capture:
            final_event = event_box

        if done and (not end_value or end_value.isspace()):
            end_value = str(init_text)

    return str(end_value), final_event, in_box


def input_box(screen, rect, back_color=pygame.Color('black'), line_color=pygame.Color('white'), line_thickness=2,
              font="freesans", font_size=32, text='', text_color=pygame.Color('white'), init_text='Enter text',
              init_text_color=pygame.Color('gray55'), draw=True, capture=True):
    # Use draw=True to set several InputBox at a time, or re-enter (draw=False); and use capture to focus on one of them
    # Use Enter/TAB to move from one InputBox to another (control must be outside this function, on your program)

    # Enable key held detection (disabled by default in pygame)
    pygame.key.set_repeat(300, 50)

    # Prepare values, font and box (to detect mouse collision)
    firstRun = True
    done = False
    cursor = "|"
    folder = ""
    font_parts = font.split("/")
    for i, part in enumerate(font_parts):
        if i == len(font_parts) - 1:
            font = part
        else:
            folder += part
    fontObj = load_font(folder=folder, font=font, fsize=font_size)
    box = pygame.Rect(rect)
    ekey = 0
    etype = 0
    epos = (0, 0)

    # Enter "read-character/draw-text" loop
    while not done:
        if capture:
            for event in pygame.event.get():
                etype = event.type
                if etype == pygame.QUIT:
                    # On windowed mode, exit when clicking the "x" (close window)
                    pygame.quit()
                    exit()
                elif etype == pygame.MOUSEBUTTONDOWN:
                    epos = event.pos
                    if not box.collidepoint(epos):
                        # Exit InputBox if mouse is pressed outside the rect, or else stay
                        done = True
                elif etype == pygame.KEYDOWN:
                    ekey = event.key
                    if ekey == pygame.K_RETURN or ekey == pygame.K_ESCAPE or ekey == pygame.K_TAB:
                        # Exit InputBox if Enter (Finish), Escape (Cancel) or Tab (Next) are pressed
                        done = True
                    elif ekey == pygame.K_BACKSPACE:
                        # Erase last character when Backspace is pressed
                        text = text[:-1]
                    else:
                        # Add entered character to text
                        text = text + event.unicode
                    draw = True
        else:
            done = True

        if firstRun or draw or done:
            # Select text to draw: initial (passed), intermediate (with "cursor") or final (no "cursor")
            if text is None or text == '':
                if init_text is None: init_text = ''
                box_text = init_text
                color = init_text_color
            else:
                if text is None: text = ''
                box_text = text
                color = text_color

            if not done:
                box_text = box_text + cursor

            # Draw rect
            pygame.draw.rect(screen, back_color, rect)
            if line_thickness > 0:
                pygame.draw.rect(screen, line_color, rect, line_thickness)

            # Draw selected text
            rtext = fontObj.render(box_text, True, color)
            tx, ty = rtext.get_size()
            screen.blit(rtext, (rect[0] + line_thickness + font_size * 0.3, rect[1] + (rect[3] - ty) / 2))

            # Update display
            pygame.display.update(rect)

            if firstRun:
                firstRun = False
                init_text = ''
            draw = False

        # Save CPU
        time.sleep(0.01)

    return text, {'Type': etype, 'Key': ekey, 'Pos': epos}, box


"""
# EXAMPLE of two InputBox with "re-enter" function

while not done

    if first_run:
        input_value1, event_box, input_box = disputil.get_input_box_value(self.screen, rect1, 
                                                                    init_text=str(value1), draw=True, capture=False)
        box1 = pygame.Rect(rect1)

        input_value1, event_box, input_box = disputil.get_input_box_value(self.screen, rect2, 
                                                                    init_text=str(value2), draw=True, capture=False)
        box2 = pygame.Rect(rect2)

        button = pygame.Rect(button_rect)

    else:
        if changed1:
            input_value1, event_box, input_box = disputil.get_input_box_value(self.screen, rect1, 
                                                                    init_text=str(value[i]), draw=False, capture=True)
        elif changed2:
            input_value2, event_box, input_box = disputil.get_input_box_value(self.screen, (ix, iy, 300, 50), 
                                                                    init_text=str(value[i]), draw=False, capture=True)

        if event_box is not None and event_box.get("Type") == pygame.MOUSEBUTTONDOWN:
            event = event_box
            event_box = None
        else:
            event = event_loop()

        if event.get("Type") == pygame.MOUSEBUTTONDOWN:
            if box1.collidepoint(event.get("Pos")):
                changed1 = True
            elif box2.collidepoint(event.get("Pos")):
                changed2 = True
            elif button.collidepoint(event.get("Pos")):
                done = True
        elif event.get("Type") == pygame.KEYDOWN:
            if event.get("Key") == pygame.K_RETURN:
                done = True

    time.sleep(0.05)
"""
