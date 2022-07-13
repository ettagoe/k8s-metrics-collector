#!/usr/bin/env bash

curl -X POST http://localhost:8428/api/v1/import -T test-datasets/node_cpu_seconds_total.jsonl
echo "Uploaded node_cpu_seconds_total.jsonl"
curl -X POST http://localhost:8428/api/v1/import -T test-datasets/node_network_recieve_bytes_total.jsonl
echo "Uploaded node_network_recieve_bytes_total.jsonl"
curl -X POST http://localhost:8428/api/v1/import -T test-datasets/node_network_transmit_bytes_total.jsonl
echo "Uploaded node_network_transmit_bytes_total.jsonl"
