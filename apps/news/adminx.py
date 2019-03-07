import xadmin

from news import models


xadmin.site.register(models.NewsCategory)
xadmin.site.register(models.News)
xadmin.site.register(models.NewsAlbum)