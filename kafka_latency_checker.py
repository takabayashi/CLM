import yaml
from hello import hello
import click
import logging
from kafka import KafkaProducer
import configparser
import time
import numpy as np
import threading
import progressbar
import os
import json
from concurrent.futures import ThreadPoolExecutor

@click.group()
def cli():
    """Kafka Latency Checker CLI."""
    pass

class LatencyMetrics:
    def __init__(self, producer, topic, msgs, timeout, message_value, threads):
        self._threads = threads
        self._producer = producer
        self._topic = topic
        self._latencies = []
        self._lock = threading.Lock()
        self._bar = progressbar.ProgressBar(max_value=msgs, redirect_stdout=True)
        self._msgs = msgs
        self._timeout = timeout
        self._message_value = message_value

    def execute(self):
        print("Starting latency monitoring...")
        from concurrent.futures import ThreadPoolExecutor

        def send_message():
            start_time = time.time()
            try:
                future = self._producer.send(self._topic, str(self._message_value).encode('utf-8'), timestamp_ms=int(start_time * 1000))
                future.add_callback(lambda metadata: self.__success_handler(start_time, metadata))
                future.add_errback(lambda exception: self.__error_handler(start_time, exception))
                future.get(timeout=self._timeout)
            except Exception as excp:
                logging.error(f"Error sending message at {time.time()}: {excp}. Start time was {start_time}")

        with ThreadPoolExecutor(max_workers=self._threads) as executor:
            for _ in range(self._msgs):
                executor.submit(send_message)

        logging.debug("Flushing producer...")
        self._producer.flush()
        logging.debug("Producer flush complete.")

        p90, p95, p99 = self.__calculate_percentiles()
        if p90 is None:
            print("No latencies recorded. Please check your Kafka configuration and try again.")
        else:
            print(f"P90 latency: {p90:.2f} seconds")
            print(f"P95 latency: {p95:.2f} seconds")
            print(f"P99 latency: {p99:.2f} seconds")

    def __success_handler(self, start_time, _):
        latency = time.time() - start_time
        with self._lock:
            self._latencies.append(latency)
            self._bar.update(len(self._latencies))

    def __error_handler(self, exception, start_time):
        logging.error(f"Error sending message at {time.time()}: {exception}. Start time was {start_time}")
        with self._lock:
            self._latencies.append(None)
            self._bar.update(len(self._latencies))

    def __calculate_percentiles(self):
        with self._lock:
            if not self._latencies:
                return None, None, None
            p90 = np.percentile(self._latencies, 90)
            p95 = np.percentile(self._latencies, 95)
            p99 = np.percentile(self._latencies, 99)
        return p90, p95, p99

@cli.command()
@click.option('--topic', default="my_monitored_topic", help='Kafka topic to check latency for.')
@click.option('--platform', type=click.Choice(['cc', 'cp'], case_sensitive=False))
def check_latency(topic, platform):
    """Check the P90, P95, and P99 latency of Kafka producers."""
    config = configparser.ConfigParser()
    config.read('cluster.properties')

    print("Initializing KafkaProducer...")

    if platform == 'cc':
        producer = KafkaProducer(
            bootstrap_servers=config['cc']['bootstrap_servers'],
            security_protocol=config['cc']['security_protocol'],
            sasl_mechanism=config['cc']['sasl_mechanism'],
            sasl_plain_username=config['cc']['sasl_plain_username'],
            sasl_plain_password=config['cc']['sasl_plain_password']
        )
    else:
         producer = KafkaProducer(
            bootstrap_servers=config['cp']['bootstrap_servers'],
            security_protocol=config['cp']['security_protocol'],
            sasl_mechanism=config['cp']['sasl_mechanism']
         )

    with open('scenario.yaml', 'r') as file:
        scenarios = yaml.safe_load(file)

    for scenario in scenarios['latency']:
        for name, params in scenario.items():
            print(f"Running {name} with parameters: {params}")
            epoch_id = int(time.time())
            print(f"Run ID: {epoch_id}")

            epoch_id = int(time.time())
            results_dir = f".results/{epoch_id}"
            os.makedirs(results_dir, exist_ok=True)

            all_latencies = []

            def write_results(file_path, data):
                with open(file_path, 'w') as file:
                    json.dump(data, file)

            for batch in range(params['batches']):
                print(f"Running batch {batch + 1}/{params['batches']}")

                metrics = LatencyMetrics(
                    producer,
                    topic,
                    msgs=params['msgs'],
                    timeout=params['timeout'],
                    message_value=params['message']['value'],
                    threads=params['max_threads']
                )
                metrics.execute()

                all_latencies.extend(metrics._latencies)

                # Asynchronously save individual batch results
                batch_results_path = os.path.join(results_dir, f"batch_{batch + 1}_results.json")
                with ThreadPoolExecutor(max_workers=2) as executor:
                    executor.submit(write_results, batch_results_path, metrics._latencies)

        # Calculate consolidated results
        consolidated_p90 = np.percentile(all_latencies, 90)
        consolidated_p95 = np.percentile(all_latencies, 95)
        consolidated_p99 = np.percentile(all_latencies, 99)

        # Include scenario details in consolidated results
        consolidated_results = {
            "scenario": name,
            "parameters": params,
            "P90": consolidated_p90,
            "P95": consolidated_p95,
            "P99": consolidated_p99
        }

        # Asynchronously save consolidated results
        consolidated_results_path = os.path.join(results_dir, "consolidated_results.json")
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(write_results, consolidated_results_path, consolidated_results)

        print(f"Consolidated P90 latency: {consolidated_p90:.4f} seconds")
        print(f"Consolidated P95 latency: {consolidated_p95:.4f} seconds")
        print(f"Consolidated P99 latency: {consolidated_p99:.4f} seconds")


if __name__ == '__main__':
    cli()
