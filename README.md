1. Open Terminal on your Mac.
2. Navigate to your project directory:
cd /path/to/your/project
3. python3 -m venv .venv
This creates a .venv folder in your project, containing an isolated Python installation.
4. Activate the environment:
source .venv/bin/activate
5. Your terminal prompt will change to show (.venv) at the beginning, indicating it's active.
Install packages: Use pip as usual; packages will install only in this environment.
6. pip install requests flask
7. To Deactivate the environment: When you're done working, simply type:
deactivate
The prompt will return to normal, and you'll be using your system's global Python again. 


chmod 777 run.sh


./run.sh
