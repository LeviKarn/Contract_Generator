#!/bin/sh
cd "$(dirname "$0")"
python3 src/generator.py
read -p "Zum Beenden Enter drücken ..."
