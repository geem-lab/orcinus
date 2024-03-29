#!/usr/bin/python3

"""Widget that simplifies defining questionnaires."""

import os
import pickle
from tkinter import BooleanVar
from tkinter import DoubleVar
from tkinter import IntVar
from tkinter import StringVar
from tkinter import TclError
from tkinter.ttk import Checkbutton
from tkinter.ttk import Combobox
from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import LabelFrame
from tkinter.ttk import Notebook

import numpy as np

from orcinus.gui.tooltip import create_tooltip

# TODO(schneiderfelipe): this will change in the future.
DATA_DIR = os.path.expanduser("~")


class Questionnaire(Frame):
    """Interface for simple questionnaires."""

    def __init__(
        self,
        master=None,
        fields=None,
        state_filename=None,
        padx=1,
        pady=2,
        column_minsize=240,
    ):
        """Construct object."""
        super().__init__(master)
        self.padx = padx
        self.pady = pady
        self.column_minsize = column_minsize
        self.state_filename = state_filename
        self.master = master
        self.fields = fields
        self.create_widgets()

    def get_values(self):
        """Return a dictionary of all variable values."""
        self.update_widgets()

        values = {}
        for name in self.variable:
            if not self.fields[name]["visible"]:
                values[name] = None
                continue

            try:
                values[name] = self.variable[name].get()
            except TclError:
                values[name] = self.fields[name]["default"]

            if values[name] == "None":
                values[name] = None

            if "values" in self.fields[name]:
                translator = self.fields[name]["values"]
                if isinstance(translator, dict):
                    try:
                        values[name] = translator[values[name]]
                    except KeyError:
                        values[name] = translator[self.fields[name]["default"]]

            if values[name] == "None":
                values[name] = None
        return values

    def init_widgets(self, *args, ignore_state=False, **kwargs):
        """Clear all fields to default values."""
        if self.fields is None:
            return

        init_values = {
            name: desc["default"] for name, desc in self.fields.items()
        }
        state_path = os.path.join(DATA_DIR, self.state_filename)
        if (
            not ignore_state
            and self.state_filename
            and os.path.isfile(state_path)
        ):
            with open(state_path, "rb") as f:
                state = pickle.load(f)
            init_values.update(state)

        for name, value in init_values.items():
            try:
                self.variable[name].set(value)
            except KeyError:
                pass

        self.update_widgets()

    def store_widgets(self, *args, **kwargs):
        """Store all fields to disk."""
        if self.fields is None:
            return

        if self.state_filename:
            state_path = os.path.join(DATA_DIR, self.state_filename)
            state = {}
            for name, _ in self.fields.items():
                try:
                    state[name] = self.variable[name].get()
                except TclError:
                    state[name] = self.fields[name]["default"]

            with open(state_path, "wb") as f:
                pickle.dump(state, f)

    def enable(self, name):
        """Show a widget by name."""
        if self.fields[name]["visible"]:
            return
        self.toggle(name)

    def disable(self, name):
        """Hide a widget by name."""
        if not self.fields[name]["visible"]:
            return
        self.toggle(name)

    def toggle(self, name):
        """Hide or show a widget by name."""
        if not self.fields[name]["visible"]:
            self.widget[name].grid()
            if name in self.label:
                self.label[name].grid()
        else:
            self.widget[name].grid_remove()
            if name in self.label:
                self.label[name].grid_remove()
        self.fields[name]["visible"] = not self.fields[name]["visible"]

    def create_widgets(self):
        """Populate object and its widgets."""
        self.variable = {}
        self.label = {}
        self.widget = {}
        self.tab = {}
        self.group = {}
        self.notebook = Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        if self.fields is None:
            return

        for i, (name, desc) in enumerate(self.fields.items()):
            if "tab" not in desc:
                desc["tab"] = "main"

            if desc["tab"] not in self.tab:
                parent = Frame(self.notebook)
                parent.columnconfigure(
                    [0, 1], weight=1, minsize=self.column_minsize
                )
                self.notebook.add(parent, text=desc["tab"].capitalize())
                self.tab[desc["tab"]] = parent
            else:
                parent = self.tab[desc["tab"]]

            if "group" in desc:
                if desc["group"] not in self.group:
                    group = LabelFrame(parent, text=desc["group"].capitalize())
                    group.columnconfigure(
                        [0, 1], weight=1, minsize=self.column_minsize
                    )
                    group.grid(
                        row=i,
                        column=0,
                        columnspan=2,
                        sticky="ew",
                        padx=self.padx,
                        pady=9 * self.pady,
                    )
                    self.group[desc["group"]] = group
                else:
                    group = self.group[desc["group"]]
                parent = group

            if "values" in desc:
                values = list(desc["values"])

            if "type" not in desc:
                # if no type is given, first guess it based on a default value,
                # or infer from the first valid value.
                if "default" in desc and desc["default"] is not None:
                    desc["type"] = type(desc["default"])
                elif "values" in desc:
                    desc["type"] = type(
                        [v for v in values if v is not None][0]
                    )
                else:
                    raise ValueError(
                        f"could not infer type, please specify: {desc}"
                    )

            if "default" not in desc:
                # if no default is given, use the first value (even if None),
                # or infer from type.
                if "values" in desc:
                    desc["default"] = [v for v in values][0]
                elif "type" in desc:
                    desc["default"] = desc["type"]()
                else:
                    raise ValueError(
                        f"could not infer default, please specify: {desc}"
                    )

            if desc["type"] is int or desc["type"] is np.int64:
                self.variable[name] = IntVar(self)
            elif desc["type"] is bool:
                self.variable[name] = BooleanVar(self)
            elif desc["type"] is str:
                self.variable[name] = StringVar(self)
            elif desc["type"] is float:
                self.variable[name] = DoubleVar(self)
                if "values" in desc:
                    values = [np.round(v, 2) for v in values]
            else:
                raise ValueError(f"unknown type '{desc['type']}' for '{name}'")

            if "text" in desc:
                text = desc["text"]
            else:
                text = name.capitalize()

            if "widget" not in desc:
                # TODO(schneiderfelipe): should this be default?
                desc["widget"] = Combobox

            if desc["widget"] is Checkbutton:
                self.widget[name] = desc["widget"](
                    parent, variable=self.variable[name], text=text
                )
            elif "values" in desc:
                self.widget[name] = desc["widget"](
                    parent, textvariable=self.variable[name], values=values
                )
            else:
                self.widget[name] = desc["widget"](
                    parent, textvariable=self.variable[name]
                )
            self.widget[name].grid(
                row=i, column=1, sticky="ew", padx=self.padx, pady=self.pady
            )

            if "help" in desc:
                create_tooltip(self.widget[name], desc["help"])

            if desc["widget"] is not Checkbutton:
                self.label[name] = Label(parent, text=text + ":")
                self.label[name].grid(
                    row=i,
                    column=0,
                    sticky="ew",
                    padx=self.padx,
                    pady=self.pady,
                )

            if "visible" not in desc:
                desc["visible"] = True

        self.init_widgets()

    def update_widgets(self, *args, **kwargs):
        """Update widget states."""
        if self.fields is None:
            return

        options = {}
        for name in self.variable:
            try:
                options[name] = self.variable[name].get()
            except TclError:
                options[name] = self.fields[name]["default"]

        for name, desc in self.fields.items():
            # TODO(schneiderfelipe): allow an analogous key "freeze", which
            # does exactly the same as switch, but enables/disables the widget
            # instead of showing/hiding it. self.enable and sefl.disable should
            # then accept an argument policy="freeze" or policy="switch" to
            # make things easier. Both "switch" (meaning available/unavailable)
            # and "freeze" (meaning impossible to change) can be used at the
            # same time. "freeze" might require setting which value is locked.
            if "switch" in desc:
                if desc["switch"](options):
                    self.enable(name)
                else:
                    self.disable(name)
