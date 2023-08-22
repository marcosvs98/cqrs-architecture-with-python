#!/bin/bash
echo "Rodando pre-commit"
pre-commit run --from-ref origin/HEAD --to-ref HEAD
