#!/bin/bash
cd /workspace/research2/pulse26
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
PY="nice -n 19 ../venv/bin/python -u"
while pgrep -f "download.py II MBAR" >/dev/null; do sleep 10; done
$PY features.py II.MBAR.00.LHZ > features_MBAR.log 2>&1
$PY download.py II SHEL 00 LHZ 2022 3 2024 2 > download_SHEL.log 2>&1
$PY features.py II.SHEL.00.LHZ > features_SHEL.log 2>&1
$PY components.py > components.log 2>&1
$PY tide_compare.py > tide_compare.log 2>&1
$PY multistation.py > multistation.log 2>&1
echo QUEUE_DONE >> multistation.log
