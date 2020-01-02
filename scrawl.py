# -*- coding: utf-8 -*-
import model
import settings
import logging
logging.basicConfig(filename=settings.LOGPATH, filemode="a", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
import core

def get_communitylist():
	res = []
	#for community in model.Community.select().where(model.Community.useFlg == 0):
	for community in model.Community.select():
		res.append(community.title)
	return res

if __name__=="__main__":
    regionlist = settings.REGIONLIST # only pinyin support
    model.database_init()
    communitylist = get_communitylist() # Read celllist from database
    #core.GetHouseByCommunitylist(communitylist) #根据小区
    #core.GetHouseByRegionlist(regionlist) #根据区域
    #core.GetRentByRegionlist(regionlist)
    #core.GetCommunityByRegionlist(regionlist) # Init,scrapy celllist and insert database; could run only 1st time
    core.GetSellByCommunitylist(communitylist)

