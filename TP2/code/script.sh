#!/bin/bash

# Comandos iniciais para configurar o ambiente

cd /home/core/Desktop/ESR-2425/TP2/code

boot_ip="10.0.25.10"
topologia="topologias/topo_overlay.json"

# Verifique o nome do nó para decidir o comando específico
case $1 in
  "c")
    export DISPLAY=:0.0
    python3 oClient.py "$boot_ip" "$2"
    ;;
  "n")
    python3 oNode.py -n "$boot_ip"
    ;;
  "pop")
    python3 oNode.py -pop "$boot_ip"
    ;;
  "s")
    python3 oNode.py -s "$topologia" "$2"
    ;;
  *)
    echo "Node not recognized"
    ;;
esac

