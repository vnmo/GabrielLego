# Gabriel Lego Desktop Client

This repository contains a Python 2.7 implementation of a client for the Gabriel LEGO task guidance wearable cognitive assistance application [\[1\]](#references).

## Deployment
### Through Docker

The easiest way of running the client is through Docker, using the provided Docker-Compose configuration file.

First, [install Docker and Docker-Compose](https://docs.docker.com/install/).

Second, set up you local X-server to [accept connections from local containers](http://wiki.ros.org/docker/Tutorials/GUI).

Third, run the Gabriel backend by navigating to the repository and running:
```bash
docker-compose up gabriel_control gabriel_ucomm gabriel_lego
```
This will fire up containers for each of the services of Gabriel (the registry, UComm and the application engine).

Finally, run the client using Docker-Compose:
```bash
docker-compose up gabriel_lego_client
```

### Native deployment
This project is based on legacy code and requires OpenCV2 to work.
On Ubuntu 16.04, requirements can be installed with
```bash
sudo apt-get install libopencv-dev python-opencv python-qt4
``` 

Additionally, some Python libraries are required.
The recommended way of installing these is by creating a Python virtualenv and installing everything there:
```bash
virtualenv --python=python2.7 ./venv
. ./venv/bin/activate
pip install -r requirements.txt
```

Finally, run Gabriel and connect to it by running
```bash
./client.py --ip ${gabriel_ip} # for CLI interface
./ui.py --ip ${gabriel_ip} # for graphical UI
```


# References
[1] Zhuo Chen, Lu Jiang, Wenlu Hu, Kiryong Ha, Brandon Amos, Padmanabhan Pillai, Alex Hauptmann, and Mahadev Satyanarayanan. 2015. Early Implementation Experience with Wearable Cognitive Assistance Applications. In Proceedings of the 2015 workshop on Wearable Systems and Applications (WearSys '15). ACM, New York, NY, USA, 33-38. DOI=http://dx.doi.org/10.1145/2753509.2753517

# License

This software is licensed under an Apache v2.0 License.
See [License](./LICENSE) for details.
