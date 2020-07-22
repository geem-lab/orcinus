#!/usr/bin/python3

"""Orcinus orca.

Orcinus orca is a simple graphical user interface (GUI) for the ORCA quantum
chemistry package.
"""

from tkinter import filedialog
from tkinter import Spinbox
from tkinter import Text
from tkinter import Tk
from tkinter.ttk import Button
from tkinter.ttk import Checkbutton
from tkinter.ttk import Entry
from tkinter.ttk import Frame
from tkinter.ttk import Style

import numpy as np

from questionnaire import Questionnaire


class InputGUI(Frame):
    """Interface for input generation."""

    def __init__(self, master=None, padx=1, pady=2, column_minsize=240):
        """Construct object."""
        super().__init__(master)
        self.padx = padx
        self.pady = pady
        self.column_minsize = column_minsize
        self.master = master
        self.create_widgets()

    def save(self):
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

    def create_widgets(self):
        """Populate object and its widgets."""
        self.text = Text(self)
        self.clear_button = Button(self, text="Clear")
        self.save_button = Button(self, text="Save")
        self.questions = Questionnaire(
            self,
            padx=self.padx,
            pady=self.pady,
            column_minsize=self.column_minsize,
            fields={
                "short description": {
                    "help": ("A one-line description for your calculation."),
                    "widget": Entry,
                    "type": str,
                },
                # TODO(schneiderfelipe): support QM/MM calculations. In
                # particular, give options for electrostatic embedding,
                # capping method and choice of QM region.
                # TODO(schneiderfelipe): support for NEB: "Number of transit
                # points", "Climbing image"/"Transition state", convergence
                # criteria, etc.
                "task": {
                    "group": "basic information",
                    "help": ("The main task of your calculation."),
                    "values": [
                        "SP",
                        "Opt",
                        "Freq",
                        "Opt Freq",
                        "Scan",
                        "OptTS",
                        "OptTS Freq",
                        "IRC",
                        "NEB",
                        "NEB Freq",
                        "MD",
                        "NoIter",
                    ],
                },
                # TODO(schneiderfelipe): automatically select numerical
                # frequencies when only that is available.
                "numerical frequencies": {
                    "group": "basic information",
                    "help": (
                        "Whether to do a numerical frequencies calculation."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                    "switch": ("task", lambda v: "Freq" in v),
                },
                "charge": {
                    "group": "basic information",
                    "text": "Total charge",
                    "help": ("Net charge of you calculation."),
                    "widget": Spinbox,
                    "values": range(-100, 101),
                    "default": 0,
                },
                "multiplicity": {
                    "group": "basic information",
                    "text": "Spin multiplicity",
                    "help": ("Spin multiplicity of you calculation."),
                    "widget": Spinbox,
                    "values": range(1, 101),
                    "switch": "unrestricted",
                },
                "unrestricted": {
                    "group": "basic information",
                    "text": "Unrestricted calculation",
                    "help": (
                        "Whether an unrestricted wavefunction should be "
                        "used."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "uco": {  # TODO(schneiderfelipe): this goes somewhere else
                    "text": "Corresponding orbitals",
                    "help": (
                        "Whether unrestricted corresponding orbitals "
                        "should be calculated."
                    ),
                    "widget": Checkbutton,
                    "values": {False: None, True: "UCO"},
                    "switch": "unrestricted",
                },
                # TODO(schneiderfelipe): this should go to the broadest
                # possible category, above even task.
                "theory": {  # TODO(schneiderfelipe): use a better name
                    "group": "level of theory",
                    "help": ("Class of calculation."),
                    "values": ["MM", "HF", "DFTB", "DFT", "MP2", "CCSD"],
                    "default": "DFT",
                },
                # TODO(schneiderfelipe): properly select it when e.g. MP2 Freq
                "frozen core": {
                    "group": "level of theory",
                    "help": (
                        "Whether the frozen core approximation should be "
                        "used."
                    ),
                    "widget": Checkbutton,
                    "values": {True: "FrozenCore", False: "NoFrozenCore"},
                    "switch": ("theory", {"MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): switch to a black-box model selector
                "dlpno": {
                    "group": "level of theory",
                    "text": "DLPNO",
                    "help": (
                        "Whether the domain-based local pair natural "
                        "orbital approximation should be used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": ("theory", "CCSD"),
                },
                # TODO(schneiderfelipe): switch to a black-box model selector
                "triples correction": {
                    "group": "level of theory",
                    "help": (
                        "Whether perturbative triples correction should "
                        "be calculated used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": ("theory", "CCSD"),
                },
                "hamiltonian": {
                    "group": "level of theory",
                    "help": ("Which model Hamiltonian should be used."),
                    "values": {"GFN1-xTB": "XTB1", "GFN2-xTB": "XTB2"},
                    "default": "GFN2-xTB",
                    "switch": ("theory", "DFTB"),
                },
                # TODO(schneiderfelipe): allow selection of functional class
                # (LDA, GGA, Meta-GGA, Hybrid, LR-Hybrid, Meta-Hybrid,
                # Double-Hybrid and LR-Double-Hybrid)
                "functional": {
                    "group": "level of theory",
                    "text": "Exchange-correlation functional",
                    "help": ("Which density functional should be used."),
                    "values": {
                        "LDA": "PWLDA",
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
                    "switch": ("theory", "DFT"),
                },
                "dispersion": {
                    "group": "level of theory",
                    "text": "Dispersion correction",
                    "help": (
                        "Which atomic pairwise dispersion correction "
                        "should be used."
                    ),
                    "values": [None, "D2", "D3Zero", "D3BJ", "D4"],
                    "default": "D4",
                    "switch": ("theory", "DFT"),
                },
                "relativity": {
                    "group": "level of theory",
                    "text": "Scalar relativistic approximation",
                    "help": (
                        "Which scalar relativistic approximation should be "
                        "used."
                    ),
                    "values": [None, "DKH", "ZORA"],
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                "spin-orbit coupling": {
                    "group": "level of theory",
                    "help": (
                        "Whether spin-orbit coupling should be taken into "
                        "account."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                # TODO(schneiderfelipe): give support for cc basis set family
                # (cc-pVTZ, etc.)
                # TODO(schneiderfelipe): choose basis sets based on classes
                # and properly show suitable selections. Also switch to basis
                # sets consistent with relativistic approximations.
                "basis set": {
                    "group": "level of theory",
                    "help": ("Which basis set should be used."),
                    "values": [
                        "def2-SV(P)",
                        "def2-SVP",
                        "def2-TZVP",
                        "def2-TZVP(-f)",
                        "def2-TZVPP",
                        "def2-QZVP",
                        "def2-QZVPP",
                    ],
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                "ecp": {
                    "group": "level of theory",
                    "text": "Effective core potentials",
                    "help": (
                        "Whether effective core potentials should be used. "
                        "NOT IMPLEMENTED."
                    ),
                    "values": [None, "def2-ECP"],
                    "default": "def2-ECP",
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): support solvation models (GBSA for
                # XTB, CPCM and SMD)
                "numerical quality": {
                    "help": ("Which numerical quality is desired."),
                    "values": {"Normal": 3, "Good": 4, "Excellent": 5},
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): choose resolution of identity as a
                # on/off tick and pre-select the best approximations in each
                # case. Choose appropriate auxiliary basis sets either based on
                # basis set class, or using AutoAux.
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
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): support the geometric counterpoise
                # method for basis set superposition error (BSSE).
                # TODO(schneiderfelipe): support coordinate manipulation as
                # lists and support fixing coordinates/degrees of freedom
                # ("Geometry constraints").
                "coordinates used": {
                    "tab": "details",
                    "group": "geometry convergence",
                    "help": (
                        "Which coordinates should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Delocalized"],
                },
                "calculate frequencies": {
                    "tab": "details",
                    "group": "geometry convergence",
                    "help": (
                        "Whether a frequencies calculation should be "
                        "done after optimization."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "optimization method": {
                    "tab": "details",
                    "group": "geometry convergence",
                    "help": (
                        "Which optimization method should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Automatic"],
                },
                "maximum number of iterations": {
                    "tab": "details",
                    "group": "geometry convergence",
                    "help": ("Maximum number of iterations."),
                    "widget": Spinbox,
                    "values": range(10, 1001, 10),
                    "default": 100,
                },
                "maximum step": {
                    "tab": "details",
                    "group": "geometry convergence details",
                    "help": ("Maximum step."),
                    "widget": Spinbox,
                    "values": np.arange(0.1, 1.0, 0.05),
                    "default": 0.3,
                },
                "hessian update scheme": {
                    "tab": "details",
                    "group": "geometry convergence details",
                    "help": (
                        "Which Hessian update scheme should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Automatic"],
                },
                # TODO(schneiderfelipe): create a group for restarts in
                # details that support reading a gbw
                "initial hessian": {
                    "tab": "details",
                    "group": "geometry convergence details",
                    "help": (
                        "Which initial model Hessian should be used for "
                        "optimization convergence."
                    ),
                    "values": [
                        "Diagonal",
                        "Almloef",
                        "Lindh",
                        "Swart",
                        "Schlegel",
                        "Read",
                    ],
                    "default": "Almloef",
                },
                # TODO(schneiderfelipe): I don't see the need to set
                # gradient, step and energy convergence criteria specifically
                # if not necessary.
                "convergence criteria": {
                    "tab": "details",
                    "group": "geometry convergence criteria",
                    "help": (
                        "Which convergence criteria should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Loose", "Normal", "Tight", "VeryTight"],
                    "default": "Normal",
                },
                "nuclear model": {
                    "tab": "details",
                    "group": "relativity",
                    "help": (
                        "Which nuclear model should be used in relativistic "
                        "approximations."
                    ),
                    "values": ["Point charge"],
                },
                "Type of excitations": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": ("Which types of excitations to consider."),
                    "values": ["Singlet and triplet"],
                },
                "method": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": ("Which excitation method to use."),
                    "values": ["Davidson"],
                },
                "tda": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "text": "Tamm-Dancoff approximation",
                    "help": (
                        "Whether the Tamm-Dancoff approximation should "
                        "be used."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "velocity representation": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": (
                        "Whether the velocity representation should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "ntos": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "text": "Natural transition orbitals",
                    "help": (
                        "Whether natural transition orbitals should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "rotatory strengths": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": (
                        "Whether rotatory strengths should be calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "quadrupole intensities": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": (
                        "Whether quadrupole intensities should be calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "number of excitations": {
                    "tab": "properties",
                    "group": "electronic excitations",
                    "help": ("Number of excitations to consider."),
                    "widget": Spinbox,
                    "values": range(1, 101),
                },
                "shielding-h": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Shielding for all H atoms",
                    "help": (
                        "Whether shielding for hydrogens should be calculated."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                },
                "shielding-c": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Shielding for all C atoms",
                    "help": (
                        "Whether shielding for carbons should be calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "shielding-p": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Shielding for all P atoms",
                    "help": (
                        "Whether shielding for phosphorus should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "coupling-h": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Spin-spin coupling for all H atoms",
                    "help": (
                        "Whether spin-spin coupling for hydrogens should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "coupling-c": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Spin-spin coupling for all C atoms",
                    "help": (
                        "Whether spin-spin coupling for carbons should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "coupling-p": {
                    "tab": "properties",
                    "group": "nuclear magnetic resonance",
                    "text": "Spin-spin coupling for all P atoms",
                    "help": (
                        "Whether spin-spin coupling for phosphorus should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                # TODO(schneiderfelipe): insert the NBO keyword
                "nbo": {
                    "tab": "properties",
                    "text": "Perform NBO analysis",
                    "help": (
                        "Whether the natural bond orbital analysis should be "
                        "performed."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                # TODO(schneiderfelipe): support output keywords such as
                # LargePrint, PrintBasis and PrintMOs. An option "output level"
                # is also interesting.
                "Wavefunction file": {
                    "tab": "output",
                    "group": "analysis",
                    "help": (
                        "Whether a wavefunction file (WFN) should be created."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
            },
        )

        self.text.grid(
            row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0
        )
        self.questions.grid(
            row=0, column=1, columnspan=2, sticky="nsew", padx=0, pady=0
        )
        self.clear_button.grid(
            row=1, column=1, sticky="nsew", padx=0, pady=self.pady
        )
        self.save_button.grid(
            row=1, column=2, sticky="nsew", padx=0, pady=self.pady
        )

        self.rowconfigure(0, weight=1, minsize=3 * self.column_minsize)
        self.columnconfigure(0, weight=1, minsize=3 * self.column_minsize)

        self.clear_button.bind("<Button-1>", self.questions.init_widgets)
        self.save_button.bind("<Button-1>", self.save)
        for _, var in self.questions.variable.items():
            var.trace("w", self.update_widgets)

        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        """Update input content with currently selected options."""
        v = self.questions.get_values()

        keywords = []
        lines = []

        if v["unrestricted"]:
            if v["theory"] in {"DFTB", "DFT"}:
                keywords.append("UKS")
            else:
                keywords.append("UHF")
        else:
            # TODO(schneiderfelipe): maybe we should omit RKS/RHF
            if v["theory"] in {"DFTB", "DFT"}:
                keywords.append("RKS")
            else:
                keywords.append("RHF")

        keywords.append(v["resolution of identity"])
        keywords.append(v["relativity"])

        if v["theory"] in {"HF", "MP2"}:
            keywords.append(v["theory"])
        if v["theory"] == "DFT":
            keywords.append(v["functional"])
        elif v["theory"] == "DFTB":
            keywords.append(v["hamiltonian"])
        elif v["theory"] == "CCSD":
            kw = v["theory"]
            if v["triples correction"]:
                kw = kw + "(T)"
            if v["dlpno"]:
                kw = "DLPNO-" + kw
            keywords.append(kw)

        keywords.append(v["dispersion"])

        keywords.append(v["basis set"])
        if v["resolution of identity"] in {"RI", "RIJCOSX"}:
            if v["relativity"]:
                keywords.append("SARC/J")
            else:
                keywords.append("def2/J")

        # TODO(schneiderfelipe): this should probably go to the end of the
        # keywords
        if v["resolution of identity"] == "RIJCOSX":
            keywords.append(f"{v['basis set']}/C")
        if v["resolution of identity"] == "RI-JK":
            keywords.append("def2/JK")

        if v["theory"] in {"MP2", "CCSD"}:
            keywords.append(v["frozen core"])

        if v["uco"]:
            keywords.append("UCO")

        if v["numerical frequencies"] and "Freq" in v["task"]:
            v["task"] = v["task"].replace("Freq", "NumFreq")
        keywords.append(v["task"])

        if v["numerical quality"]:
            if v["numerical quality"] > 3:
                if "Opt" in v["task"]:
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
    input_frame = InputGUI(main_window)
    input_frame.pack(fill="both", expand=True)
    main_window.mainloop()
