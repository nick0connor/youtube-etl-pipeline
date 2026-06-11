# python-project
Python project for Revature training program

If hosting via PM2 to fetch daily API calls, you can use the command:
```
pm2 start daily.py --interpreter python --cron "0 9 * * *" --no-autorestart
```