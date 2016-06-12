This directory contains third-party dependencies installed with `pip`.

First time setup :
Run this command to add 3rd party library flask_cors to your project.  The snapshot will be deployed to google app engine.
```
cd <project_directoy>
pip install flask_cors -t lib
```

To run locally
```
dev_appserver.py app.yaml
```
