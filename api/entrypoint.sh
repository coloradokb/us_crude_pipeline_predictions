#!/bin/bash

# Mount the NFS share
mount -t nfs 10.1.10.78:/nas_d1/datastore/pipeline/db	/datastore/pipeline/db
cd /app && . venv/bin/activate && python main.py
