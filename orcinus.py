#!/usr/bin/python3

"""Orcinus orca.

Orcinus orca is a simple graphical user interface (GUI) for the ORCA quantum
chemistry package.
"""

from collections.abc import MutableMapping
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


class ORCAInput(MutableMapping):
    """A simple abstraction of an ORCA input file."""

    def __init__(self, data=None):
        """Construct object."""
        self._mapping = {}
        if data is not None:
            self.update(data)

    def __repr__(self):
        """Return string representation of self."""
        return f"{type(self).__name__}({self._mapping})"

    def generate(self):
        """Generate input content."""
        lines = []
        for item in self["#"]:
            lines.append(f"# {item}")
        lines.append(
            f"! {' '.join([str(v) for v in self['!'] if v is not None])}"
        )
        lines.append(
            f"\n* {' '.join([str(v) for v in self['*'] if v is not None])}"
        )
        for key, value in self.items():
            if not isinstance(value, list) or key in {"#", "!", "*"}:
                continue
            lines.append(f"\n%{key}")
            for item in value:
                lines.append(f" {item}")
            lines.append("end")

        return "\n".join(lines)

    def __getitem__(self, key):
        """Get item at key."""
        if key not in self._mapping:
            self._mapping[key] = []
        return self._mapping[key]

    def __setitem__(self, key, value):
        """Set item at key to value."""
        self._mapping[key] = value

    def __delitem__(self, key):
        """Delete item at key."""
        del self._mapping[key]

    def __iter__(self):
        """Iterate keys."""
        return iter(self._mapping)

    def __len__(self):
        """Return number of keys."""
        return len(self._mapping)


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
            state_filename="questions.pickle",
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
                        "Energy",
                        "Opt",
                        "Freq",
                        "Opt Freq",
                        # "Scan",
                        "OptTS",
                        "OptTS Freq",
                        "IRC",
                        "NEB",
                        "NEB Freq",
                        # "MD",
                        # "NoIter",
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
                    "switch": [
                        ("task", lambda v: "Freq" in v),
                        ("initial hessian", "Calculate"),
                    ],
                },
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
                        # "Hybrid:B3LYP/G": "B3LYP/G",  # same as in Gaussian
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
                # TODO(schneiderfelipe): the 1-center approximation option is
                # relevant to calculations using ZORA.
                "spin-orbit coupling": {
                    "group": "level of theory",
                    "help": (
                        "Whether spin-orbit coupling should be taken into "
                        "account."
                    ),
                    "widget": Checkbutton,
                    "default": False,
                },
                # TODO(schneiderfelipe): create a details group for SCF
                # convergence things such as solvers (e.g. DIIS, KDIIS,
                # MORead), initial guesses (e.g, PModel, Hueckel), etc.. It
                # is also nice to allow a stability analysis of the SCF
                # wavefunction. In the future I also want to implement
                # options for rotating orbitals.
                # TODO(schneiderfelipe): give some support for diffuse
                # functions, specially minimally augmented. For that, some
                # nice options for avoiding linear dependency problems are
                # required in a special group for SCF convergence.
                # TODO(schneiderfelipe): give support for cc basis set family
                # (cc-pVTZ, etc.).
                # TODO(schneiderfelipe): give support for Pople-style basis
                # sets (6-31G, 6-311G, etc.). Other families beside cc and
                # def2 is ano (they also have aug-cc, ma-def2 and
                # saug-ano/aug-ano).
                # TODO(schneiderfelipe): extrapolation techniques are
                # interesting for single point calculations with DLPNO-CC
                # methods.
                # TODO(schneiderfelipe): switch to basis sets consistent with
                # relativistic approximations.
                "basis:family": {
                    "group": "level of theory",
                    "text": "Basis set family",
                    "help": ("Which basis set family should be employed."),
                    "values": ["def2"],
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                "basis:def2": {
                    "group": "level of theory",
                    "text": "Basis set quality",
                    "help": ("Which basis set should be used."),
                    "values": {
                        "DZ(P)": "def2-SV(P)",
                        "DZP": "def2-SVP",
                        "TZP": "def2-TZVP",
                        "TZP(-f)": "def2-TZVP(-f)",
                        "TZPP": "def2-TZVPP",
                        "QZP": "def2-QZVP",
                        "QZPP": "def2-QZVPP",
                    },
                    "default": "TZP",
                },
                "ecp": {
                    "group": "level of theory",
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
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): support solvation models (GBSA for
                # XTB, CPCM and SMD). Cavity construction in continuum
                # solvation is also something that oftentimes produce
                # imaginary frequencies. As such, options on that are also
                # necessary.
                # TODO(schneiderfelipe): continuum solvation models are very
                # important, in particular also parameters for cavity
                # definition such as GEPOL, SES/SAS and atomic radii. But
                # don't be too boring.
                "solvent": {
                    "help": ("Which solvent should be considered."),
                    "values": [
                        "Acetone",  # also available in CPCM
                        "Acetonitrile",  # also available in CPCM
                        "Benzene",  # unavailable in CPCM
                        "Dichloromethane",  # also available in CPCM
                        "Chloroform",  # also available in CPCM
                        "Carbon disulfide",  # unavailable in CPCM
                        "Dimethylformamide",  # unavailable in GFN1-xTB, also available in CPCM
                        "Dimethyl sulfoxide",  # also available in CPCM
                        "Ether",  # unavailable in CPCM
                        "Water",  # also available in CPCM
                        "Methanol",  # also available in CPCM
                        "n-Hexane",  # unavailable in GFN1-xTB, also available in CPCM
                        "Tetrahydrofuran",  # also available in CPCM
                        "Toluene",  # also available in CPCM
                    ],
                },
                # TODO(schneiderfelipe): set analogous standards for COSX
                # grids as well for when RIJCOSX is used.
                "numerical:quality": {
                    "help": (
                        "Which numerical quality is desired. Good is "
                        "defined as enough to avoid imaginary "
                        "frequencies due to numerical noise, but you "
                        "might need more than that."
                    ),
                    "values": {
                        "Auto": None,
                        "Normal": 3,
                        "Good": 4,
                        "Very Good": 5,
                        "Excellent": 6,
                    },
                    "default": "Good",
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
                },
                # TODO(schneiderfelipe): choose resolution of identity as a
                # on/off tick and pre-select the best approximations in each
                # case. Choose appropriate auxiliary basis sets either based on
                # basis set class, or using AutoAux.
                # TODO(schneiderfelipe): support specifying number of
                # processors. This should be in the acceleration section,
                # together with resolution of identity. Such section must
                # contain only things that make calculations fast without
                # changing accuracy.
                # TODO(schneiderfelipe): support setting maximum memory
                # requirements. I prefer to set it to total memory and
                # calculate the value per core, as this is the relevant
                # information (i.e., how much the computer has). This is
                # eligible for the acceleration section because it is related
                # to the number of processors and because having a good about
                # of memory avoids too many batches in many parts of the
                # code, thus accelerating calculations. This requires a
                # one-liner starting with %, so we need to teach ORCAInput to
                # understand accept
                #
                #     inp["%maxcore"].append(3000)
                #
                # as
                #
                #     "%maxcore 3000"
                #
                # which is new behavior.
                "ri": {
                    "group": "acceleration",
                    "text": "Resolution of identity",
                    "help": (
                        "Whether a resolution of identity approximation "
                        "should be used."
                    ),
                    # TODO(schneiderfelipe): this is a case where it makes
                    # sense to add both None (explicitly no) and "Auto"
                    # (standard ORCA policy), as they mean different things.
                    # Say it in the help.
                    "values": {
                        "Auto": "Auto",
                        None: "NoRI",
                        "RI": "RI",
                        "RI-JK": "RI-JK",
                        "RIJCOSX": "RIJCOSX",
                    },
                    "switch": ("theory", {"HF", "DFT", "MP2", "CCSD"}),
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
                    "values": ["Auto"] + list(range(100, 1001, 50)),
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
                    "values": ["Auto"],
                },
                "geom:maxiter": {
                    "tab": "details",
                    "group": "geometry convergence",
                    "text": "Maximum number of iterations",
                    "help": (
                        "Maximum number of geometry optimization "
                        "iterations."
                    ),
                    "widget": Spinbox,
                    "values": ["Auto"] + list(range(50, 1001, 25)),
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
                    "values": ["Auto", "BFGS", "Bofill", "Powell"],
                },
                # TODO(schneiderfelipe): create a group for restarts in
                # details that support reading a gbw
                "initial hessian": {
                    "tab": "details",
                    "group": "geometry convergence details",
                    "help": (
                        "Which initial model Hessian should be used for "
                        "optimization convergence. 'Auto' probably means "
                        "'Almloef'"
                    ),
                    # TODO(schneiderfelipe): sometimes an order similar to the
                    # one below is the best thing possible, with the best or
                    # most common first:
                    "values": {
                        "Auto": None,
                        "Calculate": "calc_hess true",
                        "Read": "inhess read",
                        "Swart": "inhess swart",
                        "Lindh": "inhess lindh",
                        "Almloef": "inhess almloef",
                        "Schlegel": "inhess schlegel",
                        "Diagonal": "inhess unit",
                    },
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
                # TODO(schneiderfelipe): TD-DFT for UV-vis is kind of a
                # priority at the moment.
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
                # TODO(schneiderfelipe): Tamm-Dancoff approximation is an
                # important approximation and deserves a nice spot in the
                # interface.
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
                # TODO(schneiderfelipe): this should give something like
                #
                #     %tddft
                #      nroots 4
                #     end
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

        self.clear_button.bind("<Button-1>", self.clear)
        self.save_button.bind("<Button-1>", self.save)
        for _, var in self.questions.variable.items():
            var.trace("w", self.update_widgets)

        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        """Update input content with currently selected options."""
        v = self.questions.get_values()
        print(v)  # TODO(schneiderfelipe): do proper logging, this is debug!
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

        if v["ri"] and v["ri"] != "Auto":
            inp["!"].append(v["ri"])
        inp["!"].append(v["relativity"])

        if v["theory"] in {"HF", "MP2"}:
            inp["!"].append(v["theory"])
        if v["theory"] == "DFT":
            inp["!"].append(v["functional"])
        elif v["theory"] == "DFTB":
            inp["!"].append(v["hamiltonian"])
        elif v["theory"] == "CCSD":
            kw = v["theory"]
            if v["triples correction"]:
                kw = kw + "(T)"
            if v["dlpno"]:
                kw = "DLPNO-" + kw
            inp["!"].append(kw)

        inp["!"].append(v["dispersion"])

        inp["!"].append(v[f"basis:{v['basis:family']}"])
        if v["ri"] in {"RI", "RIJCOSX"}:
            if v["relativity"]:
                inp["!"].append("SARC/J")
            else:
                inp["!"].append("def2/J")

        # TODO(schneiderfelipe): this should probably go to the end of the
        # keywords
        if v["ri"] == "RIJCOSX":
            inp["!"].append(f"{v['basis set']}/C")
        if v["ri"] == "RI-JK":
            inp["!"].append("def2/JK")

        if v["theory"] in {"MP2", "CCSD"}:
            inp["!"].append(v["frozen core"])

        if v["uco"]:
            inp["!"].append("UCO")

        if v["numerical frequencies"] and "Freq" in v["task"]:
            v["task"] = v["task"].replace("Freq", "NumFreq")
        if v["task"] != "Energy":
            inp["!"].append(v["task"])

        if v["numerical:quality"]:
            if v["numerical:quality"] > 3:
                if "Opt" in v["task"]:
                    inp["!"].append("TightOpt")
                inp["!"].append("TightSCF")
            inp["!"].append(f"Grid{v['numerical:quality']}")
            inp["!"].append(f"FinalGrid{v['numerical:quality'] + 1}")

        if v["short description"]:
            inp["#"].append(f"{v['short description']}")

        if v["scf:maxiter"] and v["scf:maxiter"] != "Auto":
            inp["scf"].append(f"maxiter {v['scf:maxiter']}")
        if v["geom:maxiter"] and v["geom:maxiter"] != "Auto":
            inp["geom"].append(f"maxiter {v['geom:maxiter']}")

        if v["initial hessian"]:
            inp["geom"].append(v["initial hessian"])
            if v["initial hessian"] == "inhess read":
                inp["geom"].append("inhessname 'freq.hess'")
            if (
                v["initial hessian"] == "calc_hess true"
                and v["numerical frequencies"]
            ):
                inp["geom"].append("numhess true")

        self.text.delete("1.0", "end")
        self.text.insert("1.0", inp.generate())


if __name__ == "__main__":
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
