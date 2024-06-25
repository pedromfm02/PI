from Services import URL_Source,Loading,MySql,QStore
from datetime import datetime

import logging

qd = QStore()
db = MySql()
load = Loading()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

logging.info("Starting the update")

date = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

#gets the id of the update_period that needs to update
result_time_table = db.get("SELECT id FROM update_time WHERE update_period <= %s",[date])
logging.info("Query result for date: %s is: %s",date,result_time_table)

for i in result_time_table:
    #for each id of the update_time table it will get the url sources that have that id in update_period_id 
    result_source_table = db.get("SELECT * FROM url_source WHERE update_period_id = %s",[i[0]])
    logging.info("Query result for update_period_id:%s is: %s",i,result_source_table)

    if result_source_table:
        for item in result_source_table:
            logging.info("The following Source is being updated: %s",item)
            #gets child links associated with the url source.
            child_links = db.get("SELECT url_link FROM url_child_source WHERE parent_id = %s",[item[0]])
            #deletes vectors that are from the url source
            qd.delete_vectors(item[1])
            if child_links:
                for link in child_links:
                    #deletes vectors that are from the child urls
                    qd.delete_vectors(link[0])
                db.delete_url_child_source(item[0])

            if item[2] == '':
                link_paths = []
            else:    
                link_paths = item[2].split(',')

            logging.info(f"[URL]: {item[1]},[paths]: {link_paths},[period]]: {item[6]},[descpr]: {item[3]},[wait]: {item[4]},[recur]: {bool(item[5])}")
            fonte = URL_Source(url=item[1],paths=link_paths,update_period=item[6],description=str(item[3]),wait_time=item[4],recursive=bool(item[5]))
            #loads url source.
            load.url_loader(fonte)

# After the updating of all the sources that nedded it it will update the date for the next update.
for i in result_time_table:
    logging.info("Refresh the date of the update_time table where id=%s, result: %s",i[0],db.update_time(i[0]))

logging.info("Update process finished")

