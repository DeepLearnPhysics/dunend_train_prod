#!/bin/bash
echo "initiating submodules"
git submodule init
git submodule update --remote

echo "installing larnd-sim"
cd modules/larnd-sim
git checkout c5042f1c6fc9b1f6b6a37e6e6c3ff0615c7c5c26
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
git checkout 281549740d15c0c2a2a8a9bf33ad58ea74cc50cb
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larpix_readout_parser"
    exit 1
fi
cd -

echo "installing SuperaAtomic"
cd modules/SuperaAtomic
git checkout bde4a158ff31034a6381c37c81b13fe9c0feb2b6
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
git checkout 296ae904d04ccf9e69f16c8087b56c8406d0d994
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install edep2supera"
    exit 1
fi
cd -

echo "installing larnd2supera"
cd modules/larnd2supera
git checkout 6e2cae6684dcdebabae08e068d72c312dee063da
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larnd2supera"
    exit 1
fi
cd -

echo "done"
