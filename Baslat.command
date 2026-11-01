#!/bin/zsh
cd -- "${0:A:h}"
if ! command -v python3 >/dev/null; then
  echo "Python 3 gerekiyor. https://www.python.org/downloads/ adresinden kurabilirsiniz."
  read 'reply?Kapatmak için Enter'; exit 1
fi
python3 server.py
