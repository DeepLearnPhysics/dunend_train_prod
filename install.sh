#!/bin/bash
echo "initiating submodules"
git submodule init
git submodule update #--remote

echo "installing larnd-sim"
cd modules/larnd-sim
#git checkout 1b8d97bf9ccdbee56ded4ceb4582ab3570c32d3a
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
#git checkout 6f6fad0c0977dc4b420770d81d5647d2345ed828
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larpix_readout_parser"
    exit 1
fi
cd -

echo "installing SuperaAtomic"
cd modules/SuperaAtomic
#git checkout bde4a158ff31034a6381c37c81b13fe9c0feb2b6
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
#git checkout 296ae904d04ccf9e69f16c8087b56c8406d0d994
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install edep2supera"
    exit 1
fi
cd -

echo "installing larnd2supera"
cd modules/larnd2supera
#git checkout a86d512a6ab83f563655d4dfdef3cca92c606dc9
pip install . --user
if [ $? -gt 0 ]
then
    echo "Failed to install larnd2supera"
    exit 1
fi
cd -

echo "done"
