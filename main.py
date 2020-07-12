#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk
from xdg import DesktopEntry,IconTheme
import glob

import sys, os

SCAN_DIR = [
    os.path.expanduser("~/.local/share/applications"),
    "/usr/share/applications"
]

CONF_FILE = os.path.expanduser("~/.local/browser_sel/config")

def load_conf(filename):
    conf_dir = os.path.dirname(filename)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    if not os.path.exists(filename):
        open(filename,"w").write("")

    lns = (x.strip() for x in open(filename,"r").readlines())
    desktops = (x for x in lns if x!="")
    return list(desktops)

def save_conf(filename, desktops):
    conf_dir = os.path.dirname(filename)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    open(filename,"w").write("\n".join(desktops))


class DesktopFile(object):

    def __init__(self, filename):
        self.filename = filename
        self.entry = DesktopEntry.DesktopEntry(filename)
        icon_name = self.entry.getIcon()
        self.icon_path = None
        if not icon_name is None:
            self.icon_path = IconTheme.getIconPath(icon_name)
        self.tooltip = "\n".join([self.entry.getName(),self.entry.getComment()])
        self.short_name = self.entry.getName()

        actions = self.entry.get("Actions",group="Desktop Entry", type="string", list=True)

        self.btn = [self.build_btn(None)] + [self.build_btn(a) for a in actions]

    def build_btn(self, action):

        img = None if self.icon_path is None else Gtk.Image.new_from_file(self.icon_path)

        if action is None:
            short_name = self.short_name
            tooltip = self.tooltip
            exec_cmd = self.entry.getExec()
        else:
            group = "Desktop Action %s"%action
            action_name = self.entry.get("Name", group=group, type="string")
            short_name = action_name
            tooltip = "\n".join([self.tooltip, action_name])
            exec_cmd = self.entry.get("Exec", group=group, type="string")

        if img is None:
            btn = Gtk.Button(label=short_name)
        else:
            btn = Gtk.Button()
            vbox = Gtk.VBox()
            btn.add(vbox)
            vbox.pack_start(img, True, True, 0)
            label = Gtk.Label()
            label.set_markup("<small>%s</small>"%short_name)
            vbox.pack_start(label, True, True, 0)
            
        btn.set_property("tooltip-text", tooltip)

        print (exec_cmd)
        btn.connect("clicked", self.onClick)
        return btn

    def onClick(self, btn):
        print("Click")
        
def main(url_list):
    browsers = load_conf(CONF_FILE)
    print(browsers)

    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    win.set_border_width(10)
    #win.set_type_hint(Gdk.WindowTypeHint.UTILITY)
    accel = Gtk.AccelGroup()
    win.add_accel_group(accel)

    key, mod = Gtk.accelerator_parse("ESC")
    win.add_accelerator("destroy",accel, key, mod, Gtk.AccelFlags.VISIBLE)

    grid = Gtk.Grid()
    win.add(grid)

    column = 1
    row = 1
    for b in browsers:
        if not os.path.exists(b):
            continue

        entry = DesktopFile(b)
        for b in entry.btn:
            grid.attach(b, column, row, 1, 1)
            column += 1
        column = 1
        row += 1

    win.show_all()
    Gtk.main()

def scan_for_browsers():
    ret = []
    for d in SCAN_DIR:
        print("Scanning %s"%d)
        files = glob.glob(os.path.join(d,"*.desktop"))
        for f in files:
            de = DesktopEntry.DesktopEntry(f)
            if "WebBrowser" in de.getCategories():
                print("Found %s"%f)
                ret.append(f)
        
    save_conf(CONF_FILE, ret)

def update_program():
    print("Nah, not now")

def check_for_updates():
    print("Nah, not now")

def show_help():
    print("HELP")

default_op = {
    "--scan": scan_for_browsers,
    "--update": update_program,
    "--check": check_for_updates,
    "--help": show_help
}

if __name__ == "__main__":
    op = None if len(sys.argv)<=1 else sys.argv[1]

    if op in default_op:
        default_op[op]()
    else:
        main(sys.argv[1:])