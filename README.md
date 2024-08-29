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

This file defines the scenarios to be tested. Each scenario should have the following parameters:

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

## Running the Application

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. File up the `cluster.properties` file with the access information about your cluster.

3. Run the latency checker:
   ```bash
   python kafka_latency_checker.py check-latency
   ```

4. Check the results in the `.results` folder. The results will be saved in the `.results` directory, with each run having its own subdirectory named by the epoch time.

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
