# Data meant only for temporary use.

recently_downloaded = []

# News/announcements: the item selected for this session (or None), and a guard so
# we only pick one per session (see hand_check_news in __init__.py).
news_item = None
news_checked = False
