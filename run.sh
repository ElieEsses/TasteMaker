python3 -m venv venv
source venv/bin/activate          # same shell = same python
python -m pip install -q --upgrade pip

STD_LIB_REGEX='^(argparse|asyncio|base64|datetime|json|math|os|re|sys|time)$'
grep -vE "$STD_LIB_REGEX|^\s*#|^\s*$" requirements.txt > .req.clean

while read -r pkg; do
  if [[ -n "$pkg" ]]; then
    python -m pip install -q "$pkg" || {
      echo "⚠️  Skipping un-installable package: $pkg";
    }
  fi
done < .req.clean
rm .req.clean

python -B Project/main.py
python -m pip freeze | sort > requirements.txt
