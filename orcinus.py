#!/usr/bin/python3

"""Simple ORCA graphical user interface."""

from tkinter import BooleanVar
from tkinter import DoubleVar
from tkinter import IntVar
from tkinter import StringVar
from tkinter import Tk

from tkinter import filedialog
from tkinter import Spinbox
from tkinter import Text
from tkinter.ttk import Button
from tkinter.ttk import Checkbutton
from tkinter.ttk import Combobox

from tkinter.ttk import Entry
from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Style


class Questionnaire(Frame):
    """Interface for simple questionnaires."""

    def __init__(self, master=None, fields=None):
        """Construct object."""
        super().__init__(master)
        self.master = master
        self.fields = fields
        self.create_widgets()
        self.clear()

    def get_values(self):
        """Return a dictionary of all variable values."""
        values = {}
        for name in self.variable:
            if not self.fields[name]["visible"]:
                values[name] = None
                continue

            values[name] = self.variable[name].get()
            if values[name] == "None":
                values[name] = None

            if "values" in self.fields[name]:
                translator = self.fields[name]["values"]
                if isinstance(translator, dict):
                    values[name] = translator[values[name]]

            if values[name] == "None":
                values[name] = None
        return values

    def clear(self, *args, **kwargs):
        """Clear all fields to default values."""
        if self.fields is None:
            return

        for name, desc in self.fields.items():
            self.variable[name].set(desc["default"])

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

        if self.fields is None:
            return

        for i, (name, desc) in enumerate(self.fields.items()):
            if "values" in desc:
                values = list(desc["values"])

            if "type" not in desc:
                # if no type is given, first guess it based on a default
                # value, or infer from the first valid value.
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
                # if no default is given, use the first valid value, or infer
                # from type.
                if "values" in desc:
                    desc["default"] = [v for v in values if v is not None][0]
                elif "type" in desc:
                    desc["default"] = desc["type"]()
                else:
                    raise ValueError(
                        f"could not infer default, please specify: {desc}"
                    )

            if desc["type"] is int:
                self.variable[name] = IntVar(self)
            elif desc["type"] is bool:
                self.variable[name] = BooleanVar(self)
            elif desc["type"] is str:
                self.variable[name] = StringVar(self)
            elif desc["type"] is float:
                self.variable[name] = DoubleVar(self)
            else:
                raise ValueError(f"unknown type '{desc['type']}'")

            if "text" in desc:
                text = desc["text"]
            else:
                text = name.capitalize()

            if "widget" not in desc:
                # TODO(schneiderfelipe): should this be default?
                desc["widget"] = Combobox

            if desc["widget"] is Checkbutton:
                self.widget[name] = desc["widget"](
                    self, variable=self.variable[name], text=text
                )
            elif "values" in desc:
                self.widget[name] = desc["widget"](
                    self, textvariable=self.variable[name], values=values
                )
            else:
                self.widget[name] = desc["widget"](
                    self, textvariable=self.variable[name]
                )
            self.widget[name].grid(row=i, column=1, sticky="ew")

            if desc["widget"] is not Checkbutton:
                self.label[name] = Label(self, text=text + ":")
                self.label[name].grid(row=i, column=0, sticky="ew")

            if "visible" not in desc:
                desc["visible"] = True


class InputFrame(Frame):
    """Interface for input generation."""

    def __init__(self, master=None):
        """Construct object."""
        super().__init__(master)
        self.master = master
        self.create_widgets()
        self.update()

    def create_widgets(self):
        """Populate object and its widgets."""
        self.text = Text(self)
        self.clear_button = Button(self, text="Clear")
        self.save_button = Button(self, text="Save")
        self.questions = Questionnaire(
            self,
            {
                "short description": {"widget": Entry, "type": str},
                "task": {
                    "values": {
                        "Single point": "SP",
                        "Geometry optimization": "Opt",
                        "Frequencies": "Freq",
                        "Nudged elastic band": "NEB",
                    }
                },
                "optimization": {"widget": Checkbutton, "default": True},
                "frequencies": {"widget": Checkbutton, "default": False},
                "charge": {
                    "widget": Spinbox,
                    "text": "Total charge",
                    "values": range(-10, 11),
                    "default": 0,
                },
                "multiplicity": {
                    "widget": Spinbox,
                    "text": "Spin multiplicity",
                    "values": range(1, 11),
                },
                "unrestricted": {"widget": Checkbutton, "default": False},
                "corresponding orbitals": {
                    "widget": Checkbutton,
                    "default": True,
                },
                "model": {
                    "values": ["HF", "DFTB", "DFT", "MP2", "CCSD"],
                    "default": "DFT",
                },
                "triples correction": {"widget": Checkbutton, "default": True},
                "dlpno": {
                    "text": "DLPNO",
                    "widget": Checkbutton,
                    "default": True,
                },
                "frozen core": {
                    "widget": Checkbutton,
                    "values": {True: "FrozenCore", False: "NoFrozenCore"},
                    "default": True,
                },
                "hamiltonian": {
                    "values": {"GFN1-xTB": "XTB1", "GFN2-xTB": "XTB2"},
                    "default": "GFN2-xTB",
                },
                "functional": {
                    "text": "XC functional",
                    "values": {
                        "LDA": "LDA",
                        "GGA:B97": "B97",
                        "GGA:BP86": "BP86",
                        "GGA:BLYP": "BLYP",
                        "GGA:PW91": "PW91",
                        "GGA:PWP": "PWP",
                        "GGA:PBE": "PBE",
                        "GGA:revPBE": "revPBE",
                        "Meta-GGA:M06L": "M06L",
                        "Meta-GGA:TPSS": "TPSS",
                        "Hybrid:B3LYP": "B3LYP",
                        "Hybrid:B3PW91": "B3PW91",
                        "Hybrid:PWP1": "PWP1",
                        "Hybrid:PBE0": "PBE0",
                        "RS-Hybrid:wB97X": "wB97X",
                        "RS-Hybrid:LC-BLYP": "LC-BLYP",
                        "RS-Hybrid:CAM-B3LYP": "CAM-B3LYP",
                        "Meta-Hybrid:TPSSh": "TPSSh",
                        "Double-Hybrid:B2PLYP": "B2PLYP",
                        "RS-Double-Hybrid:wB2PLYP": "wB2PLYP",
                    },
                    "default": "GGA:BLYP",
                },
                "dispersion correction": {
                    "values": [None, "D2", "D3Zero", "D3BJ", "D4"],
                    "default": "D4",
                },
                "resolution of identity": {
                    "values": {
                        None: "NoRI",
                        "RI": "RI",
                        "RI-JK": "RI-JK",
                        "RIJCOSX": "RIJCOSX",
                    },
                    "default": "RI",
                },
                "relativity": {
                    "values": [None, "DKH", "ZORA"],
                    "default": None,
                },
                "basis set": {
                    "values": [
                        "def2-SV(P)",
                        "def2-SVP",
                        "def2-TZVP",
                        "def2-TZVP(-f)",
                        "def2-TZVPP",
                        "def2-QZVP",
                        "def2-QZVPP",
                    ],
                    "default": "def2-TZVP",
                },
                "effective core potential": {
                    "values": [None, "def2-ECP"],
                    "default": "def2-ECP",
                },
                "numerical quality": {
                    "values": {
                        "Normal": "Grid3 FinalGrid4",
                        "Good": "TightSCF Grid4 FinalGrid5",
                        "Excellent": "TightSCF Grid5 FinalGrid6",
                    },
                    "default": "Good",
                },
            },
        )

        self.text.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.questions.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.clear_button.grid(row=1, column=1, sticky="nsew")
        self.save_button.grid(row=1, column=2, sticky="nsew")

        self.clear_button.bind("<Button-1>", self.questions.clear)
        self.save_button.bind("<Button-1>", self.save)
        for _, var in self.questions.variable.items():
            var.trace("w", self.update)

    def _get_values(self):
        """Ensure widgets properly influence each other."""
        v = self.questions.get_values()

        if v["task"] == "Freq":
            self.questions.enable("optimization")
        else:
            self.questions.disable("optimization")

        if v["task"] == "NEB":
            self.questions.enable("frequencies")
        else:
            self.questions.disable("frequencies")

        if v["unrestricted"]:
            self.questions.enable("multiplicity")
            self.questions.enable("corresponding orbitals")
        else:
            self.questions.disable("multiplicity")
            self.questions.disable("corresponding orbitals")

        if v["model"] == "DFTB":
            self.questions.enable("hamiltonian")
        else:
            self.questions.disable("hamiltonian")

        if v["model"] == "DFT":
            self.questions.enable("functional")
            self.questions.enable("dispersion correction")
        else:
            self.questions.disable("functional")
            self.questions.disable("dispersion correction")

        if v["model"] == "CCSD":
            self.questions.enable("triples correction")
            self.questions.enable("dlpno")
        else:
            self.questions.disable("triples correction")
            self.questions.disable("dlpno")

        if v["model"] in {"MP2", "CCSD"}:
            self.questions.enable("frozen core")
        else:
            self.questions.disable("frozen core")

        if v["model"] in {"HF", "DFT", "MP2", "CCSD"}:
            self.questions.enable("resolution of identity")
            self.questions.enable("relativity")
            self.questions.enable("basis set")
            self.questions.enable("effective core potential")
            self.questions.enable("numerical quality")
        else:
            self.questions.disable("resolution of identity")
            self.questions.disable("relativity")
            self.questions.disable("basis set")
            self.questions.disable("effective core potential")
            self.questions.disable("numerical quality")

        return self.questions.get_values()

    def update(self, *args, **kwargs):
        """Update input content with currently selected options."""
        v = self._get_values()

        keywords = []
        lines = []

        if v["unrestricted"]:
            if v["model"] in {"DFTB", "DFT"}:
                keywords.append("UKS")
            else:
                keywords.append("UHF")
        else:
            if v["model"] in {"DFTB", "DFT"}:
                keywords.append("RKS")
            else:
                keywords.append("RHF")

        keywords.append(v["resolution of identity"])
        keywords.append(v["relativity"])

        if v["model"] == "DFT":
            keywords.append(v["functional"])
        elif v["model"] == "DFTB":
            keywords.append(v["hamiltonian"])
        elif v["model"] == "CCSD":
            kw = v["model"]
            if v["triples correction"]:
                kw = kw + "(T)"
            if v["dlpno"]:
                kw = "DLPNO-" + kw
            keywords.append(kw)

        keywords.append(v["dispersion correction"])

        keywords.append(v["basis set"])
        if v["resolution of identity"] in {"RI", "RIJCOSX"}:
            if v["relativity"]:
                keywords.append("SARC/J")
            else:
                keywords.append("def2/J")
        if v["resolution of identity"] == "RIJCOSX":
            keywords.append(f"{v['basis set']}/C")
        if v["resolution of identity"] == "RI-JK":
            keywords.append("def2/JK")

        if v["model"] in {"MP2", "CCSD"}:
            keywords.append(v["frozen core"])

        if v["corresponding orbitals"]:
            keywords.append("UCO")

        if v["task"] == "Freq" and v["optimization"]:
            keywords.append("Opt")
        keywords.append(v["task"])
        if v["task"] == "NEB" and v["frequencies"]:
            keywords.append("Freq")

        if v["numerical quality"] != "Grid3 FinalGrid4" and (
            v["task"] == "Opt" or v["optimization"]
        ):
            keywords.append("TightOpt")
        keywords.append(v["numerical quality"])

        if v["short description"]:
            lines.append(f"# {v['short description']}")
        lines.append(f"! {' '.join([k for k in keywords if k is not None])}")

        if not v["multiplicity"]:
            v["multiplicity"] = 1
        lines.append(f"\n*xyzfile {v['charge']} {v['multiplicity']} init.xyz")

        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(lines))

    def save(self, *args, **kwargs):
        """Ask user for filename and save the current input."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".inp",
            filetypes=[("Input Files", "*.in*"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, "w") as f:
            text = self.text.get("1.0", "end")
            f.write(text)


if __name__ == "__main__":
    main_window = Tk()

    style = Style()
    if style.theme_use() == "default":
        style.theme_use("clam")

    main_window.title(__doc__.split("\n", 1)[0].strip().strip("."))
    input_frame = InputFrame(main_window)
    input_frame.pack()
    main_window.mainloop()
