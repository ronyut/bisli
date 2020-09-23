#!/bin/bash
echo -ne "Pyan architecture: generating architecture.{dot,svg}\n"
./pyan.py pyan/*.py --no-defines --uses --colored --annotate --dot -V >architecture.dot 2>architecture.log
dot -Tsvg architecture.dot >architecture.svg
