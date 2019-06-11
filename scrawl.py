import model
import settings
import logging
logging.basicConfig(filename=settings.LOGPATH, filemode="a", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)
import core
import sys

def get_communitylist():
	res = []
	#for community in model.Community.select().where(model.Community.useFlg == 1):
	for community in model.Community.select():
		res.append(community.title)
	return res

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    regionlist = settings.REGIONLIST # only pinyin support
    model.database_init()
    #core.GetHouseByRegionlist(regionlist)
    #core.GetRentByRegionlist(regionlist)
    #core.GetCommunityByRegionlist(regionlist) # Init,scrapy celllist and insert database; could run only 1st time
    communitylist = get_communitylist() # Read celllist from database
    core.GetSellByCommunitylist(communitylist)

