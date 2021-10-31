python garde.py --file input/`date +%Y-%m-%d`.txt
cd calendar
git commit -m 'publish' *.ics
git push dokku master
cd ..
