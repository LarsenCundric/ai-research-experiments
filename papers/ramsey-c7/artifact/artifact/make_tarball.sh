#!/bin/bash
# Pack the artifact (sources, base CNFs, cubes, logs, colourings, paper) into artifact/ramsey-c7-artifact.tar.gz
cd /workspace/ramsey-c7 && artifact/make_checksums.sh && \
tar czf artifact/ramsey-c7-artifact.tar.gz artifact/README.md artifact/SHA256SUMS $(cut -c67- artifact/SHA256SUMS) && \
ls -la artifact/ramsey-c7-artifact.tar.gz
