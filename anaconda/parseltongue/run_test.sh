#!/bin/bash

export PYTHONPATH=$PREFIX/lib/obit/python:$PREFIX/share/parseltongue/python
$PYTHON -c 'import Wizardry.AIPSData'
