from api.cruds.post import update_expired_posts
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone='Asia/Seoul')

scheduler.add_job(update_expired_posts, "cron", day_of_week='mon-sun', hour=0, minute=11, second=30)
