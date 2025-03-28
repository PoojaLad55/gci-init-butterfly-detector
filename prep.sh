sudo apt install fswebcam

gciFilePath=$(pwd)

pip install virtualenv
python3 -m venv .fly

pip install -r requirements.txt

chmod +x alternate.sh

(crontab -l; echo "@reboot $gciFilePath/alternate.sh") | crontab -
