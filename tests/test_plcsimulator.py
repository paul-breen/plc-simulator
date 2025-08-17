import os

import pytest

import plcsimulator

base = os.path.dirname(__file__)

def test_version():
    assert plcsimulator.__version__ == '0.5.0'

