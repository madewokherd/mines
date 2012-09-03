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

import dreamsweeper

border_color = gtk.gdk.color_parse('#CCC')

clear_color = gtk.gdk.color_parse('#FFF')
clear_num_color = gtk.gdk.color_parse('#000')

mine_color = gtk.gdk.color_parse('#000')
mine_num_color = gtk.gdk.color_parse('#FFF')

unknown_color = gtk.gdk.color_parse('#888')
unknown_num_color = gtk.gdk.color_parse('#444')

class MainWindow(object):
    def __init__(self):
        self.window = gtk.Window()

        self.window.connect('delete-event', self.on_delete)

        self.board = dreamsweeper.SquareBoard()

        self.drawing_area = gtk.DrawingArea()

        self.drawing_area.connect('expose-event', self.on_area_expose)
        self.drawing_area.connect('motion-notify-event', self.on_area_motion)

        self.drawing_area.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.POINTER_MOTION_MASK)

        self.drawing_area.show()

        self.window.add(self.drawing_area)

        self.window.show()

        self.mouse_space = None

    def on_delete(self, widget, event):
        gtk.main_quit()

    def on_area_expose(self, widget, event):
        drawable = widget.window
        allocation = widget.get_allocation()
        gc = drawable.new_gc()
        for space in self.board.spaces:
            polygon = self.board.get_polygon(space, allocation.width, allocation.height)

            polygon = tuple((int(x), int(y)) for (x, y) in polygon)

            if space == self.mouse_space:
                gc.set_rgb_fg_color(clear_color)
            else:
                gc.set_rgb_fg_color(unknown_color)
            drawable.draw_polygon(gc, True, polygon)

            gc.set_rgb_fg_color(border_color)
            drawable.draw_polygon(gc, False, polygon)
        return True

    def on_area_motion(self, widget, event):
        allocation = widget.get_allocation()
        mouse_space = self.board.space_at_point(event.x, event.y, allocation.width, allocation.height)

        if mouse_space != self.mouse_space:
            self.mouse_space = mouse_space
            self.drawing_area.queue_draw()


def main(argv):
    window = MainWindow()

    gtk.main()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

