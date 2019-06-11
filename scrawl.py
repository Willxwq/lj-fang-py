#import core
import model
import settings
import logging

def get_communitylist():
	res = []
	#for community in model.Community.select().where(model.Community.useFlg == 1):
	for community in model.Community.select():
		res.append(community.title)
	return res

if __name__=="__main__":
    logging.basicConfig(filename='/data/wwwlogs/python/sh.log', filemode="a", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info('this is a loggging info message')
    logging.error('this is a loggging info message')

