#
# Regular cron jobs for the karesansui package
#
0 4	* * *	root	[ -x /usr/bin/karesansui_maintenance ] && /usr/bin/karesansui_maintenance
