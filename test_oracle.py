from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import re
import geocoder
import cx_Oracle


cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_10")

@dataclass
class Business:
    """holds business data
    """
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    long: float = None
    lat: float = None

@dataclass
class BusinessList:
    """holds list of Business objects, 
       and save to both excel and csv
    """
    business_list : list[Business] = field(default_factory=list)
    
    def dataframe(self):
        """transform business_list to pandas dataframe 
        Returns: pandas dataframe
        """
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")
    
    def save_to_excel(self, filename):
        """saves pandas dataframe to excel (xlsx) file
        Args:
            filename (str): filename
        """   
        # writer = pd.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter', options={'encoding': 'utf-8'})
        self.dataframe().to_excel(f'{filename}.xlsx', index=False)
    
    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file
        Args:
            filename (str): filename
        """
        self.dataframe().to_csv(f'{filename}.csv', index=False,encoding='utf-16')

    


def main():
    
    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto('https://www.google.com/maps', timeout=60000)
        # wait is added for dev phase. can remove it in production
        # page.wait_for_timeout(5000)
        citi_list_1 = ["Bac Lieu",
            "Ben Thuy",
            "Ben Tre",
            "Bien Hoa",
            "Buon Me Thuot",
            "Cam Ranh"
            ,
            "Can Tho",
            "Cao Lanh",
            "Cho Lon",
            "Con Son",
            "Da Lat",
            "Da Nang",
            "Ha Long",
            "Hai Duong",
            "Haiphong",
            "Hanoi",
            "Ho Chi Minh City",
            "Hoa Binh",
            "Hue",
            "Kon Tum",
            "Lao Cai",
            "Long Xuyen",
            "My Tho",
            "Nam Dinh",
            "Nha Trang",
            "Phan Thiet",
            "Pleiku",
            "Quang Ngai",
            "Qui Nhon",
            "Rach Gia",
            "Sa Dec",
            "Tay Ninh",
            "Thai Binh",
            "Thai Nguyen",
            "Thanh Hoa",
            "Thu Dau Mot",
            "Tuy Hoa",
            "Vinh",
            "Vinh Long",
            "Vung Tau"
            ]
        # citi_list_1=["Hung Yen", "Ha Noi"]
        for x in citi_list_1:
            page.locator('//input[@id="searchboxinput"]').fill(f'Hotels {x}')
            # page.wait_for_timeout(3000)
            
            page.keyboard.press('Enter')
            # page.wait_for_timeout(5000)
            
            # scrolling 
            page.hover('(//div[@role="article"])[1]')

            # this variable is used to detect if the bot
            # scraped the same number of listings in the previous iteration
            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)
                
                if page.locator('//div[@role="article"]').count() >= total:
                    listings = page.locator('//div[@role="article"]').all()[:total]
                    print(f'Total Scraped: {len(listings)}')
                    break
                else:
                    # logic to break from loop to not run infinitely 
                    # in case arrived at all available listings
                    if page.locator('//div[@role="article"]').count() == previously_counted:
                        listings = page.locator('//div[@role="article"]').all()
                        print(f'Arrived at all available\nTotal Scraped: {len(listings)}')
                        break
                    else:
                        previously_counted = page.locator('//div[@role="article"]').count()
                        print(f'Currently Scraped: ', page.locator('//div[@role="article"]').count())
            
            business_list = BusinessList()
            # scraping
            for listing in listings:
            
                listing.click()
                # page.wait_for_timeout(5000)
                
                name_xpath = '//h1[contains(@class, "fontHeadlineLarge")]'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                reviews_span_xpath = '//span[@role="img"]'
                
                business = Business()
                
                if page.locator(name_xpath).count() > 0:
                    business.name = page.locator(name_xpath).inner_text()
                else:
                    business.name = ''
                if page.locator(address_xpath).count() > 0:
                    business.address = page.locator(address_xpath).inner_text()
                    if page.locator(address_xpath).inner_text() != None:
                        result = geocoder.arcgis(location=page.locator(address_xpath).inner_text())
                        business.lat,business.long = result.latlng
                    else:
                        business.lat=''
                        business.long=''
                else:
                    business.address = ''
                if page.locator(website_xpath).count() > 0:
                    business.website = page.locator(website_xpath).inner_text()
                else:
                    business.website = ''
                if page.locator(phone_number_xpath).count() > 0:
                    business.phone_number = page.locator(phone_number_xpath).inner_text()
                else:
                    business.phone_number = ''
                if listing.locator(reviews_span_xpath).count() > 0:
                    business.reviews_average = float(listing.locator(reviews_span_xpath).get_attribute('aria-label').split()[0].replace(',','.').strip())
                    business.reviews_count = int(re.sub(r'[\W_]','',listing.locator(reviews_span_xpath).get_attribute('aria-label').split()[2].strip()))
                    # print(listing.locator(reviews_span_xpath).get_attribute('aria-label'))
                else:
                    business.reviews_average = ''
                    business.reviews_count = ''
                    
                business_list.business_list.append(business)
                df= business_list.dataframe()
                df['long']=df['long'].fillna(0)
                df['lat']= df['lat'].fillna(0)
                # print(df)
                dataInsertionTuples= [tuple(x) for x in df.values]
                print(dataInsertionTuples)
                connStr= 'test_code/Oracle123@10.0.223.163:1521/bcadb'
                conn = None

                #correct the instant client path
                
                try:
                    conn= cx_Oracle.connect(connStr)
                    cur = conn.cursor()
                    sqlTxt='INSERT INTO test_insert\
                            (name, address, website, phone_number, reviews_count, reviews_average, long_loc, lat_loc)\
                            VALUES (:1, :2, :3, :4, :5, :6, :7, :8)'
                    cur.executemany(sqlTxt, [x for x in dataInsertionTuples])
                    rowCount= cur.rowcount
                    print("number of rows inserted", rowCount)

                    #commit
                    conn.commit()

                except Exception as err:
                    print('Error while inserting rows')
                    print(err)
                finally:
                    if(conn):
                        #close the cursor object to avoid memory leaks
                        cur.close()
                        #close the connection as well
                        conn.close()
                print("Insert completed")              
        browser.close()

def ETL_SQL():
    # cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_10")

    conn=None
    connStr= 'test_code/Oracle123@10.0.223.163:1521/bcadb'
    try:
        conn=cx_Oracle.connect(connStr)
        cur= conn.cursor()

        sqlTxt='DELETE FROM TEST_TRANSFORM where name is null'
        cur.execute(sqlTxt)
        conn.commit()

        sqlTxt='insert into test_transform (\
                select name, address, website, phone_number, trunc(avg(reviews_count)), round(avg(reviews_average),1), long_loc, lat_loc\
                from test_insert\
                where name is not null\
                group by name, address, website, phone_number, long_loc, lat_loc)'
        cur.execute(sqlTxt)
        conn.commit()

        #Delete duplcate post-insert
        sqlTxt='DELETE FROM TEST_TRANSFORM A\
            WHERE ROWID > (SELECT MIN(ROWID) FROM TEST_TRANSFORM B\
            WHERE A.NAME= B.NAME\
            AND A.ADDRESS= B.ADDRESS\
            AND A.WEBSITE=B.WEBSITE\
            AND A.PHONE_NUMBER= B.PHONE_NUMBER\
            AND A.REVIEWS_COUNT= B.REVIEWS_COUNT\
            AND A.REVIEWS_AVERAGE= B.REVIEWS_AVERAGE\
            AND A.LONG_LOC= B.LONG_LOC\
            AND A.LAT_LOC= B.LAT_LOC)'
        cur.execute(sqlTxt)
        conn.commit()

        print('finished transform')
    except Exception as err:
        print('Error while inserting rows')
        print(err)
    finally:
        if(conn):
        #close the cursor object to avoid memory leaks
            cur.close()
            #close the connection as well
            conn.close()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()
    
    if args.search:
        search_for = args.search
    else:
        citi_list = ["Bac Lieu",
            "Ben Thuy",
            "Ben Tre",
            "Bien Hoa",
            "Buon Me Thuot",
            "Cam Ranh",
            "Can Tho",
            "Cao Lanh",
            "Cho Lon",
            "Con Son",
            "Da Lat",
            "Da Nang",
            "Ha Long",
            "Hai Duong",
            "Haiphong",
            "Hanoi",
            "Ho Chi Minh City",
            "Hoa Binh",
            "Hue",
            "Kon Tum",
            "Lao Cai",
            "Long Xuyen",
            "My Tho",
            "Nam Dinh",
            "Nha Trang",
            "Phan Thiet",
            "Pleiku",
            "Quang Ngai",
            "Qui Nhon",
            "Rach Gia",
            "Sa Dec",
            "Tay Ninh",
            "Thai Binh",
            "Thai Nguyen",
            "Thanh Hoa",
            "Thu Dau Mot",
            "Tuy Hoa",
            "Vinh",
            "Vinh Long",
            "Vung Tau"]
        for i in citi_list:
        # in case no arguments passed
        # the scraper will search by defaukt for:
            search_for = f'Hotels {i}'
    
    # total number of products to scrape. Default is 10
    if args.total:
        total = args.total
    else:
        total = 5
        
    main()
    ETL_SQL()

