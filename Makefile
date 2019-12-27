
locale/fire-tv.pot : plugin.py firetv.py
	pygettext3 -o locale/fire-tv.pot plugin.py firetv.py
	find locale -name "*.po" -exec msgmerge -U {} locale/fire-tv.pot \;
