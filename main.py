#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk

import sys, os

def qualcosa(btn):
    print("Pulsante premuto")


win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
#win.set_type_hint(Gdk.WindowTypeHint.UTILITY)

hbox = Gtk.Box(spacing=6)
win.add(hbox)

btn = Gtk.Button.new_with_label("Premi me")
btn.connect("clicked", qualcosa)
hbox.pack_start(btn, True, True, 0)



win.show_all()
Gtk.main()