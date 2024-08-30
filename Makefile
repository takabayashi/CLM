########### Confluent Platform Rules
cp: create-cp # use this rule to create confluent platform with docker
create-cp:
	rm -rf ./platforms/cp/.data
	docker compose --file ./platforms/cp/docker-compose.yml up --detach

destroy-cp:
	docker compose --file ./platforms/cp/docker-compose.yml down
	rm -rf ./platforms/cp/.data

check-cp-status:
	if [$(curl -LI http://rest-proxy:8082/clusters/777 -o /dev/null -w '%{http_code}\n' -s) == "200"]; then echo 0

cp-topics:
	docker compose exec kafka kafka-topics --create --if-not-exists --topic=my_monitored_topic --partitions=1 --bootstrap-server=localhost:9092

cp-latency-metrics:
	python kafka_latency_checker.py check-latency --platform=cp
cp-metrics: cp-latency-metrics

########### Confluent Cloud Rules
cc: create-cc # use this rule to create confluent cloud using terraform
create-cc:
	terraform -chdir=./platforms/cc/tf init
	terraform -chdir=./platforms/cc/tf plan -var-file="secret.tfvars"
	terraform -chdir=./platforms/cc/tf apply -var-file="secret.tfvars"

destroy-cc:
	terraform -chdir=./platforms/cc/tf destroy -var-file="secret.tfvars"

cc-latency-metrics:
	python kafka_latency_checker.py check-latency --platform=cc
cc-metrics: cc-latency-metrics