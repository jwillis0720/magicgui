#!/usr/bin/env python

"""Tests for `magicgui` package."""

from enum import Enum

import pytest
from qtpy import QtWidgets as QtW

from magicgui import magicgui


class Medium(Enum):
    Glass = 1.520
    Oil = 1.515
    Water = 1.333
    Air = 1.0003


def test_magicgui(qtbot):
    @magicgui
    def func(a: str = "string", b: int = 3, c=7.1) -> str:
        return "works"

    widget = func.Gui()
    assert func() == "works"
    assert widget.a == "string"
    assert widget.b == 3
    assert widget.c == 7.1
    assert isinstance(widget.a_widget, QtW.QLineEdit)
    assert isinstance(widget.b_widget, QtW.QSpinBox)
    assert isinstance(widget.c_widget, QtW.QDoubleSpinBox)

    widget.show()
    assert widget.isVisible()


def test_dropdown_list_from_enum(qtbot):
    @magicgui
    def func(arg: Medium = Medium.Water):
        ...

    widget = func.Gui()
    assert widget.arg == Medium.Water
    assert isinstance(widget.arg_widget, QtW.QComboBox)
    items = [widget.arg_widget.itemText(i) for i in range(widget.arg_widget.count())]
    assert items == Medium._member_names_


def test_dropdown_list_from_str(qtbot):
    CHOICES = ["Oil", "Water", "Air"]

    @magicgui(arg={"choices": CHOICES})
    def func(arg="Water"):
        ...

    widget = func.Gui()
    assert widget.arg == "Water"
    assert isinstance(widget.arg_widget, QtW.QComboBox)
    items = [widget.arg_widget.itemText(i) for i in range(widget.arg_widget.count())]
    assert items == CHOICES

    # the default value must be in the list
    @magicgui(arg={"choices": ["Oil", "Water", "Air"]})
    def func(arg="Silicone"):
        ...

    with pytest.raises(ValueError):
        widget = func.Gui()


def test_multiple_gui_independence(qtbot):
    @magicgui
    def example1(a=2):
        return a

    @magicgui
    def example2(a=5):
        return a

    w1 = example1.Gui()
    w2 = example2.Gui()
    # they get their initial values from the function sigs
    assert w1.a == 2
    assert w2.a == 5
    # settings one doesn't affect the other
    w1.a = 10
    assert w1.a == 10
    assert w2.a == 5
    # vice versa...
    w2.a = 4
    assert w2.a == 4
    assert w1.a == 10
    # calling the original equations updates the function defaults
    assert example1() == 10
    assert example2() == 4
