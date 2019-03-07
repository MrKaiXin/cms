import xadmin

from goods import models


xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.Goods)
xadmin.site.register(models.GoodsAlbum)