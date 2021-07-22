#!/bin/bash

config_file="/etc/systemd/resolved.conf.d/consul.conf"

mkdir -p /etc/systemd/resolved.conf.d
rm -rf "$config_file"
touch "$config_file"
echo "[Resolve]" >"$config_file"
echo "DNS=172.20.0.2" >>"$config_file"
echo "Domains=~." >>"$config_file"

echo "Run sudo systemctl restart systemd-resolved.service to apply changes"
