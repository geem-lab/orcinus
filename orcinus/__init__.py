#!/usr/bin/python3

"""Orcinus orca.

Orcinus orca is a simple graphical user interface (GUI) for the ORCA quantum
chemistry package.
"""

from collections.abc import MutableMapping


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
        inliners = ["!", "maxcore", "*"]
        lines = []

        for item in self["#"]:
            lines.append(f"# {item}")

        for key in inliners:
            tag = key
            if key == "*":
                tag = f"\n{key}"
            elif key == "maxcore":
                tag = f"%{key}"
            lines.append(
                f"{tag} {' '.join([str(v) for v in self[key] if v is not None])}"
            )

        for key, value in self.items():
            if (
                not isinstance(value, list)
                or set(value) == {None}
                or key in inliners
                or key == "#"
            ):
                continue
            lines.append(f"\n%{key}")
            for item in value:
                if item is not None:
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


if __name__ == "__main__":
    from orcinus.gui import main

    main()
