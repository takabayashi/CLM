# Makefile for managing Confluent Platform and Confluent Cloud

# Display help for each rule
help:
	@echo "Available rules:"
	@echo "  cp                - Create Confluent Platform using Docker"
	@echo "  create-cp         - Initialize and start Confluent Platform services"
	@echo "  destroy-cp        - Stop and remove Confluent Platform services"
	@echo "  check-cp-status   - Check the status of the Confluent Platform"
	@echo "  cp-topics         - Create a topic in the Confluent Platform"
	@echo "  cp-latency-metrics- Run latency metrics on Confluent Platform"
	@echo "  cc                - Create Confluent Cloud using Terraform"
	@echo "  create-cc         - Initialize and apply Terraform for Confluent Cloud"
	@echo "  destroy-cc        - Destroy Confluent Cloud resources"
	@echo "  cc-latency-metrics- Run latency metrics on Confluent Cloud"

########### Confluent Platform Rules
# Create Confluent Platform using Docker
cp: create-cp

# Initialize and start Confluent Platform services
create-cp:
	rm -rf ./platforms/cp/.data
	docker compose --file ./platforms/cp/docker-compose.yml up --detach

# Stop and remove Confluent Platform services
destroy-cp:
	docker compose --file ./platforms/cp/docker-compose.yml down
	rm -rf ./platforms/cp/.data

# Check the status of the Confluent Platform
check-cp-status:
	if [$(curl -LI http://rest-proxy:8082/clusters/777 -o /dev/null -w '%{http_code}\n' -s) == "200"]; then echo 0

# Create a topic in the Confluent Platform
cp-topics:
	docker compose exec kafka kafka-topics --create --if-not-exists --topic=my_monitored_topic --partitions=1 --bootstrap-server=localhost:9092

# Run latency metrics on Confluent Platform
cp-latency-metrics:
	python kafka_latency_checker.py check-latency --platform=cp
cp-metrics: cp-latency-metrics

########### Confluent Cloud Rules
# Create Confluent Cloud using Terraform
cc: create-cc

# Initialize and apply Terraform for Confluent Cloud
create-cc:
	terraform -chdir=./platforms/cc/tf init
	terraform -chdir=./platforms/cc/tf plan -var-file="secret.tfvars"
	terraform -chdir=./platforms/cc/tf apply -var-file="secret.tfvars"

# Destroy Confluent Cloud resources
destroy-cc:
	terraform -chdir=./platforms/cc/tf destroy -var-file="secret.tfvars"

# Run latency metrics on Confluent Cloud
cc-latency-metrics:
	python kafka_latency_checker.py check-latency --platform=cc
cc-metrics: cc-latency-metrics
