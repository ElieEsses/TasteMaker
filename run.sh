#!/usr/bin/env bash
set -euo pipefail

python3 -m venv venv
source venv/bin/activate
python -m pip install --quiet --upgrade pip setuptools wheel

REQ_IN="requirements.in"
REQ_LOCK="requirements.txt"
STD_LIB_REGEX='^(argparse|asyncio|base64|datetime|json|math|os|re|sys|time)$'

# Only regenerate requirements.txt if requirements.in changed
if [[ ! -f $REQ_LOCK || $REQ_IN -nt $REQ_LOCK ]]; then
  echo "🔄  Updating lock file..."
  grep -vE "$STD_LIB_REGEX|^\s*#|^\s*$" "$REQ_IN" > .req.clean
  while read -r pkg; do
    if [[ -n "$pkg" ]]; then
      python -m pip install -q "$pkg" || echo "⚠️  Skipping: $pkg"
    fi
  done < .req.clean
  python -m pip freeze | sort > "$REQ_LOCK"
  rm .req.clean
else
  python -m pip install -q -r "$REQ_LOCK"
fi

# Run your app
python -B Project/main.py
