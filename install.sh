#!/bin/bash
echo "initiating submodules"
git submodule init
git submodule update 

echo "installing larnd-sim"
cd modules/larnd-sim
export SKIP_CUPY_INSTALL=1
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larnd-sim"
    exit 1
fi
cd -

echo "installing event parser"
cd modules/larpix_readout_parser
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larpix_readout_parser"
    exit 1
fi
cd -

echo "installing ndlar_flow"
cd modules/ndlar_flow
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install ndlar_flow"
    exit 1
fi
cd -

echo "installing SuperaAtomic"
cd modules/SuperaAtomic
export SUPERA_WITHOUT_PYTHON=1
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install SuperaAtomic"
    exit 1
fi
cd -

echo "installing edep2supera"
cd modules/edep2supera
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install edep2supera"
    exit 1
fi
cd -

echo "installing larnd2supera"
cd modules/larnd2supera
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larnd2supera"
    exit 1
fi
cd -

echo "installing flow2supera"
cd modules/flow2supera
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install flow2supera"
    exit 1
fi
cd -

echo "done"
