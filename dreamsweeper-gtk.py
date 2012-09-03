# Copyright (C) 2012 by Vincent Povirk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys

import gtk
import pango

import dreamsweeper

border_color = gtk.gdk.color_parse('#555')

clear_color = gtk.gdk.color_parse('#FFF')
clear_num_color = gtk.gdk.color_parse('#000')

mine_color = gtk.gdk.color_parse('#000')
mine_num_color = gtk.gdk.color_parse('#FFF')

unknown_color = gtk.gdk.color_parse('#aaa')

def pango_layout_from_box(context, text, width, height):
    desc = pango.FontDescription('Sans')
    desc.set_size(1024 * 1024)

    layout = pango.Layout(context)
    layout.set_text(text)
    layout.set_width(-1)
    layout.set_font_description(desc)

    drawn_extents, logical_extents = layout.get_extents()
    _x, _y, layout_width, layout_height = logical_extents

    scale = min(float(width) * pango.SCALE / layout_width, float(height) * pango.SCALE / layout_height)

    desc.set_size(int(desc.get_size() * scale))

    layout.set_font_description(desc)

    return layout

class MainWindow(object):
    def __init__(self):
        self.window = gtk.Window()

        self.window.connect('delete-event', self.on_delete)

        self.board = dreamsweeper.SquareBoard()

        self.board.first_space_zero = True
        self.board.reveal_around_zeroes = True

        self.drawing_area = gtk.DrawingArea()

        self.drawing_area.connect('expose-event', self.on_area_expose)
        self.drawing_area.connect('motion-notify-event', self.on_area_motion)
        self.drawing_area.connect('button-press-event', self.on_button_press)
        self.drawing_area.connect('button-release-event', self.on_button_release)

        self.drawing_area.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)

        self.drawing_area.show()

        self.window.add(self.drawing_area)

        self.window.show()

        self.mouse_space = None
        self.held_mouse_button = None

    def on_delete(self, widget, event):
        gtk.main_quit()

    def on_area_expose(self, widget, event):
        drawable = widget.window
        allocation = widget.get_allocation()
        gc = drawable.new_gc()
        for space in self.board.spaces:
            polygon = self.board.get_polygon(space, allocation.width, allocation.height)

            polygon = tuple((int(x), int(y)) for (x, y) in polygon)

            box = tuple(int(x) for x in self.board.get_text_box(space, allocation.width, allocation.height))

            if space in self.board.known_spaces:
                value, adjacent = self.board.known_spaces[space]
                if value:
                    gc.set_rgb_fg_color(mine_color)
                else:
                    gc.set_rgb_fg_color(clear_color)
            elif space == self.mouse_space:
                gc.set_rgb_fg_color(clear_color)
            else:
                gc.set_rgb_fg_color(unknown_color)
            drawable.draw_polygon(gc, True, polygon)

            if space in self.board.flagged_spaces:
                value = self.board.flagged_spaces[space]

                if value:
                    gc.set_rgb_fg_color(mine_color)
                else:
                    gc.set_rgb_fg_color(clear_color)

                drawable.draw_rectangle(gc, True, box[0] + box[2]/4, box[1] + box[3]/4, box[2]/2, box[3]/2)

            adjacent = -1
            if space in self.board.known_spaces:
                value, adjacent = self.board.known_spaces[space]
                if value:
                    gc.set_rgb_fg_color(mine_num_color)
                else:
                    gc.set_rgb_fg_color(clear_num_color)

            if adjacent != -1:
                context = widget.get_pango_context()
                layout = pango_layout_from_box(context, str(adjacent), box[2], box[3])

                drawn_extents, logical_extents = layout.get_pixel_extents()
                layout_x, layout_y, layout_width, layout_height = logical_extents
                xofs = int((box[2] - layout_width) / 2)
                yofs = int((box[3] - layout_height) / 2)

                drawable.draw_layout(gc, box[0] + xofs, box[1] + yofs, layout)

            gc.set_rgb_fg_color(border_color)
            drawable.draw_polygon(gc, False, polygon)
        return True

    def on_button_press(self, widget, event):
        if self.held_mouse_button is not None:
            return

        allocation = widget.get_allocation()
        mouse_space = self.board.space_at_point(event.x, event.y, allocation.width, allocation.height)

        self.held_mouse_button = event.button

        if mouse_space != self.mouse_space:
            self.mouse_space = mouse_space
            self.drawing_area.queue_draw()

    def on_button_release(self, widget, event):
        if event.button != self.held_mouse_button:
            return

        allocation = widget.get_allocation()
        mouse_space = self.board.space_at_point(event.x, event.y, allocation.width, allocation.height)

        if mouse_space is not None:
            if self.held_mouse_button == 1:
                self.board.reveal_space(mouse_space)
            elif self.held_mouse_button == 3:
                self.board.flag_space(mouse_space, 1)

        self.mouse_space = None
        self.held_mouse_button = None
        self.drawing_area.queue_draw()

    def on_area_motion(self, widget, event):
        allocation = widget.get_allocation()
        mouse_space = self.board.space_at_point(event.x, event.y, allocation.width, allocation.height)

        if self.held_mouse_button is not None and mouse_space != self.mouse_space:
            self.mouse_space = mouse_space
            self.drawing_area.queue_draw()


def main(argv):
    window = MainWindow()

    gtk.main()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

