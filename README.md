<h1 align="center">
  <br>
  <a href="http://github.com/Star-Sync"><img src="https://x5a81d4mva.ufs.sh/f/vO1KpS4QDgU0XomMFhvzcj1LEp8Nb3ZI0koeyJSitX9s2lWF" alt="StarSync-Core" width="200"></a>
  <br>
  StarSync Core
  <br>
</h1>


## How To Use

To clone and run the `ss-core` service, you'll need Docker installed on your computer.

```bash
# Clone this repository
$ git clone https://github.com/Star-Sync/ss-core

# Go into the repository
$ cd ss-core

# Go into the docker directory
$ cd docker

# Run the container
$ docker compose up --build
```

## How to run tests
```bash
# Install testing packages
$ pip install -r requirements-dev.txt

# Run tests and generate coverage report
$ python -m pytest --cov=./ --cov-report=html --cov-fail-under=50
```
View the coverage report by opening `htmlcov/index.html` in a browser.
