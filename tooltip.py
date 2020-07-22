#!/usr/bin/python3

"""Simple tooltip widget."""

from tkinter import TclError
from tkinter import Toplevel
from tkinter.ttk import Frame
from tkinter.ttk import Label


# http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
class Tooltip(Frame):
    """Simple tooltip."""

    def __init__(self, widget):
        """Construct object."""
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self, text):
        """Display text in tooltip window."""
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call(
                "::tk::unsupported::MacWindowStyle",
                "style",
                tw._w,
                "help",
                "noActivates",
            )
        except TclError:
            pass
        label = Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
        )
        label.pack(ipadx=1)

    def hide_tip(self):
        """Hide tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    """Create a tooltip for widget."""
    toolTip = Tooltip(widget)

    def enter(event):
        toolTip.show_tip(text)

    def leave(event):
        toolTip.hide_tip()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
