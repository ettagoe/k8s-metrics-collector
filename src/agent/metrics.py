m = {
  "node": {
    "node_cpu_utilization": "avg_over_time(cluster:node_cpu:ratio[%I%])",
    # todo do I need job here?
    "node_cpu_usage_total": "sum((1 - sum without (mode) (rate(node_cpu_seconds_total{job=\"node-exporter\", mode=~\"idle|iowait|steal\"}[%I%]))) / ignoring(cpu) group_left count without (cpu, mode) (node_cpu_seconds_total{job=\"node-exporter\", mode=\"idle\"})) by (instance)",
    "node_interface_network_rx_bytes": "sum_over_time(node_network_receive_bytes_total[%I%])",
    "node_interface_network_rx_dropped": "node_network_receive_drop_total[%I%]",
    "node_interface_network_rx_errors": "node_network_receive_errs_total[%I%]",
    "node_interface_network_rx_packets": "node_network_receive_packets_total[%I%]",
    "node_network_rx_bytes": "sum(node_interface_network_rx_bytes)",
    "node_network_tx_bytes": "sum(node_interface_network_tx_bytes)",
    "node_network_total_bytes": "sum(node_interface_network_rx_bytes) + sum(node_interface_network_tx_bytes)"

  },
  "container": {
    "container_cpu_limit": "kube_pod_container_resource_limits",
    "container_cpu_request": "kube_pod_container_resource_requests"
  }
}