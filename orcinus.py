#!/usr/bin/python3

"""Simple ORCA graphical user interface."""

from tkinter import filedialog
from tkinter import Spinbox
from tkinter import Text
from tkinter import Tk
from tkinter.ttk import Button
from tkinter.ttk import Checkbutton
from tkinter.ttk import Entry
from tkinter.ttk import Frame
from tkinter.ttk import Style

from questionnaire import Questionnaire


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
                "short description": {
                    "help": "A one-line description for your calculation.",
                    "widget": Entry,
                    "type": str,
                },
                "task": {
                    "group": "basic",
                    "help": "The main task of your calculation.",
                    "values": {
                        "Single point": "SP",
                        "Geometry optimization": "Opt",
                        "Frequencies": "Freq",
                        "Nudged elastic band": "NEB",
                    },
                },
                "optimization": {
                    "group": "basic",
                    "help": (
                        "Whether to do a geometry optimization pior to "
                        "the frequencies calculation."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                },
                "frequencies": {
                    "group": "basic",
                    "help": (
                        "Whether to do a frequencies calculation after "
                        "the nudged elastic band calculation."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "charge": {
                    "group": "basic",
                    "help": "Net charge of you calculation.",
                    "widget": Spinbox,
                    "text": "Total charge",
                    "values": range(-100, 101),
                    "default": 0,
                },
                "multiplicity": {
                    "group": "basic",
                    "help": "Spin multiplicity of you calculation.",
                    "widget": Spinbox,
                    "text": "Spin multiplicity",
                    "values": range(1, 101),
                },
                "unrestricted": {
                    "group": "basic",
                    "help": (
                        "Whether an unrestricted wavefunction should be "
                        "used."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "corresponding orbitals": {
                    "help": (
                        "Whether unrestricted corresponding orbitals "
                        "should be calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "model": {
                    "group": "method",
                    "help": "Class of calculation.",
                    "values": ["HF", "DFTB", "DFT", "MP2", "CCSD"],
                    "default": "DFT",
                },
                "frozen core": {
                    "group": "method",
                    "help": (
                        "Whether the frozen core approximation should be "
                        "used."
                    ),
                    "widget": Checkbutton,
                    "values": {True: "FrozenCore", False: "NoFrozenCore"},
                    "default": True,
                },
                "dlpno": {
                    "group": "method",
                    "help": (
                        "Whether the domain-based local pair natural "
                        "orbital approximation should be used."
                    ),
                    "text": "DLPNO",
                    "widget": Checkbutton,
                    "default": True,
                },
                "triples correction": {
                    "group": "method",
                    "help": (
                        "Whether perturbative triples correction should "
                        "be calculated used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                },
                "hamiltonian": {
                    "group": "method",
                    "help": "Which model Hamiltonian should be used.",
                    "values": {"GFN1-xTB": "XTB1", "GFN2-xTB": "XTB2"},
                    "default": "GFN2-xTB",
                },
                "functional": {
                    "group": "method",
                    "help": "Which density functional should be used.",
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
                    "group": "method",
                    "help": (
                        "Which atomic pairwise dispersion correction "
                        "should be used."
                    ),
                    "values": [None, "D2", "D3Zero", "D3BJ", "D4"],
                    "default": "D4",
                },
                "relativity": {
                    "group": "method",
                    "help": (
                        "Which scalar relativistic correction should be "
                        "used."
                    ),
                    "values": [None, "DKH", "ZORA"],
                    "default": None,
                },
                "basis set": {
                    "group": "method",
                    "help": "Which basis set should be used.",
                    "values": [
                        "def2-SV(P)",
                        "def2-SVP",
                        "def2-TZVP",
                        "def2-TZVP(-f)",
                        "def2-TZVPP",
                        "def2-QZVP",
                        "def2-QZVPP",
                    ],
                    "default": "def2-SV(P)",
                },
                "effective core potential": {
                    "group": "method",
                    "help": (
                        "Whether effective core potentials should be used. "
                        "NOT IMPLEMENTED."
                    ),
                    "values": [None, "def2-ECP"],
                    "default": "def2-ECP",
                },
                "resolution of identity": {
                    "help": (
                        "Whether a resolution of identity approximation "
                        "should be used."
                    ),
                    "values": {
                        None: "NoRI",
                        "RI": "RI",
                        "RI-JK": "RI-JK",
                        "RIJCOSX": "RIJCOSX",
                    },
                    "default": "RI",
                },
                "numerical quality": {
                    "help": "Which numerical quality is desired.",
                    "values": {"Normal": 3, "Good": 4, "Excellent": 5},
                    "default": "Normal",
                },
            },
        )

        self.text.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.questions.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.clear_button.grid(row=1, column=1, sticky="nsew")
        self.save_button.grid(row=1, column=2, sticky="nsew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.clear_button.bind("<Button-1>", self.questions.clear)
        self.save_button.bind("<Button-1>", self.save)
        for _, var in self.questions.variable.items():
            var.trace("w", self.update)

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

        if v["model"] in {"HF", "MP2"}:
            keywords.append(v["model"])
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

        if v["numerical quality"] > 3:
            if v["task"] == "Opt" or v["optimization"]:
                keywords.append("TightOpt")
            keywords.append("TightSCF")
        keywords.append(f"Grid{v['numerical quality']}")
        keywords.append(f"FinalGrid{v['numerical quality'] + 1}")

        if v["short description"]:
            lines.append(f"# {v['short description']}")
        lines.append(f"! {' '.join([k for k in keywords if k is not None])}")

        if not v["multiplicity"]:
            v["multiplicity"] = 1
        lines.append(f"\n*xyzfile {v['charge']} {v['multiplicity']} init.xyz")

        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(lines))


if __name__ == "__main__":
    main_window = Tk()

    style = Style()
    if style.theme_use() == "default":
        style.theme_use("clam")

    main_window.title(__doc__.split("\n", 1)[0].strip().strip("."))
    input_frame = InputFrame(main_window)
    input_frame.pack(fill="both", expand=True)
    main_window.mainloop()
