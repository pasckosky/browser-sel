#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk
from xdg import DesktopEntry,IconTheme

import sys, os

class DesktopFile(object):

    def __init__(self, filename):
        self.filename = filename
        self.entry = DesktopEntry.DesktopEntry(filename)
        icon_name = self.entry.getIcon()
        icon_path = None
        if not icon_name is None:
            icon_path = IconTheme.getIconPath(icon_name)
        
        if icon_path is None:
            self.btn = Gtk.Button(label="Browser")
        else:
            img = None if icon_path is None else Gtk.Image.new_from_file(icon_path)
            self.btn = Gtk.Button()
            self.btn.add(img)

            # tooltip: self.entry.getName() self.entry.getComment()

        self.btn.connect("clicked", self.onClick)

    def onClick(self, btn):
        command = self.entry.getExec()
        print("Click %s"% command)
        
browsers = ["/usr/share/applications/ff56.desktop",
            "/usr/share/applications/firefox.desktop",
            "/usr/share/applications/brave-browser.desktop",
            "/usr/share/applications/google-chrome.desktop",
            "/usr/share/applications/google-chrome-incognito.desktop"]


win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
#win.set_type_hint(Gdk.WindowTypeHint.UTILITY)

vbox = Gtk.VBox(spacing=6)
win.add(vbox)

added = 0
hbox = None
for b in browsers:
    if not os.path.exists(b):
        continue

    btn = DesktopFile(b)
    if added >= 3:
        hbox = None

    if hbox is None:
        hbox = Gtk.HBox(spacing=6)
        added = 0
        vbox.pack_start(hbox,True,True,0)

    hbox.pack_start(btn.btn, True, True, 0)

win.show_all()
Gtk.main()