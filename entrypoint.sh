#!/bin/sh -l

cd /github/workspace/LCV
python3 main.py &
newman run https://api.postman.com/collections/718114-7c3075d5-4fcb-4621-b867-1b3b726b551a?access_key=PMAT-01HHB6WCBQYZ3TPNTBMWB0G29A