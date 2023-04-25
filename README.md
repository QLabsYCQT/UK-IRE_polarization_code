# UK-IE Project

This repository contains the code developed to run experiments on deployed fibre between Manchester-Southport, and Southport-Portraine.

Link to project folder in shared drive [here](https://drive.google.com/drive/folders/1Fm4DN06zBZNw2_FUfHMZRcQgkJ7rD39z?usp=share_link).
## Getting started

Start by making sure you have Python installed. You can do this by running 

```python --version```

in your terminal of choice - it should return something like `Python 3.10.6`. Make sure the version is 3.8 or newer. If you don't have a suitable Python installation you can get it from the following link:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

Once you have Python installed, click the green 'Code' button above and choose an option for downloading the code to your machine. Cloning with Git is recommended, as this allows you to commit and push any changes you make to this repository. 

Note that if you download the code as a .zip file, you will also need to manually download the code from the ukie-server and yqcinst repositories manually, and put them in the relevant places. If you clones using Git, run the command `git submodule update --init` to clone them at the relevant commit. The most recent version of these repositories is not necessarily the version that is required here - following the links in the GitHub Code tab will take you to the right point in time to download each repository. 


---

### Setting up a virtual environment (optional)

This is not crucial but highly recommended - using a virtual environment on a per-repository basis means that you avoid conflicts between projects that may have different requirements. Once you have cloned or downloaded the code into a folder, navigate to that folder in your terminal. 

In order to create a virtual environment in a subfolder called `venv`, run the following command:

```bash
python -m venv venv
```
This may take some time to complete. Once that finishes running, you now have a complete Python installation local to this project. To activate the virtual environment, run the following command:

``` bash
# On Windows:
venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate
```

You should see some visual indication that you are in the virtual environment - usually `(venv)` to the left of the terminal prompt. It is sensible to verify that you have the desired version of Python in your virtual environment by again running `python --version`. Note that depending on your particular Python installation, you may have to use `python3` instead of `python` for each of these steps. If you use an editor like VS Code, you can configure it to use your virtual environment when you run a script - more info here: [https://code.visualstudio.com/docs/python/environments](https://code.visualstudio.com/docs/python/environments)

---

Whether or not you are using a virtual environment, you now need to install the project requirements - to do that, run:

```bash
python -m pip install -r requirements.txt
```

This will take some time, but when everything has installed the final step is to set up the configuration file and to optionally set set the `UKIE_CONFIG_FILE` environment variable to tell Python where to find it. To do this, run the following command:

```bash
# On Windows (PowerShell):
$Env:UKIE_CONFIG_FILE = "config.json"

# On Linux/macOS
export UKIE_CONFIG_FILE="config.json"
```
