from math import inf
from constants import colors


class Node:
    nodetypes = ["blank", "start", "end", "wall", "mud", "dormant"]

    colors = {
        "regular": {
            "blank": colors.WHITE,
            "start": colors.RED,
            "end": colors.BLUE,
            "wall": colors.BLACK,
            "dormant": colors.GREY,
        },
        "visited": {
            "blank": colors.GREEN,
            "start": colors.RED,
            "end": colors.BLUE,
            "wall": colors.BLACK,
            "dormant": colors.GREY,
        },
        "path": {
            "blank": colors.GREY,
            "start": colors.RED,
            "end": colors.BLUE,
            "wall": colors.BLACK,
            "dormant": colors.GREY,
        },
    }

    distance_modifiers = {
        "blank": 1,
        "start": 1,
        "end": 1,
        "wall": inf,
        "dormant": inf,
    }

    def __init__(self, nodetype, text="", colors=colors, dmf=distance_modifiers):
        self.nodetype = nodetype
        self.rcolor = colors["regular"][self.nodetype]
        self.vcolor = colors["visited"][self.nodetype]
        self.pcolor = colors["path"][self.nodetype]
        self.is_visited = (
            True if nodetype == "start" else True if nodetype == "end" else False
        )
        self.is_path = (
            True if nodetype == "start" else True if nodetype == "end" else False
        )
        self.distance_modifier = dmf[self.nodetype]
        self.color = (
            self.pcolor
            if self.is_path
            else self.vcolor
            if self.is_visited
            else self.rcolor
        )

    def update(
        self,
        nodetype=False,
        is_visited="unchanged",
        is_path="unchanged",
        colors=colors,
        dmf=distance_modifiers,
        nodetypes=nodetypes,
    ):
        if nodetype:
            assert nodetype in nodetypes, f"nodetype must be one of: {nodetypes}"
            if (self.nodetype == ("start" or "end")) and (
                nodetype == ("wall" or "mud")
            ):
                pass
            else:
                self.nodetype = nodetype

        if is_visited != "unchanged":
            assert (
                type(is_visited) == bool
            ), "'is_visited' must be boolean: True or False"
            self.is_visited = is_visited

        if is_path != "unchanged":
            assert type(is_path) == bool, "'is_path' must be boolean: True or False"
            self.is_path = is_path

        self.rcolor = colors["regular"][self.nodetype]
        self.vcolor = colors["visited"][self.nodetype]
        self.pcolor = colors["path"][self.nodetype]
        self.distance_modifier = dmf[self.nodetype]
        self.color = (
            self.pcolor
            if self.is_path
            else self.vcolor
            if self.is_visited
            else self.rcolor
        )
