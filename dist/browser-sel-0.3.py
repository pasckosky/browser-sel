#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from xdg import DesktopEntry, IconTheme
import glob

import sys
import os

__version__ = "0.3"
__GITHUB_HOST__ = "https://raw.githubusercontent.com/pasckosky/browser-sel/master/"


def request_http():
    try:
        #raise Exception, "test"
        import requests
        advanced = True
    except:
        import urllib.request
        import urllib.error
        import urllib.parse
        advanced = False

    def request_page_advanced(url):
        r = requests.get(url)
        if r.status_code == 200:
            page = r.text
            r.close()
            return page
        else:
            print("Error %d on HTTP request" % r.status_code)
            r.close()
            return ""

    def request_page_old(url):
        print("Old request of %s" % url)
        f = urllib.request.urlopen(url)
        try:
            page = f.read()
        except:
            print("Error on HTTP request")
            page = ""
        f.close()
        return page

    return request_page_advanced if advanced else request_page_old


def check_version(ref_version):
    fn_get = request_http()
    lastest_url = "%s/dist/latest" % __GITHUB_HOST__
    lastest_version = fn_get(lastest_url).strip()
    print("Lastes version is %s" % lastest_version)
    print("You have version %s" % ref_version)
    sys.exit(0)


def download_last(ref_version, dest_fname, update):
    fn_get = request_http()
    lastest_url = "%s/dist/latest" % __GITHUB_HOST__
    lastest_version = fn_get(lastest_url).strip()

    if update and lastest_version == ref_version:
        print("You already have the last version")
        sys.exit(0)
    if update:
        print("You have version %s, downloading version %s" %
              (ref_version, lastest_version))

    if lastest_version == "":
        print("Errors while checking lastest version")
        sys.exit(1)
    ver_url = "%s/dist/browser-sel-%s.py" % (__GITHUB_HOST__, lastest_version)
    script_file = fn_get(ver_url)
    if script_file == "":
        print("Errors while getting lastest version")
        sys.exit(1)

    fout = open(dest_fname, "w")
    fout.write(script_file)
    fout.close()
    print("File version %s has been saved as %s" %
          (lastest_version, dest_fname))
    if not update:
        print("Move it wherever you please")
    sys.exit(0)


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
        open(filename, "w").write("")

    lns = (x.strip() for x in open(filename, "r").readlines())
    desktops = (x for x in lns if x != "")
    return list(desktops)


def save_conf(filename, desktops):
    conf_dir = os.path.dirname(filename)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    open(filename, "w").write("\n".join(desktops))


ICON_SIZE = 16


class DesktopFile(object):

    def __init__(self, filename, urls):
        self.filename = filename
        self.urls = urls
        self.entry = DesktopEntry.DesktopEntry(filename)
        icon_name = self.entry.getIcon()
        self.icon_path = None
        if not icon_name is None:
            self.icon_path = IconTheme.getIconPath(icon_name, ICON_SIZE)
        self.tooltip = "\n".join(
            [self.entry.getName(), self.entry.getComment()])
        self.short_name = self.entry.getName()

        actions = self.entry.get(
            "Actions", group="Desktop Entry", type="string", list=True)

        self.btn = [self.build_btn(None)] + [self.build_btn(a)
                                             for a in actions]

    def build_btn(self, action):

        if self.icon_path is None:
            img = None
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.icon_path, width=ICON_SIZE, height=ICON_SIZE, preserve_aspect_ratio=True)
            img = Gtk.Image.new_from_pixbuf(pixbuf)

        # img = None if self.icon_path is None else Gtk.Image.new_from_file(
        #     self.icon_path)

        if action is None:
            short_name = self.short_name
            tooltip = self.tooltip
            exec_cmd = self.entry.getExec()
        else:
            group = "Desktop Action %s" % action
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
            label.set_markup("<small>%s</small>" % short_name)
            vbox.pack_start(label, True, True, 0)

        btn.set_property("tooltip-text", tooltip)

        btn.exec_cmd = exec_cmd.replace(
            "%u", "%U").replace("%U", '"%s"') + " &"
        btn.connect("clicked", self.onClick)
        return btn

    def onClick(self, btn):
        if len(self.urls) == 0:
            os.system(btn.exec_cmd.replace('"%s"', ""))
        else:
            for u in self.urls:
                os.system(btn.exec_cmd % u)
        Gtk.main_quit()


def main(url_list):
    browsers = load_conf(CONF_FILE)
    if browsers == []:
        print("""Browser list is empty.

$ %s --scan

to build (update) the list of the browsers.
You can manually edit %s file to remove/add programs
""" % (sys.argv[0], CONF_FILE))
        sys.exit(0)

    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    win.set_border_width(10)
    # win.set_type_hint(Gdk.WindowTypeHint.UTILITY)

    if len(url_list) == 0:
        win.set_title("Open")
    elif len(url_list) == 1:
        win.set_title(url_list[0])
    else:
        win.set_title("Multiple urls")

    # accel = Gtk.AccelGroup()
    # win.add_accel_group(accel)
    #
    # key, mod = Gtk.accelerator_parse("ESC")
    # win.add_accelerator("destroy",accel, key, mod, Gtk.AccelFlags.VISIBLE)

    grid = Gtk.Grid()
    win.add(grid)

    column = 1
    row = 1
    for b in browsers:
        if not os.path.exists(b):
            continue

        entry = DesktopFile(b, url_list)
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
        print("Scanning %s" % d)
        files = glob.glob(os.path.join(d, "*.desktop"))
        for f in files:
            de = DesktopEntry.DesktopEntry(f)
            if "WebBrowser" in de.getCategories():
                print("Found %s" % f)
                ret.append(f)

    save_conf(CONF_FILE, ret)


def update_program():
    download_last(__version__, sys.argv[0], True)


def check_for_updates():
    check_version(__version__)


def show_help():
    print("HELP")


def update_scheme(schemes, desktop):
    def update(line):
        try:
            k, v = line.split("=")
        except ValueError:
            return line
        h = k.split("/")
        if h[0] != "x-scheme-handler":
            return line
        if not h[1] in schemes:
            return line
        return "%s=%s" % (k, desktop)

    fname = os.path.expanduser("~/.config/mimeapps.list")
    lines = (x.strip() for x in open(fname, "r").readlines())
    adjusted = [update(x) for x in lines]
    open(fname, "w").write("\n".join(adjusted))


def install_desktop():
    localdir = os.path.expanduser("~/.local/share/applications")
    if not os.path.exists(localdir):
        os.path.makedirs(localdir)
    open(os.path.join(localdir, "browser-sel.desktop"), "w").write("""[Desktop Entry]
Version=1.0
Name=Browser Selector
Comment=Choose a browser for opening urls
Icon=web-browser
GenericName=Web Browser
Exec=%(filename)s %%U
Terminal=false
Type=Application
Categories=Network;WebBrowser;
StartupNotify=true
X-MultipleArgs=false
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;x-scheme-handler/ftp;
Keywords=web;browser;internet;
X-Desktop-File-Install-Version=0.24
""" % {
        "filename": os.path.realpath(sys.argv[0])
    })

    update_scheme(["http", "https", "about"], "browser-sel.desktop")


default_op = {
    "--scan": scan_for_browsers,
    "--update": update_program,
    "--check": check_for_updates,
    "--install": install_desktop,
    "--help": show_help
}

if __name__ == "__main__":
    op = None if len(sys.argv) <= 1 else sys.argv[1]

    if op in default_op:
        default_op[op]()
    else:
        main(sys.argv[1:])
