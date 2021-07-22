import os
import signal
import sys
from threading import Thread

import requests
from consul import Consul, Check
from flask import Flask

consul = Consul("172.20.0.2")

SRV_NAME_1 = os.environ["SRV_NAME_1"]
SRV_NAME_2 = os.environ["SRV_NAME_2"]

SRV_PORT_1 = int(os.environ["SRV_PORT_1"])
SRV_PORT_2 = int(os.environ["SRV_PORT_2"])

app = Flask(SRV_NAME_1)


@app.route("/healthcheck")
def healthcheck():
    response = app.response_class(
        response="OK",
        status=200,
        mimetype='text'
    )
    return response


@app.route("/say_hello")
def say_hello():
    answer = requests.get(f"http://{SRV_NAME_2}.service.dc1.consul:{SRV_PORT_2}/hello")
    return answer.text + f" this is {SRV_NAME_1}!!!"


@app.route("/hello")
def hello():
    response = app.response_class(
        response=f"Hello {SRV_NAME_1}\n",
        status=200,
        mimetype='text'
    )
    return response


def exit_gracefully(*args):
    print("Graceful stop")
    consul.kv.delete(f"status/{SRV_NAME_1}")
    consul.agent.service.deregister(f"{SRV_NAME_1}_id")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    consul.kv.put(f'status/{SRV_NAME_1}', 'started')


    def run_flask():
        app.run(host="0.0.0.0", port=SRV_PORT_1)


    thread = Thread(target=run_flask)
    thread.daemon = True
    thread.start()

    consul.kv.put(f'status/{SRV_NAME_1}', 'running')
    consul.agent.service.register(SRV_NAME_1, f"{SRV_NAME_1}_id", "172.17.0.1", SRV_PORT_1,
                                  check=Check.http(f"http://172.17.0.1:{SRV_PORT_1}/healthcheck", "10s"))

    print(f"HELLO {SRV_NAME_1}: http://{SRV_NAME_1}.service.dc1.consul:{SRV_PORT_1}/hello")
    print(f"ASK FOR HELLO FROM {SRV_NAME_2}: http://{SRV_NAME_1}.service.dc1.consul:{SRV_PORT_1}/say_hello")

    thread.join()
    print("EXIT")
