#!/bin/bash
# replaces queue3 order (GEOFON is slow, ~4 min/month): SACV first, then WIN
cd /workspace/research2/pulse26
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3000000
PY="nice -n 19 timeout 9000 ../venv/bin/python -u"
$PY download.py II SACV 00 LHZ 2022 3 2024 2 > download_SACV.log 2>&1
$PY features.py II.SACV.00.LHZ > features_SACV.log 2>&1
echo SACV_DONE >> features_SACV.log
$PY download.py GE WIN -- LHZ 2022 3 2024 2 >> download_WIN.log 2>&1
$PY features.py GE.WIN.--.LHZ > features_WIN.log 2>&1
echo QUEUE4_DONE >> features_WIN.log
