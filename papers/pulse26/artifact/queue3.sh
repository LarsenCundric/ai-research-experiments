#!/bin/bash
# extra stations for robustness round (10 Oct 2026): II.ASCN, GE.WIN, II.SACV, LHZ 2022-03..2024-02
cd /workspace/research2/pulse26
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3000000
PY="nice -n 19 timeout 7200 ../venv/bin/python -u"
$PY download.py II ASCN 00 LHZ 2022 3 2024 2 > download_ASCN.log 2>&1
$PY features.py II.ASCN.00.LHZ > features_ASCN.log 2>&1
$PY download.py GE WIN -- LHZ 2022 3 2024 2 > download_WIN.log 2>&1
$PY features.py GE.WIN.--.LHZ > features_WIN.log 2>&1
$PY download.py II SACV 00 LHZ 2022 3 2024 2 > download_SACV.log 2>&1
$PY features.py II.SACV.00.LHZ > features_SACV.log 2>&1
echo QUEUE3_DONE >> features_SACV.log
