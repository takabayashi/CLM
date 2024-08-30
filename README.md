# CLM - Confluent Light Monitor

This application is designed to monitor in a light way confluent clusters. Among the monitoring capabilities you will find the following capabilities:

 - `check_latency` Check the latency of Kafka producers by running various scenarios defined in a YAML configuration file. It calculates P90, P95, and P99 latency metrics for each scenario and batch, and saves the results in a structured format.

## Configuration

### cluster.properties

This file contains the Kafka cluster configuration. Ensure the following fields are correctly set:

- `bootstrap_servers`: The Kafka bootstrap server address.
- `sasl_mechanism`: The SASL mechanism used for authentication.
- `security_protocol`: The security protocol used.
- `sasl_plain_username`: The username for SASL authentication.
- `sasl_plain_password`: The password for SASL authentication.

### scenario.yaml

This file defines the scenarios to be forced agaisnt a cluster during monitoring time. Each scenario should have the following parameters:

- `msgs`: Number of messages to send in each batch.
- `batches`: Number of times to repeat the scenario.
- `timeout`: Timeout for each message send operation.
- `max_threads`: Maximum number of threads to use for sending messages.
- `message`: The message content to send.

Example:
```yaml
latency:
  - scenario_1:
      msgs: 1000 # number of messages used by this test in each batch
      batches: 2 # number of batches
      timeout: 10 # max timeout before a error hit. Errors will not be part of the latency calculation.
      max_threads: 10 # max number of threads used by the application to send mesages in parallel
      message: 
        value: {'attr1': 'value_attr1', 'attr2': 'value_attr2'} # value of message to be produced
```

## Platforms Overview

### Confluent Cloud (CC)
Confluent Cloud is a fully managed Apache Kafka service that allows you to focus on building your applications without the operational overhead of managing Kafka infrastructure. It provides scalability, security, and reliability out of the box.

### Confluent Platform (CP)
Confluent Platform is a self-managed distribution of Apache Kafka that includes additional tools and services to enhance Kafka's capabilities. It allows for on-premises deployment and provides features like schema registry, ksqlDB, and Kafka Connect.

## Starting the Environments

### Starting Confluent Platform (CP)
To start the Confluent Platform using Docker, use the following command:
```bash
make cp
```
This command will initialize and start the Confluent Platform services defined in the `docker-compose.yml` file.

### Starting Confluent Cloud (CC)
To create a Confluent Cloud environment using Terraform, follow these steps:
1. Navigate to the Terraform directory:
   ```bash
   cd platforms/cc/tf
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Plan and apply the Terraform configuration:
   ```bash
   terraform plan -var-file="secret.tfvars"
   terraform apply -var-file="secret.tfvars"
   ```

## Running the Application

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. File up the `cluster.properties` file with the access information about your cluster.

4. Run the latency checker:
   ```bash
   python kafka_latency_checker.py check-latency
   ```

5. Check the results in the `.results` folder. The results will be saved in the `.results` directory, with each run having its own subdirectory named by the epoch time.

## Running Latency Metrics

### On Confluent Platform (CP)
To run latency metrics on the Confluent Platform, use the following command:
```bash
make cp-latency-metrics
```
This will execute the latency checker for the Confluent Platform.

### On Confluent Cloud (CC)
To run latency metrics on Confluent Cloud, use the following command:
```bash
make cc-latency-metrics
```
This will execute the latency checker for Confluent Cloud.

## Setup Envriroment
### Creating a Confluent Cloud Cluster with terraform

1. Create a `secret.tfvars` file with your CC api key information. Use the template file to make your life easier.
2. Initialize terraform

```shell
cd tf
terraform init
```

3. Plan and apply your changes. This command will create a new cluster at your CC enviroment.

```shell
terraform plan -var-file="secret.tfvars" 
terraform apply -var-file="secret.tfvars" 
```

4. Get the terraform output file u the `cluster.properties` file. 

```shell
terraform output
```

Now you are ready to run a first metric agains a confluent cloud cluster.


## Dependencies

All dependencies are listed in the `requirements.txt` file.
