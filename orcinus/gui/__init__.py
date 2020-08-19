#!/usr/bin/python3

"""Utilities for the graphical user interface."""

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

from orcinus.gui.questionnaire import Questionnaire
from orcinus import ORCAInput


def main():
    """Start the graphical user interface."""
    main_window = Tk()
    # TODO(schneiderfelipe): we need an icon.

    style = Style()
    if style.theme_use() == "default":
        style.theme_use("clam")

    main_window.title(__doc__.split("\n", 1)[0].strip().strip("."))
    input_frame = InputGUI(main_window)
    input_frame.pack(fill="both", expand=True)

    def on_window_close():
        """Proceed to close window."""
        input_frame.store_widgets()
        main_window.destroy()

    main_window.protocol("WM_DELETE_WINDOW", on_window_close)
    main_window.mainloop()


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

    def clear(self, *args, **kwargs):
        """Clear all fields to default values."""
        self.questions.init_widgets(*args, ignore_state=True, **kwargs)

    def store_widgets(self, *args, **kwargs):
        """Store all fields to disk."""
        self.questions.store_widgets(*args, **kwargs)

    def create_widgets(self):
        """Populate object and its widgets."""
        self.text = Text(self)
        self.clear_button = Button(self, text="Clear")
        self.save_button = Button(self, text="Save")
        self.questions = Questionnaire(
            self,
            state_filename=".orcinus_questions.pickle",
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
                    "values": {
                        s: s.replace("+", " ")
                        for s in [
                            "Energy",  # can be done with XTB
                            # "Energy+Gradient",  # can be done with XTB
                            "Opt",  # can be done with XTB
                            "Freq",  # can be done with XTB if numerical
                            "Opt+Freq",  # can be done with XTB if numerical
                            "OptTS",  # can be done with XTB
                            "OptTS+Freq",  # can be done with XTB if numerical
                            "IRC",  # can be done with XTB
                            "OptTS+Freq+IRC",  # can be done with XTB if numerical
                            "NEB",  # can be done with XTB
                            "NEB+Freq",  # can be done with XTB if numerical
                            "NEB+Freq+IRC",  # can be done with XTB if numerical
                            # "Scan",  # can be done with XTB
                            # "MD",  # can be done with XTB
                            # "QM/MM",  # can be done with XTB
                            # "NoIter",  # TODO(schneiderfelipe): should this exist?
                        ]
                    },
                    "default": "Opt+Freq",
                },
                # TODO(schneiderfelipe): implement ts_mode and ts_active_atoms
                # in a very simple way (things will get interestiing when
                # there is a way of selecting atoms on the screen.
                # TODO(schneiderfelipe): implement options for IRC. They are
                # important.
                # TODO(schneiderfelipe): implement access to Z_solver and
                # Z_maxiter in a details group about frequency calculations.
                "charge": {
                    "group": "basic information",
                    "text": "Total charge",
                    "help": ("Net charge of you calculation."),
                    "widget": Spinbox,
                    "values": range(-100, 101),
                    "default": 0,
                },
                "spin": {
                    "group": "basic information",
                    "text": "Spin multiplicity",
                    "help": ("Spin multiplicity of you calculation."),
                    "widget": Spinbox,
                    "values": range(1, 101),
                    "switch": lambda k: k["unrestricted"],
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
                    "switch": lambda k: k["unrestricted"],
                },
                # TODO(schneiderfelipe): give some support for broken
                # symmetry (BS-DFT).
                # TODO(schneiderfelipe): this should go to the broadest
                # possible category, above even task.
                "theory": {  # TODO(schneiderfelipe): use a better name
                    "group": "level of theory",
                    "help": ("Class of calculation."),
                    "values": ["MM", "HF", "DFTB", "DFT", "MP2", "CCSD"],
                    "default": "DFT",
                },
                # TODO(schneiderfelipe): the frozen core approximation can be
                # tuned with things such as energy window or electron
                # counting, but the defaults should be very reliable.
                # TODO(schneiderfelipe): properly select NoFrozenCore it when
                # e.g. MP2 Freq.
                "frozen core": {
                    "group": "level of theory",
                    "help": (
                        "Whether the frozen core approximation should be "
                        "used."
                    ),
                    "widget": Checkbutton,
                    # TODO(schneiderfelipe): I am assuming FrozenCore is always
                    # default.
                    # TODO(schneiderfelipe): the def2/C, etc. basis sets were
                    # optimized for FrozenCore calculations. As such,
                    # NoFrozenCore must enforce AutoAux!
                    "values": {True: None, False: "NoFrozenCore"},
                    "switch": lambda k: k["theory"] in {"MP2", "CCSD"},
                },
                "triples correction": {
                    "group": "level of theory",
                    "help": (
                        "Whether perturbative triples correction should "
                        "be calculated used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": lambda k: k["theory"] == "CCSD",
                },
                "dftb:hamiltonian": {
                    "group": "level of theory",
                    "text": "DFTB Hamiltonian",
                    "help": ("Which model Hamiltonian should be used."),
                    "values": {"GFN1-xTB": "XTB1", "GFN2-xTB": "XTB2"},
                    "default": "GFN2-xTB",
                    "switch": lambda k: k["theory"] == "DFTB",
                },
                "dft:family": {
                    "group": "level of theory",
                    "text": "Density functional family",
                    "help": (
                        "Which density functional family should be " "used."
                    ),
                    "values": {
                        s: s.lower()
                        for s in [
                            "LDA",
                            "GGA",
                            "meta-GGA",
                            "Hybrid",
                            "RS-Hybrid",
                            "meta-Hybrid",
                            "Double-Hybrid",
                            "RS-Double-Hybrid",
                        ]
                    },
                    "default": "GGA",
                    "switch": lambda k: k["theory"] == "DFT",
                },
                "dft:lda": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": ["HFS", "VWN5", "VWN3", "PWLDA"],
                    "default": "VWN5",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "LDA",
                },
                "dft:gga": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": [
                        "BP86",
                        "BLYP",
                        "OLYP",
                        "GLYP",
                        "XLYP",
                        "PW91",
                        "mPWPW",
                        "mPWLYP",
                        "PBE",
                        "rPBE",
                        "revPBE",
                        "PWP",
                        # "B97",
                    ],
                    "default": "BLYP",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "GGA",
                },
                "dft:hybrid": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": [
                        "B1LYP",
                        "B3LYP",
                        "B3LYP/G",  # same as in Gaussian
                        "O3LYP",
                        "X3LYP",
                        "B1P",
                        "B3P",
                        "B3PW",
                        "PW1PW",
                        "mPW1PW",
                        "mPW1LYP",
                        "PBE0",
                        "PW6B95",
                        "BHandHLYP",
                    ],
                    "default": "B3LYP",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "Hybrid",
                },
                "dft:meta-gga": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": [
                        "TPSS",
                        "M06L",
                        "B97M-V",
                        "B97M-D3BJ",
                        "SCANfunc",
                    ],
                    "default": "SCANfunc",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "meta-GGA",
                },
                "dft:meta-hybrid": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": ["TPSSh", "TPSS0", "M06", "M062X"],
                    "default": "TPSSh",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "meta-Hybrid",
                },
                "dft:rs-hybrid": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": [
                        "wB97",
                        "wB97X",
                        "wB97X-D3",
                        "wB97X-V",
                        "wB97X-D3BJ",
                        "wB97M-V",
                        "wB97M-D3BJ",
                        "CAM-B3LYP" "LC-BLYP",
                    ],
                    "default": "wB97X",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "RS-Hybrid",
                },
                "dft:double-hybrid": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": [
                        "B2PLYP",
                        "B2PLYP-D",
                        "B2PLYP-D3",
                        "mPW2PLYP",
                        "mPW2PLYP-D",
                        "B2GP-PLYP",
                        "B2K-PLYP",
                        "B2T-PLYP",
                        "PWPB95",
                        "DSD-BLYP",
                        "DSD-PBEP86",
                        "DSD-PBEB95",
                    ],
                    "default": "B2PLYP",
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "Double-Hybrid",
                },
                "dft:rs-double-hybrid": {
                    "group": "level of theory",
                    "text": "Density functional",
                    "help": ("Which density functional should be used."),
                    "values": ["wB2PLYP", "wB2GP-PLYP"],
                    "switch": lambda k: k["theory"] == "DFT"
                    and k["dft:family"] == "RS-Double-Hybrid",
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
                    "switch": lambda k: k["theory"] == "DFT",
                },
                # TODO(schneiderfelipe): create a details group for SCF
                # convergence things such as solvers (e.g. DIIS, KDIIS,
                # MORead), initial guesses (e.g, PModel, Hueckel), etc.. It
                # is also nice to allow a stability analysis of the SCF
                # wavefunction. In the future I also want to implement
                # options for rotating orbitals.
                # TODO(schneiderfelipe): some nice options for avoiding linear
                # dependency problems are required in a special group for SCF
                # convergence.
                # TODO(schneiderfelipe): give support for other families such
                # as ano (they also have aug-cc, ma-def2 and saug-ano/aug-ano).
                # TODO(schneiderfelipe): extrapolation techniques are
                # interesting for single point calculations with DLPNO-CC
                # methods.
                "basis:family": {
                    "group": "level of theory",
                    "text": "Basis set family",
                    "help": ("Which basis set family should be employed."),
                    "values": {s: s.lower() for s in ["def2", "cc", "Pople"]},
                    "switch": lambda k: k["theory"]
                    in {"HF", "DFT", "MP2", "CCSD"},
                },
                "basis:def2": {
                    "group": "level of theory",
                    "text": "Basis set quality",
                    "help": ("Which basis set should be used."),
                    "values": {
                        "DZ(P)": "def2-SV(P)",
                        "DZ(P)D": "ma-def2-SV(P)",
                        "DZP": "def2-SVP",
                        "DZPD": "ma-def2-SVP",
                        "TZP(-f)": "def2-TZVP(-f)",
                        "TZP(-f)D": "ma-def2-TZVP(-f)",
                        "TZP": "def2-TZVP",
                        "TZPD": "ma-def2-TZVP",
                        "TZPP": "def2-TZVPP",
                        "TZPPD": "ma-def2-TZVPP",
                        "QZP": "def2-QZVP",
                        "QZPP": "def2-QZVPP",
                        "QZPPD": "ma-def2-QZVPP",
                    },
                    "default": "TZP",
                    "switch": lambda k: k["basis:family"] == "def2"
                    and k["theory"] in {"HF", "DFT", "MP2", "CCSD"},
                },
                "basis:cc": {
                    "group": "level of theory",
                    "text": "Basis set quality",
                    "help": ("Which basis set should be used."),
                    "values": {
                        "DZP": "cc-pVDZ",
                        "DZPD": "aug-cc-pVDZ",
                        "TZP": "cc-pVTZ",
                        "TZPD": "aug-cc-pVTZ",
                        "QZP": "cc-pVQZ",
                        "QZPD": "aug-cc-pVQZ",
                        "5ZP": "cc-pV5Z",
                        "5ZPD": "aug-cc-pV5Z",
                        "6ZP": "cc-pV6Z",
                        "6ZPD": "aug-cc-pV6Z",
                    },
                    # TODO(schneiderfelipe): this should probably change!
                    "default": "TZP",
                    "switch": lambda k: k["basis:family"] == "cc"
                    and k["theory"] in {"HF", "DFT", "MP2", "CCSD"},
                },
                "basis:pople": {
                    "group": "level of theory",
                    "text": "Basis set quality",
                    "help": ("Which basis set should be used."),
                    "values": {
                        # "M": "STO-3G",
                        # "M(P)": "STO-3G*",
                        "DZ": "6-31G",
                        "DZ(P)": "6-31G(d)",
                        "DZP": "6-31G(d,p)",
                        # "DZ(D)": "6-31+G",
                        # "DZ(PD)": "6-31+G(d)",
                        "DZP(D)": "6-31+G(d,p)",
                        "DZPD": "6-31++G(d,p)",
                        "TZ": "6-311G",
                        "TZ(P)": "6-311G(2df)",
                        "TZP": "6-311G(2df,2pd)",
                        # "TZ(D)": "6-311+G",
                        # "TZ(PD)": "6-311+G(2df)",
                        "TZP(D)": "6-311+G(2df,2pd)",
                        "TZPD": "6-311++G(2df,2pd)",
                    },
                    "default": "TZP",
                    "switch": lambda k: k["basis:family"] == "Pople"
                    and k["theory"] in {"HF", "DFT", "MP2", "CCSD"},
                },
                # TODO(schneiderfelipe): implement a details group for basis
                # sets and implement basis set decontraction there (e.g.,
                # DecontractAux [useful for reducing RI error for core
                # properties, etc.], etc.). Also implement a forceful AutoAux
                # flag, which is sometimes useful for checking auxiliary basis
                # set dependencies.
                "numerical:quality": {
                    "text": "Numerical quality",
                    "help": (
                        "Which numerical quality is desired. Good is "
                        "defined as enough to avoid imaginary "
                        "frequencies due to numerical noise, but you "
                        "might need more than that."
                    ),
                    "values": {
                        "Poor": -1,
                        "Fair": 0,
                        "Good": 1,
                        "Very Good": 2,
                        "Excellent": 3,
                        "Extreme": 4,
                    },
                    "default": "Good",
                    "switch": lambda k: k["theory"]
                    in {"HF", "DFT", "MP2", "CCSD"},
                },
                # TODO(schneiderfelipe): the acceleration section must contain
                # only things that make calculations fast without changing
                # accuracy.
                "dlpno": {
                    "group": "acceleration",
                    "text": "DLPNO",
                    "help": (
                        "Whether the domain-based local pair natural "
                        "orbital approximation should be used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": lambda k: (
                        k["theory"] in {"MP2", "CCSD"}
                        or (
                            k["theory"] == "DFT"
                            and "Double-Hybrid" in k["dft:family"]
                        )
                    ),
                },
                "ri": {
                    "group": "acceleration",
                    "text": "Resolution of identity",
                    "help": (
                        "Whether the resolution of identity approximation "
                        "should be used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": lambda k: (
                        k["theory"] == "HF"
                        or (
                            k["theory"] in {"MP2", "CCSD"} and not k["dlpno"]
                        )  # TODO(schneiderfelipe): this should probably also include double-hybrids
                        or (
                            k["theory"] == "DFT"
                            and (
                                "GGA" in k["dft:family"]
                                or "Hybrid" in k["dft:family"]
                            )
                        )
                    ),
                },
                # "For HF, the use of RI-JK with AutoAux is beneficial only for
                # fairly small systems (less than 200 electrons) with large
                # basis sets (at least triple-ζ quality)."
                # (doi:10.1021/acs.jctc.6b01041).
                "ri:hf": {
                    "group": "acceleration",
                    "text": "Resolution of identity",
                    "help": (
                        "Whether a resolution of identity approximation "
                        "should be used."
                    ),
                    "values": {
                        # None: "NoRI",  # HF: Exact J + exact K: no auxiliary functions and no grids needed.
                        # Hybrid DFT: Exact J + exact K + GGA-XC: no auxiliary functions needed, DFT grid controlled by the GRID keyword.
                        # "Auto": "Auto",
                        #
                        # RIJDX seems like a synonym for RIJONX
                        "RIJONX": "RIJONX",  # HF: RIJ + exact K: <basis>/ J auxiliaries, no grids.
                        # Hybrid DFT: RIJ + exact K + GGA-XC: <basis>/ J auxiliaries, DFT grid controlled by the GRID keyword.
                        "RIJK": "RIJK",  # HF: RIJ + RIK = RIJK: <basis>/JK auxiliaries, no grids.
                        # Hybrid DFT: RIJ + RIK + GGA-XC: <basis>/ JK auxiliaries, DFT grid controlled by the GRID keyword.
                        "RIJCOSX": "RIJCOSX",  # HF: RIJ + COSX: <basis>/ J auxiliaries, COSX grid controlled by the GRIDX keyword.
                        # Hybrid DFT: RIJ + COSX + GGA-XC: <basis>/ J auxiliaries, COSX grid controlled by the GRIDX keyword, DFT grid controlled by the GRID keyword.
                    },
                    "default": "RIJCOSX",
                    "switch": lambda k: (k["ri"] or k["dlpno"])
                    and (
                        k["theory"] in {"HF", "MP2", "CCSD"}
                        or (
                            k["theory"] == "DFT"
                            and "Hybrid" in k["dft:family"]
                        )
                    ),
                },
                "nprocs": {
                    "group": "acceleration",
                    "text": "Number of processes",
                    "help": ("Number of parallel processes to use."),
                    "widget": Spinbox,
                    "values": [2 ** n for n in range(6)],
                    "default": 6,
                },
                "memory": {
                    "group": "acceleration",
                    "text": "Total memory",
                    "help": ("How much memory to use in total."),
                    "widget": Spinbox,
                    "values": np.arange(6000, 18001, 500),
                    "default": 12000,
                },
                # TODO(schneiderfelipe): cavity construction in continuum
                # solvation is also something that oftentimes produce
                # imaginary frequencies. As such, options on that are also
                # necessary.
                # TODO(schneiderfelipe): continuum solvation models are very
                # important, in particular also parameters for cavity
                # definition such as GEPOL, SES/SAS and atomic radii. But
                # don't be too boring.
                "solvation": {
                    "help": ("Whether implicit solvation should be used."),
                    "widget": Checkbutton,
                    "default": True,
                },
                "solvation:model": {
                    "text": "Solvation model",
                    "help": ("Which solvent model should be used."),
                    "values": ["CPCM", "SMD"],
                    "default": "SMD",
                    "switch": lambda k: k["solvation"]
                    and k["theory"] != "DFTB",
                },
                "solvation:cpcm": {
                    "text": "Solvent",
                    "help": ("Which solvent should be considered."),
                    "values": {
                        "Water": "Water",  # ε = 80.4
                        "Dimethyl sulfoxide": "DMSO",  # ε = 47.2
                        "Dimethylformamide": "DMF",  # ε = 38.3
                        "Acetonitrile": "Acetonitrile",  # ε = 36.6
                        "Methanol": "Methanol",  # ε = 32.63
                        "Ethanol": "Ethanol",  # ε = 24.3
                        "Ammonia": "Ammonia",  # ε = 22.4
                        "Acetone": "Acetone",  # ε = 20.7
                        "Pyridine": "Pyridine",  # ε = 12.5
                        "1-Octanol": "Octanol",  # ε = 10.30
                        "Dichloromethane": "CH2Cl2",  # ε = 9.08
                        "Tetrahydrofuran": "THF",  # ε = 7.25
                        "Chloroform": "Chloroform",  # ε = 4.9
                        "Toluene": "Toluene",  # ε = 2.4
                        "Benzene": "Benzene",  # ε = 2.3
                        "Tetrachloromethane": "CCl4",  # ε = 2.24
                        "Cyclohexane": "Cyclohexane",  # ε = 2.02
                        "n-Hexane": "Hexane",  # ε = 1.89
                    },
                    "default": "Water",
                    "switch": lambda k: k["solvation"]
                    and k["theory"] != "DFTB"
                    and k["solvation:model"] == "CPCM",
                },
                "solvation:smd": {
                    "text": "Solvent",
                    "help": ("Which solvent should be considered."),
                    "values": {
                        "Water": "Water",  # ε = 80.4
                        "Dimethyl sulfoxide": "DMSO",  # ε = 47.2
                        "Dimethylformamide": "DMF",  # ε = 38.3
                        "Acetonitrile": "Acetonitrile",  # ε = 36.6
                        "Nitromethane": "Nitromethane",  # ε = 35.87
                        "Nitrobenzene": "Nitrobenzene",  # ε = 34.82
                        "Methanol": "Methanol",  # ε = 32.63
                        "Ethanol": "Ethanol",  # ε = 24.3
                        "Acetone": "Acetone",  # ε = 20.7
                        "Pyridine": "Pyridine",  # ε = 12.5
                        "1-Octanol": "1-Octanol",  # ε = 10.30
                        "Dichloromethane": "Dichloromethane",  # ε = 9.08
                        "Tetrahydrofuran": "THF",  # ε = 7.25
                        "Chloroform": "Chloroform",  # ε = 4.9
                        "Diethyl ether": "Diethyl ether",  # ε = 4.3
                        "Carbon disulfide": "Carbon disulfide",  # ε = 2.641
                        "Toluene": "Toluene",  # ε = 2.4
                        "Benzene": "Benzene",  # ε = 2.3
                        "Tetrachloromethane": "CCl4",  # ε = 2.24
                        "Cyclohexane": "Cyclohexane",  # ε = 2.02
                        "n-Hexane": "n-Hexane",  # ε = 1.89
                        # TODO(schneiderfelipe): complete this list!
                    },
                    "default": "Water",
                    "switch": lambda k: k["solvation"]
                    and k["theory"] != "DFTB"
                    and k["solvation:model"] == "SMD",
                },
                "solvation:gbsa": {
                    "text": "Solvent",
                    "help": ("Which solvent should be considered."),
                    "values": {
                        "Water": "Water",  # ε = 80.4
                        "Dimethyl sulfoxide": "DMSO",  # ε = 47.2
                        "Dimethylformamide": "DMF",  # ε = 38.3, unavailable in GFN1-xTB
                        "Acetonitrile": "Acetonitrile",  # ε = 36.6
                        "Methanol": "Methanol",  # ε = 32.63
                        "Acetone": "Acetone",  # ε = 20.7
                        "Dichloromethane": "CH2Cl2",  # ε = 9.08
                        "Tetrahydrofuran": "THF",  # ε = 7.25
                        "Chloroform": "CHCl3",  # ε = 4.9
                        "Diethyl ether": "Ether",  # ε = 4.3
                        "Carbon disulfide": "CS2",  # ε = 2.641
                        "Toluene": "Toluene",  # ε = 2.4
                        "Benzene": "Benzene",  # ε = 2.3
                        "n-Hexane": "n-Hexan",  # ε = 1.89, unavailable in GFN1-xTB
                    },
                    "default": "Water",
                    "switch": lambda k: k["solvation"]
                    and k["theory"] == "DFTB",
                },
                # TODO(schneiderfelipe): switch to basis sets consistent with
                # relativistic approximations.
                "relativity": {
                    # "group": "level of theory",
                    "text": "Scalar relativistic approximation",
                    "help": (
                        "Which scalar relativistic approximation should be "
                        "used."
                    ),
                    "values": [None, "DKH", "ZORA"],
                    "switch": lambda k: k["theory"]
                    in {"HF", "DFT", "MP2", "CCSD"},
                },
                # TODO(schneiderfelipe): the 1-center approximation option is
                # relevant to calculations using ZORA.
                "spin-orbit coupling": {
                    # "group": "level of theory",
                    "help": (
                        "Whether spin-orbit coupling should be taken into "
                        "account."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                    "switch": lambda k: k["theory"] != "DFTB",
                },
                "ecp": {
                    # "group": "level of theory",
                    "text": "Effective core potentials",
                    "help": (
                        "Whether effective core potentials should be used. "
                        "NOT IMPLEMENTED."
                    ),
                    # TODO(schneiderfelipe): this requires a good
                    # implementation, which I think can improve costly
                    # calculations with heavy atoms. I also want to ensure
                    # nice compatibility between basis sets and ECPs.
                    # TODO(schneiderfelipe): this is a case where "Auto" makes
                    # sense, since leaving it unspecified might trigger the
                    # default set of ECPs as of ORCA 4+. Whenever this is the
                    # case, say it in the help.
                    "values": [None, "def2-ECP"],
                    "default": "def2-ECP",
                    "switch": lambda k: k["theory"]
                    in {"HF", "DFT", "MP2", "CCSD"},
                },
                "excited states": {
                    "tab": "properties",
                    "text": "Excited states calculation",
                    "help": ("Whether excited states should be calculated."),
                    "widget": Checkbutton,
                    "default": False,
                },
                # TODO(schneiderfelipe): support RAMAN/IR and related stuff.
                # Raman requires polazirabilities ("%elprop Polar 1 end") and
                # may only work with numerical frequencies (please check). See
                # <https://sites.google.com/site/orcainputlibrary/vibrational-frequencies>.
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
                "scf:maxiter": {
                    "tab": "details",
                    "group": "self consistent field",
                    "text": "Maximum number of iterations",
                    "help": (
                        "Maximum number of self consistent field "
                        "iterations."
                    ),
                    "widget": Spinbox,
                    "values": ["Auto"] + list(range(100, 501, 50)),
                },
                # TODO(schneiderfelipe): support the geometric counterpoise
                # method for basis set superposition error (BSSE). This should
                # appear disabled for unavailable cases such as
                # nonparameterized basis set, etc. Tell what is available in
                # the help.
                # TODO(schneiderfelipe): support coordinate manipulation as
                # lists and support fixing coordinates/degrees of freedom
                # ("Geometry constraints").
                # TODO(schneiderfelipe): the following should support things
                # like "COpt" in place of "Opt" for fixing bad internal
                # coordinates (sometimes molecules explode due to that).
                "geom:step": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "text": "Optimization method",
                    "help": (
                        "Which optimization method should be used for "
                        "optimization convergence. 'Rational function' is "
                        "probably the best method for minimization (followed "
                        "by 'quasi-Newton') and 'partitioned Rational "
                        "function' is probably the best method for "
                        "transition state optimizations. Those probably best "
                        "are the defaults ('Auto')."
                    ),
                    "values": {
                        "Auto": None,
                        "Rational function": "step rfo",
                        "partitioned Rational function": "step prfo",
                        "quasi-Newton": "step qn",
                        "GDIIS": "step gdiis",
                    },
                    "switch": lambda k: "Opt" in k["task"],
                },
                "geom:trust": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "text": "Trust radius",
                    "help": (
                        "Maximum geometry optimization step to take. "
                        "Some tests showed that 0.2 is probably best "
                        "when updating trust radii."
                    ),
                    "widget": Spinbox,
                    "values": np.arange(0.1, 0.51, 0.05),
                    "default": 0.2,
                    "switch": lambda k: "Opt" in k["task"],
                },
                "geom:update_trust": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "text": "Update trust radius",
                    "help": (
                        "Whether to update the maximum geometry "
                        "optimization step."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    # TODO(schneiderfelipe): I know trust radius update works
                    # with RFO (I've tested) and I am pretty sure that it works
                    # with PRFO (because the manual suggests using the update
                    # for OptTS). I definitely know the update does not work
                    # with QN (I tested and got segfault; ORCA forum says
                    # allowing this option would be a "conceptual bug"). I am
                    # not sure about GDIIS (I believe the value gets ignored,
                    # but I am not sure).
                    "switch": lambda k: "Opt" in k["task"]
                    and k["geom:step"] != "quasi-Newton",
                },
                "coordinates used": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "help": (
                        "Which coordinates should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Delocalized"],
                    "switch": lambda k: "Opt" in k["task"],
                },
                "calculate frequencies": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "help": (
                        "Whether a frequencies calculation should be "
                        "done after optimization."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                    "switch": lambda k: "Opt" in k["task"],
                },
                "geom:maxiter": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "text": "Maximum number of iterations",
                    "help": (
                        "Maximum number of geometry optimization "
                        "iterations."
                    ),
                    "widget": Spinbox,
                    "values": list(range(30, 301, 10)),
                    "switch": lambda k: "Opt" in k["task"],
                },
                "geom:tight": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "text": "Tight geometry optimization",
                    "help": (
                        "Whether a tight geometry optimization should be done."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                    "switch": lambda k: "Opt" in k["task"],
                },
                "hessian update scheme": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "help": (
                        "Which Hessian update scheme should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Auto", "BFGS", "Bofill", "Powell"],
                    "switch": lambda k: "Opt" in k["task"],
                },
                # TODO(schneiderfelipe): create a group for restarts in
                # details that support reading a gbw
                "initial hessian": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "help": (
                        "Which initial model Hessian should be used for "
                        "optimization convergence. 'Swart' is probably the "
                        "best option, followed by 'Lindh' and 'Almlöf'."
                    ),
                    "values": {
                        "Read": "inhess read",
                        "Calculate": "calc_hess true",
                        "Swart": "inhess swart",
                        "Lindh": "inhess lindh",
                        "Almlöf": "inhess almloef",
                        "Schlegel": "inhess schlegel",
                        "Diagonal": "inhess unit",
                    },
                    "default": "Swart",
                    "switch": lambda k: "Opt" in k["task"],
                },
                # TODO(schneiderfelipe): I don't see the need to set
                # gradient, step and energy convergence criteria specifically
                # if not necessary.
                "convergence criteria": {
                    "tab": "details",
                    "group": "geometry optimization",
                    "help": (
                        "Which convergence criteria should be used for "
                        "optimization convergence."
                    ),
                    "values": ["Loose", "Normal", "Tight", "VeryTight"],
                    "default": "Normal",
                    "switch": lambda k: "Opt" in k["task"],
                },
                "freq:restart": {
                    "tab": "details",
                    "group": "frequencies",
                    "text": "Restart frequencies calculation",
                    "help": (
                        "Whether a frequencies calculation should be "
                        "restarted."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                "freq:scaling": {
                    "tab": "details",
                    "group": "frequencies",
                    "text": "Frequency scaling",
                    "help": ("Number to multiply all your frequency values."),
                    "widget": Spinbox,
                    "values": np.arange(0.95, 1.051, 0.01),
                    "default": 1.0,
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
                "excited states:method": {
                    "tab": "details",
                    "group": "excited states calculation",
                    "text": "Excited states calculation method",
                    "help": ("Which excitation method to use."),
                    "values": ["TD-DFT"],
                    "switch": lambda k: k["excited states"],
                },
                "tddft:nroots": {
                    "tab": "details",
                    "group": "excited states calculation",
                    "text": "Number of excited states",
                    "help": ("Number of excited states to consider."),
                    "widget": Spinbox,
                    "values": range(1, 101),
                    "default": 30,
                    "switch": lambda k: k["excited states"]
                    and k["excited states:method"] == "TD-DFT",
                },
                "tddft:tda": {
                    "tab": "details",
                    "group": "excited states calculation",
                    "text": "Tamm-Dancoff approximation",
                    "help": (
                        "Whether the Tamm-Dancoff approximation should "
                        "be used."
                    ),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": lambda k: k["excited states"]
                    and k["excited states:method"] == "TD-DFT",
                },
                "tddft:nto": {
                    "tab": "details",
                    "group": "excited states calculation",
                    "text": "Natural transition orbitals",
                    "help": (
                        "Whether natural transition orbitals should be "
                        "calculated."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                    "switch": lambda k: k["excited states"]
                    and k["excited states:method"] == "TD-DFT",
                },
                "tddft:maxdim": {
                    "tab": "details",
                    "group": "excited states calculation",
                    "text": "Davidson expansion space",
                    "help": ("Size of the Davidson expansion space."),
                    "widget": Spinbox,
                    "values": range(2, 361),
                    "default": 10,
                    "switch": lambda k: k["excited states"]
                    and k["excited states:method"] == "TD-DFT",
                },
                # "Type of excitations": {
                #     "tab": "details",
                #     "group": "excited states calculation",
                #     "help": ("Which types of excitations to consider."),
                #     "values": ["Singlet and triplet"],
                #     "switch": lambda k: k["excited states"]
                #     and k["excited states:method"] == "TD-DFT",
                # },
                # "velocity representation": {
                #     "tab": "details",
                #     "group": "excited states calculation",
                #     "help": (
                #         "Whether the velocity representation should be "
                #         "calculated."
                #     ),
                #     "widget": Checkbutton,
                #     "default": False,
                #     "switch": lambda k: k["excited states"]
                #     and k["excited states:method"] == "TD-DFT",
                # },
                # "rotatory strengths": {
                #     "tab": "details",
                #     "group": "excited states calculation",
                #     "help": (
                #         "Whether rotatory strengths should be calculated."
                #     ),
                #     "widget": Checkbutton,
                #     "default": False,
                #     "switch": lambda k: k["excited states"]
                #     and k["excited states:method"] == "TD-DFT",
                # },
                # "quadrupole intensities": {
                #     "tab": "details",
                #     "group": "excited states calculation",
                #     "help": (
                #         "Whether quadrupole intensities should be "
                #         "calculated."
                #     ),
                #     "widget": Checkbutton,
                #     "default": False,
                #     "switch": lambda k: k["excited states"]
                #     and k["excited states:method"] == "TD-DFT",
                # },
                # TODO(schneiderfelipe): support output keywords such as
                # PrintBasis and PrintMOs.
                "output:level": {
                    "tab": "output",
                    "text": "Output level",
                    "help": ("How much output should be created."),
                    "values": {
                        # "Auto": None,
                        "Mini": "MiniPrint",
                        "Small": "SmallPrint",
                        "Normal": "NormalPrint",
                        "Large": "LargePrint",
                    },
                    "default": "Small",
                },
                "output:mos": {
                    "tab": "output",
                    "text": "Print molecular orbitals",
                    "help": ("Whether molecular orbitals should be printed."),
                    "widget": Checkbutton,
                    "default": True,
                },
                "output:basis": {
                    "tab": "output",
                    "text": "Print basis sets",
                    "help": ("Whether basis sets should be printed."),
                    "widget": Checkbutton,
                    "default": True,
                    "switch": lambda k: k["output:level"] != "Large",
                },
                "wavefunction file": {
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
        self.columnconfigure(0, weight=1, minsize=4 * self.column_minsize)

        self.clear_button.bind("<Button-1>", self.clear)
        self.save_button.bind("<Button-1>", self.save)
        for _, var in self.questions.variable.items():
            var.trace("w", self.update_widgets)

        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        """Update input content with currently selected options."""
        v = self.questions.get_values()
        inp = ORCAInput()

        if not v["spin"]:
            v["spin"] = 1

        inp["*"] = ["xyzfile", v["charge"], v["spin"], "init.xyz"]

        if v["unrestricted"]:
            if v["theory"] in {"DFTB", "DFT"}:
                inp["!"].append("UKS")
            else:
                inp["!"].append("UHF")
        # else:
        #     if v["theory"] in {"DFTB", "DFT"}:
        #         inp["!"].append("RKS")
        #     else:
        #         inp["!"].append("RHF")

        ri = None
        if v["theory"] != "DFTB":
            if not v["ri"] and not v["dlpno"]:
                ri = "NoRI"
            elif v["theory"] == "DFT" and "gga" in v["dft:family"]:
                ri = "RI"
            elif v["ri:hf"] and v["ri:hf"] != "Auto":
                ri = v["ri:hf"]

        use_auxj = False
        use_auxjk = False
        use_auxc = False
        if ri in {"RI", "RIJONX", "RIJDX", "RIJCOSX"}:
            use_auxj = True
        elif ri == "RIJK":
            use_auxjk = True

        theory = v["theory"]
        if v["theory"] == "DFTB":
            theory = v["dftb:hamiltonian"]
        elif v["theory"] == "DFT":
            theory = v[f"dft:{v['dft:family']}"]

        if theory in {"MP2", "CCSD"} or (
            v["theory"] == "DFT" and "double-hybrid" in v["dft:family"]
        ):
            if v["dlpno"]:
                theory = "DLPNO-" + theory
                use_auxc = True
            elif ri and ri not in {None, "NoRI"}:
                theory = "RI-" + theory
                use_auxc = True

        if v["theory"] == "CCSD":
            if v["triples correction"]:
                theory = theory + "(T)"

        use_numfreq = False
        if (
            v["relativity"]
            or ri == "RIJK"
            or v["theory"] == "DFTB"
            or (
                v["theory"] == "DFT"
                and (
                    "meta-gga" in v["dft:family"]
                    or "double-hybrid" in v["dft:family"]
                )
            )
        ):
            use_numfreq = True

        use_numgrad = False
        if v["theory"] == "CCSD":
            use_numgrad = True

        inp["!"].append(theory)
        inp["!"].append(v["dispersion"])
        inp["!"].append(v["relativity"])
        if v["theory"] != "DFTB":
            inp["!"].append(v[f"basis:{v['basis:family']}"])

        inp["!"].append(ri)
        if ri != "NoRI":
            auxbas = set()
            if use_auxj:
                if v["basis:family"] == "def2":
                    if not v["relativity"]:
                        auxbas.add("def2/J")
                    else:
                        # TODO(schneiderfelipe): this will move from here as
                        # the special basis for relativistic calculations get
                        # automatically specified (currently we accept e.g.
                        # def2-TZVP as is, which is not wanted).
                        auxbas.add("SARC/J")
                else:
                    auxbas.add("AutoAux")

            if use_auxjk:
                if v["basis:family"] == "def2":
                    auxbas.add("def2/JK")
                elif v["basis:family"] == "cc":
                    if v["basis:cc"] in {
                        f"{prefix}cc-pV{n}Z"
                        for n in {"T", "Q", 5}
                        for prefix in {"", "aug-"}
                    }:
                        auxbas.add(f"{v['basis:cc']}/JK")
                    else:
                        auxbas.add("AutoAux")
                else:
                    auxbas.add("AutoAux")

            if use_auxc:
                if v["basis:family"] == "def2":
                    if v["basis:def2"] in {
                        "def2-SVP",
                        "def2-TZVP",
                        "def2-TZVPP",
                        "def2-QZVPP",
                    }:
                        auxbas.add(f"{v['basis:def2']}/C")
                    else:
                        auxbas.add("AutoAux")
                elif v["basis:family"] == "cc":
                    if v["basis:cc"] in {
                        f"{prefix}cc-pV{n}Z"
                        for prefix in {"", "aug-"}
                        for n in {"D", "T", "Q", 5, 6}
                    }:
                        auxbas.add(f"{v['basis:cc']}/C")
                    else:
                        auxbas.add("AutoAux")
                else:
                    auxbas.add("AutoAux")

            if "AutoAux" in auxbas:
                inp["!"].append("AutoAux")
            else:
                inp["!"].extend(sorted(auxbas))

        if v["theory"] in {"MP2", "CCSD"}:
            inp["!"].append(v["frozen core"])

        inp["!"].append(v["uco"])

        task = v["task"]
        if use_numgrad and "Opt" in task:
            task = task.replace("Opt", "Opt NumGrad")
        if use_numfreq and "Freq" in task:
            task = task.replace("Freq", "NumFreq")

        if task != "Energy":
            inp["!"].append(task)

        inp["maxcore"].append(int(v["memory"] / v["nprocs"]))

        if v["solvation"]:
            if v["theory"] == "DFTB":
                solvation_model = "gbsa"
            else:
                solvation_model = v["solvation:model"].lower()
            solvent = v[f"solvation:{solvation_model}"].lower()

            if solvation_model == "cpcm":
                inp["!"].append(f"CPCM({solvent})")
            else:
                inp["cpcm"].append("smd true")
                inp["cpcm"].append(f'smdsolvent "{solvent}"')

        if v["geom:tight"]:
            inp["!"].append("TightOpt")

        if v["numerical:quality"]:
            inp["!"].append(
                {
                    -1: "LooseSCF",
                    1: "TightSCF",
                    2: "TightSCF",
                    3: "VeryTightSCF",
                    4: "ExtremeSCF",
                }[v["numerical:quality"]]
            )

        if v["theory"] == "DFT":
            n_grid = v["numerical:quality"] + 3
            if v["excited states:method"] == "TD-DFT":
                n_grid += 1
            # TODO(schneiderfelipe): NOCV and other similar property
            # calculations require the following:
            #
            #     n_grid += 1
            #
            # (i.e., at least Grid5 to be good).
            inp["!"].append(f"Grid{n_grid}")
            if n_grid > 6:
                inp["!"].append("NoFinalGrid")
            else:
                inp["!"].append(f"FinalGrid{n_grid + 1}")
        if ri == "RIJCOSX":
            n_gridx = v["numerical:quality"] + 3
            if "Opt" in task and "DLPNO-MP2" in theory:
                n_gridx += 3
            # TODO(schneiderfelipe): GIAO/NMR and EPR calculations may require
            # the following:
            #
            #     n_gridx += 2
            #
            # (i.e., at least GridX6 to be good).
            elif v["excited states:method"] == "TD-DFT":
                n_gridx += 1
            if n_gridx > 3:
                inp["!"].append(f"GridX{min(n_gridx, 9)}")

        if v["output:level"] != "SmallPrint":
            inp["!"].append(v["output:level"])
        if v["output:basis"] and v["output:level"] != "LargePrint":
            inp["!"].append("PrintBasis")
        if v["output:mos"] and v["output:level"] != "LargePrint":
            inp["!"].append("PrintMOs")
        elif not v["output:mos"] and v["output:level"] == "LargePrint":
            inp["!"].append("NoPrintMOs")
        if v["nbo"]:
            inp["!"].append("NBO")

        if v["short description"]:
            inp["#"].append(f"{v['short description']}")

        if v["scf:maxiter"] and v["scf:maxiter"] != "Auto":
            inp["scf"].append(f"maxiter {v['scf:maxiter']}")
        if v["geom:maxiter"] and v["geom:maxiter"] != "Auto":
            inp["geom"].append(f"maxiter {v['geom:maxiter']}")

        inp["geom"].append(v["geom:step"])
        if v["geom:trust"]:
            trust_radius = -v["geom:trust"]
            if v["geom:step"] != "step qn":
                trust_radius *= {True: -1, False: 1}[v["geom:update_trust"]]
            inp["geom"].append(f"trust {trust_radius}")

        if v["initial hessian"]:
            inp["geom"].append(v["initial hessian"])
            if v["initial hessian"] == "inhess read":
                inp["geom"].append('inhessname "freq.hess"')
            if v["initial hessian"] == "calc_hess true" and use_numfreq:
                inp["geom"].append("numhess true")

        if v["freq:restart"]:
            inp["freq"].append("restart true")
        if v["freq:scaling"] and v["freq:scaling"] != 1.0:
            inp["freq"].append(f"scalfreq {v['freq:scaling']}")

        if v["nprocs"] > 1:
            inp["pal"].append(f"nprocs {v['nprocs']}")

        if v["excited states"]:
            if v["excited states:method"] == "TD-DFT":
                inp["tddft"].append(f"nroots {v['tddft:nroots']}")
                inp["tddft"].append(f"maxdim {v['tddft:maxdim']}")
                if not v["tddft:tda"]:
                    inp["tddft"].append("tda false")
                if v["tddft:nto"]:
                    inp["tddft"].append("donto true")

        self.text.delete("1.0", "end")
        self.text.insert("1.0", inp.generate())
