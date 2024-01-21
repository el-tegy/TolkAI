output "streamlit_instance_ips" {
  value = google_compute_instance.streamlit_node.*.network_interface.0.access_config.0.nat_ip
}

output "streamlit_ssh_commands" {
  value = [for ip in google_compute_instance.streamlit_node.*.network_interface.0.access_config.0.nat_ip : "ssh ${var.username}@${ip}"]
}
