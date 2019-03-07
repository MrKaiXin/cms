import xadmin

from users import models


# xadmin.site.register(models.User)
xadmin.site.register(models.Address)
xadmin.site.register(models.Area)