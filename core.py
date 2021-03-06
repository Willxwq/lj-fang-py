# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import settings
import model
import misc
import time
import datetime
#import urllib2
import urllib.request
import logging
import json

#logging.basicConfig(filename='/data/wwwlogs/python/sh.log', filemode="a", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)
BASE_URL = u"https://%s.lianjia.com/" % (settings.CITY)
CITY = settings.CITY

def GetHouseByCommunitylist(communitylist):
    logging.info("Get House Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_house_percommunity(community)
        except Exception as e:
            logging.error(e)
            logging.error(convertToUX(community) + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetHouseByRegionlist(regionlist=[u'xicheng']):
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logging.info("Get Onsale House Infomation in %s" % regionname)
        try:
            get_house_perregion(regionname)
        except Exception as e:
            logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetHouseNum(communitylist):
    logging.info("Get House Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_house_percommunity(community)
        except Exception as e:
            logging.error(e)
            logging.error(convertToUX(community) + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetSellByCommunitylist(communitylist):
    logging.info("Get Sell Infomation")
    starttime = datetime.datetime.now()
    page = 1;
    total = len(communitylist)
    for community in communitylist:
        try:
            logging.info("finish Sell Infomation : %d total pages %d" %(page, total))
            get_sell_percommunity(community)
            page = page + 1
        except Exception as e:
            page = page + 1
            logging.error(e)
            logging.error(convertToUX(community).decode() + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetRentByCommunitylist(communitylist):
    logging.info("Get Rent Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_rent_percommunity(community)
        except Exception as e:
            logging.error(e)
            logging.error(convertToUX(community) + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetCommunityByRegionlist(regionlist=[u'xicheng']):
    logging.info("Get Community Infomation")
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        try:
            get_community_perregion(regionname)
            logging.info(regionname + "Done")
        except Exception as e:
            logging.error(e)
            logging.error(regionname + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def GetRentByRegionlist(regionlist=[u'xicheng']):
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logging.info("Get Rent House Infomation in %s" % regionname)
        try:
            get_rent_perregion(regionname)
        except Exception as e:
            logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def get_house_percommunity(communityname):
    url = BASE_URL + u"ershoufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    if total_pages == None:
        return
        #row = model.Houseinfo.select().count()
        #raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        i = 0
        log_progress("GetHouseByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        hisprice_data_source = []
        for ultag in soup.findAll("ul", {"class":"sellListContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({u'title':housetitle.a.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('data-lj_action_housedel_id')
                    if houseID == None:
                        houseID = housetitle.a.get('data-housecode')
                    if houseID == None:
                        continue
                    info_dict.update({u'houseID':houseID})

                    houseinfo = name.find("div", {"class":"houseInfo"})
                    info = houseinfo.get_text().split('|')

                    info_dict.update({u'housetype':info[0]})
                    info_dict.update({u'square':info[1]})
                    info_dict.update({u'direction':info[2]})
                    info_dict.update({u'decoration':info[3]})
                    info_dict.update({u'floor':info[4]})
                    info_dict.update({u'years':info[5]})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    housefloorInfo = housefloor.get_text().split('   -  ')
                    info_dict.update({u'community':housefloorInfo[0]})

                    followInfo = name.find("div", {"class":"followInfo"})
                    info_dict.update({u'followInfo':followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class":"taxfree"})
                    if taxfree == None:
                        info_dict.update({u"taxtype":""})
                    else:
                        info_dict.update({u"taxtype":taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    info_dict.update({u'totalPrice':totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    info_dict.update({u'unitPrice':unitPrice.get("data-price")})
                except:
                    continue

                # Houseinfo insert into mysql
                data_source.append(info_dict)
                hisprice_data_source.append({"houseID":info_dict["houseID"], "totalPrice":info_dict["totalPrice"]})
                #model.Houseinfo.insert(**info_dict).upsert().execute()
                #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()
            break

        if data_source == [] :
            continue
        with model.database.atomic():
            logging.info("data_source : " + json.dumps(data_source))
            model.Houseinfo.insert_many(data_source).upsert().execute()
            model.Hisprice.insert_many(hisprice_data_source).upsert().execute()
        time.sleep(1)

def get_house_percommunity_old(communityname):
    url = BASE_URL + u"ershoufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    
    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class":"clear"})
        i = 0
        log_progress("GetHouseByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        hisprice_data_source = []
        for name in nameList: # per house loop
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.find("div", {"class":"title"})
                info_dict.update({u'title':housetitle.a.get_text().strip()})
                info_dict.update({u'link':housetitle.a.get('href')})

                houseaddr = name.find("div", {"class":"address"})
                if CITY == 'bj':
                    info = houseaddr.div.get_text().split('/')
                else:
                    info = houseaddr.div.get_text().split('|')
                info_dict.update({u'community':info[0].strip()})
                info_dict.update({u'housetype':info[1].strip()})
                info_dict.update({u'square':info[2].strip()})
                info_dict.update({u'direction':info[3].strip()})
                info_dict.update({u'decoration':info[4].strip()})

                housefloor = name.find("div", {"class":"flood"})
                floor_all = housefloor.div.get_text().split('-')[0].strip().split(' ')
                info_dict.update({u'floor':floor_all[0].strip()})
                info_dict.update({u'years':floor_all[-1].strip()})

                followInfo = name.find("div", {"class":"followInfo"})
                info_dict.update({u'followInfo':followInfo.get_text()})

                tax = name.find("div", {"class":"tag"})
                info_dict.update({u'taxtype':tax.get_text().strip()})

                totalPrice = name.find("div", {"class":"totalPrice"})
                info_dict.update({u'totalPrice':totalPrice.span.get_text()})

                unitPrice = name.find("div", {"class":"unitPrice"})
                info_dict.update({u'unitPrice':unitPrice.get('data-price')})
                info_dict.update({u'houseID':unitPrice.get('data-hid')})
            except:
                continue
            # houseinfo insert into mysql
            data_source.append(info_dict)
            hisprice_data_source.append({"houseID":info_dict["houseID"], "totalPrice":info_dict["totalPrice"]})
            #model.Houseinfo.insert(**info_dict).upsert().execute()
            #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            model.Houseinfo.insert_many(data_source).upsert().execute()
            model.Hisprice.insert_many(hisprice_data_source).upsert().execute()
        time.sleep(1)

def get_sell_percommunity(communityname):
    url = BASE_URL + u"chengjiao/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    logging.info(url)
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    
    if total_pages == None:
        row = model.Sellinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"chengjiao/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetSellByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"listContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID':houseID.strip()})

                    house = housetitle.get_text().strip().split(' ')
                    info_dict.update({u'community':house[0].strip()})
                    info_dict.update({u'housetype':house[1].strip()})
                    info_dict.update({u'square':house[2].strip()})

                    houseinfo = name.find("div", {"class":"houseInfo"})
                    info = houseinfo.get_text().split('|')
                    info_dict.update({u'direction':info[0].strip()})
                    info_dict.update({u'status':info[1].strip()})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    floor_all = housefloor.get_text().strip().split(' ')
                    info_dict.update({u'floor':floor_all[0].strip()})
                    info_dict.update({u'years':floor_all[-1].strip()})

                    followInfo = name.find("div", {"class":"source"})
                    info_dict.update({u'source':followInfo.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    if totalPrice.span is None:
                        info_dict.update({u'totalPrice':totalPrice.get_text().strip()})
                    else:
                        info_dict.update({u'totalPrice':totalPrice.span.get_text().strip()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    if unitPrice.span is None:
                        info_dict.update({u'unitPrice':unitPrice.get_text().strip()})
                    else:
                        info_dict.update({u'unitPrice':unitPrice.span.get_text().strip()})

                    dealDate= name.find("div", {"class":"dealDate"})
                    info_dict.update({u'dealdate':dealDate.get_text().strip().replace('.','-')})

                    aa = name.find("span", {"class":"dealCycleTxt"})

                    aaa = aa.findAll("span")

                    info_dict.update({u'listing_price' : aaa[0].get_text().strip()[2:-1]})
                    info_dict.update({u'cycle' : aaa[1].get_text().strip()[4:-1]})
                    info_dict.update({u'browse_num' : ''})
                    info_dict.update({u'attention_num' : ''})
                    info_dict.update({u'view_num' : ''})
                    info_dict.update({u'adjust_num' : ''})

                    #communityinfo = get_sellInfo_by_url(housetitle.a.get('href'))
                    #for key, value in communityinfo.items():
                        #info_dict.update({key:value})

                except:
                    continue
                # Sellinfo insert into mysql
                data_source.append(info_dict)
                #model.Sellinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Sellinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)

def get_community_perregion(regionname=u'xicheng'):
    url = BASE_URL + u"xiaoqu/" + regionname +"/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages_com(url)
    
    if total_pages == None:
        row = model.Community.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"xiaoqu/" + regionname +"/pg%d/" % page
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class":"clear"})
        i = 0
        log_progress("GetCommunityByRegionlist", regionname, page+1, total_pages)
        data_source = []
        for name in nameList: # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("div", {"class":"title"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.a.get('href')
                info_dict.update({u'title':title})
                info_dict.update({u'link':link})

                district = name.find("a", {"class":"district"})
                info_dict.update({u'district':district.get_text()})
                
                bizcircle = name.find("a", {"class":"bizcircle"})
                info_dict.update({u'bizcircle':bizcircle.get_text()})

                tagList = name.find("div", {"class":"tagList"})
                info_dict.update({u'tagList':tagList.get_text().strip('\n')})

                onsale = name.find("a", {"class":"totalSellCount"})
                info_dict.update({u'onsale':onsale.span.get_text().strip('\n')})

                onrent = name.find("a", {"title":title+u"租房"})
                info_dict.update({u'onrent':onrent.get_text().strip('\n').split(u'套')[0]})

                info_dict.update({u'id':name.get('data-housecode')})

                price = name.find("div", {"class":"totalPrice"})
                info_dict.update({u'price':price.span.get_text().strip('\n')})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.items():
                    info_dict.update({key:value})

            except:
                continue
            # communityinfo insert into mysql
            data_source.append(info_dict)
            #model.Community.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Community.insert_many(data_source).upsert().execute()
        time.sleep(1)

def get_rent_percommunity(communityname):
    url = BASE_URL + u"zufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"rent/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("div", {"class":"content__list"}):
            for name in ultag.find_all("div", {"class":"content__list--item"}):
                log_progress("GetRentByCommunitylist", communityname, page+1, total_pages)
                i = i + 1
                info_dict = {}
                tempStr = ''
                try:
                    housetitleOb = name.find("p", {"class":"content__list--item--title"})
                    housetitle = housetitleOb.find("a")
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID':houseID})

                    tempInfo = name.find("p", {"class":"content__list--item--des"})
                    for tempData in tempInfo.find_all("a"):
                        tempStr += tempData.get_text().strip()

                    info_dict.update({u'region':tempStr})

                    info_dict.update({u'zone':tempInfo.get_text().strip()})

                    info_dict.update({u'meters':tempInfo.get_text().strip()})

                    other = name.find("span", {"class":"hide"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("i", {"class":"content__item__tag--is_subway_house"})
                    if subway is None:
                        info_dict.update({u'subway':''})
                    else:
                        info_dict.update({u'subway':subway.span.get_text().strip()})

                    decoration = name.find("i", {"class":"content__item__tag--decoration"})
                    if decoration is None:
                        info_dict.update({u'decoration':''})
                    else:
                        info_dict.update({u'decoration':decoration.span.get_text().strip()})

                    heating = name.find("i", {"class":"content__item__tag--two_bathroom"})
                    if decoration is None:
                        info_dict.update({u'heating':''})
                    else:
                        info_dict.update({u'heating':heating.span.get_text().strip()})

                    priceT = name.find("span", {"class":"content__list--item-price"})
                    price = priceT.find("em")
                    info_dict.update({u'price':int(price.span.get_text().strip())})

                    pricepre = name.find("p", {"class":"content__list--item--time oneline"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)

def get_rent_percommunity_bak(communityname):
    url = BASE_URL + u"zufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"rent/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"info-panel"})
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID':houseID})

                    region = name.find("span", {"class":"region"})
                    info_dict.update({u'region':region.get_text().strip()})

                    zone = name.find("span", {"class":"zone"})
                    info_dict.update({u'zone':zone.get_text().strip()})

                    meters = name.find("span", {"class":"meters"})
                    info_dict.update({u'meters':meters.get_text().strip()})

                    other = name.find("div", {"class":"con"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("span", {"class":"fang-subway-ex"})
                    if subway is None:
                        info_dict.update({u'subway':""})
                    else:
                        info_dict.update({u'subway':subway.span.get_text().strip()})

                    decoration = name.find("span", {"class":"decoration-ex"})
                    if decoration is None:
                        info_dict.update({u'decoration':""})
                    else:
                        info_dict.update({u'decoration':decoration.span.get_text().strip()})

                    heating = name.find("span", {"class":"heating-ex"})
                    info_dict.update({u'heating':heating.span.get_text().strip()})

                    price = name.find("div", {"class":"price"})
                    info_dict.update({u'price':int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class":"price-pre"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)

def get_house_perregion(district):
    url = BASE_URL + u"ershoufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetHouseByRegionlist", district, page+1, total_pages)
        data_source = []
        hisprice_data_source = []
        for ultag in soup.findAll("ul", {"class":"sellListContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({u'title':housetitle.a.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('data-housecode')
                    info_dict.update({u'houseID':houseID})


                    houseinfo = name.find("div", {"class":"houseInfo"})
                    if CITY == 'bj':
                        info = houseinfo.get_text().split('/')
                    else:
                        info = houseinfo.get_text().split('|')
                    info_dict.update({u'housetype':info[0]})
                    info_dict.update({u'square':info[1]})
                    info_dict.update({u'direction':info[2]})
                    info_dict.update({u'decoration':info[3]})
                    info_dict.update({u'floor':info[4]})
                    info_dict.update({u'years':info[5]})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    housefloorInfo = housefloor.get_text().split('   -  ')
                    info_dict.update({u'community':housefloorInfo[0]})

                    followInfo = name.find("div", {"class":"followInfo"})
                    info_dict.update({u'followInfo':followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class":"taxfree"})
                    if taxfree == None:
                        info_dict.update({u"taxtype":""})
                    else:
                        info_dict.update({u"taxtype":taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    info_dict.update({u'totalPrice':totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    info_dict.update({u'unitPrice':unitPrice.get("data-price")})
                except:
                    continue

                # Houseinfo insert into mysql
                data_source.append(info_dict)
                hisprice_data_source.append({"houseID":info_dict["houseID"], "totalPrice":info_dict["totalPrice"]})
                #model.Houseinfo.insert(**info_dict).upsert().execute()
                #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            model.Houseinfo.insert_many(data_source).upsert().execute()
            model.Hisprice.insert_many(hisprice_data_source).upsert().execute()
        time.sleep(1)

def get_rent_perregion(district):
    url = BASE_URL + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_rent_total_pages(url)
    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)
    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"zufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByRegionlist", district, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("div", {"class":"content__list"}):
            for name in ultag.find_all("div", {"class":"content__list--item"}):
                i = i + 1
                info_dict = {}
                tempStr = ''
                try:
                    housetitleOb = name.find("p", {"class":"content__list--item--title"})
                    housetitle = housetitleOb.find("a")
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.get('href')})
                    houseID = housetitle.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID':houseID})

                    tempInfo = name.find("p", {"class":"content__list--item--des"})
                    for tempData in tempInfo.find_all("a"):
                        tempStr += tempData.get_text().strip()

                    info_dict.update({u'region':tempStr})

                    info_dict.update({u'zone':tempInfo.get_text().strip()})

                    info_dict.update({u'meters':tempInfo.get_text().strip()})

                    other = name.find("span", {"class":"hide"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("i", {"class":"content__item__tag--is_subway_house"})
                    if subway is None:
                        info_dict.update({u'subway':''})
                    else:
                        info_dict.update({u'subway':subway.get_text().strip()})

                    decoration = name.find("i", {"class":"content__item__tag--decoration"})
                    if decoration is None:
                        info_dict.update({u'decoration':''})
                    else:
                        info_dict.update({u'decoration':decoration.get_text().strip()})

                    heating = name.find("i", {"class":"content__item__tag--two_bathroom"})
                    if decoration is None:
                        info_dict.update({u'heating':''})
                    else:
                        info_dict.update({u'heating':heating.get_text().strip()})

                    priceT = name.find("span", {"class":"content__list--item-price"})
                    price = priceT.find("em")
                    info_dict.update({u'price':int(price.get_text().strip())})

                    pricepre = name.find("p", {"class":"content__list--item--time oneline"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            #log_progress("GetRentByRegionlist", data_source, 1, 1)
            model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)

def get_rent_perregion_bak(district):
    url = BASE_URL + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_rent_total_pages(url)
    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"zufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByRegionlist", district, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"info-panel"})
                    info_dict.update({u'title':housetitle.h2.a.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get("href")})
                    houseID = name.get("data-housecode")
                    info_dict.update({u'houseID':houseID})

                    region = name.find("span", {"class":"region"})
                    info_dict.update({u'region':region.get_text().strip()})

                    zone = name.find("span", {"class":"zone"})
                    info_dict.update({u'zone':zone.get_text().strip()})

                    meters = name.find("span", {"class":"meters"})
                    info_dict.update({u'meters':meters.get_text().strip()})

                    other = name.find("div", {"class":"con"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("span", {"class":"fang-subway-ex"})
                    if subway == None:
                        info_dict.update({u'subway':""})
                    else:
                        info_dict.update({u'subway':subway.span.get_text().strip()})

                    decoration = name.find("span", {"class":"decoration-ex"})
                    if decoration == None:
                        info_dict.update({u'decoration': ""})
                    else:
                        info_dict.update({u'decoration':decoration.span.get_text().strip()})

                    heating = name.find("span", {"class":"heating-ex"})
                    if decoration == None:
                        info_dict.update({u'heating': ""})
                    else:
                        info_dict.update({u'heating':heating.span.get_text().strip()})

                    price = name.find("div", {"class":"price"})
                    info_dict.update({u'price':int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class":"price-pre"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_communityinfo_by_url(url):
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class":"xiaoquInfoItem"})
    res = {}
    if communityinfos == []:
        res.update({year:''})
        res.update({housetype:''})
        res.update({cost:''})
        res.update({service:''})
        res.update({company:''})
        res.update({building_num:''})
        res.update({house_num:''})
    else:
        for info in communityinfos:
            key_type = {
            u"建筑年代": u'year',
            u"建筑类型": u'housetype',
            u"物业费用": u'cost',
            u"物业公司": u'service',
            u"开发商": u'company',
            u"楼栋总数": u'building_num',
            u"房屋总数": u'house_num',
            }
            try:
                key = info.find("span",{"xiaoquInfoLabel"})
                value = info.find("span",{"xiaoquInfoContent"})
                key_info = key_type[key.get_text().strip()]
                value_info = value.get_text().strip()
                res.update({key_info:value_info})

            except:
                continue
    return res

def get_sellInfo_by_url(url):
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    sellInfoMsg = soup.find("div", {"class":"msg"})
    res = {}
    num = 0
    if sellInfoMsg == []:
        res.update({cycle:''})
        res.update({listing_price:''})
        res.update({adjust_num:''})
        res.update({view_num:''})
        res.update({attention_num:''})
        res.update({browse_num:''})
    else:
        sellInfoMsg = sellInfoMsg.findAll("label")
        key_type = {
                    1: u'listing_price',
                    2: u'cycle',
                    3: u'adjust_num',
                    4: u'view_num',
                    5: u'attention_num',
                    6: u'browse_num',
                    }
        for info in sellInfoMsg:
            try:
                num += 1;
                key_info = key_type[num]
                value_info = info.get_text().strip()
                res.update({key_info:value_info})
            except:
                continue
    return res

def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logging.error("Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False

def log_progress(function, address, page, total):
    logging.info("Progress: %s %s: current page %d total pages %d" %(function, address, page, total))

def convertToUX(content):
    return content.encode("unicode_escape")

    tmp = ""
    for cr in content:
        if (cr=="u" or cr=="'"):
            tmp = tmp + cr
            continue
        tmp = tmp + repr(cr).replace("u'", "").replace("'","")
    return tmp.encode("utf-8").decode("unicode_escape").encode("utf-8")