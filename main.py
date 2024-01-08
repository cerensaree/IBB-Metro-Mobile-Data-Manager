import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import time
import redis
import json
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger("metro-data-manager")
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
)
logger.addHandler(handler)

elasticlogger = logging.getLogger('elasticsearch')
elasticlogger.setLevel(logging.WARNING)

six_months_ago = datetime.now() - timedelta(days=int(os.environ.get("AGO_VALUE", "180")))

es_client = Elasticsearch([os.environ.get("ELASTIC_SEARCH_URL", "http://10.8.0.34:80/esearch")], http_auth=(
    os.environ.get("ELASTICSEARCH", "admin"), os.environ.get("ELASTIC_PSWRD", "Fs2020..")))
redis_cache = redis.StrictRedis(host=os.environ.get("REDISHOST", "metro-redis.metroprojecttest.svc.cluster.mantam"),
                                port=int(os.environ.get("REDIS_PORT", "6379")),
                                db=os.environ.get("REDIS_DB_VALUE", "0"),
                                password=os.environ.get("REDIS_PASS", "metroapi"))


def run():
    error_limit = int(os.environ.get("ERROR_LIMIT", "5"))

    while True:
        try:
            s = Search(using=es_client, index=os.environ.get("SEARCH-INDEX", "metro-elapsed"))

            line_filter = Q('term', line="M2")
            tag_filter = Q('term', tag="elapsedContinue")
            section_query = Q('dis_max', queries=[
                Q('term', section='ASANSOR'),
                Q('term', section='YURUYEN MERDIVEN')
            ])
            bool_query = Q('dis_max', queries=[
                Q('term', state='MerdivenGenelArıza'),
                Q('term', state='MerdivenAcilDurdurma'),
                Q('term', state='AsansörGenelArıza')
            ])
            # 2023-10-26T13:50:42.654252 [:-3] son 3 hane alınmayacak.
            # print(f"{datetime.now().isoformat()[:-3]}Z") 

            date_range_filter = Q('range',
                                  startTime={'gte': six_months_ago.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"})

            combined_query = line_filter & tag_filter & section_query & bool_query & date_range_filter

            s = s.query(combined_query)
            s = s.extra(size=10000)

            response = s.execute()

            db_connection = psycopg2.connect(
                host=os.environ.get("METRO_HOST", "metro-db.metroprojecttest.svc.cluster.mantam"),
                database=os.environ.get("METRO_DB", "metro"),
                user=os.environ.get("METRODB", "metro"),
                password=os.environ.get("METRO_PSWRD", "metrodb.12345")
            )
            cursor = db_connection.cursor()

            cursor.execute("DELETE FROM tbl_metro")

            for hit in response:
                # cursor.execute("SELECT COUNT(*) FROM tbl_metro WHERE line = %s AND station = %s AND section = %s AND equipment = %s", (line, station, section, equipment, state))
                # count = cursor.fetchone()[0]

                # if count == 0:
                insert_query = """
                INSERT INTO tbl_metro (line, station, section, equipment, state, tag, startTime, value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                data = (hit.line, hit.station, hit.section, hit.equipment, hit.state, hit.tag, hit.startTime, hit.value)
                cursor.execute(insert_query, data)

            db_connection.commit()
            cursor.close()

            result = []

            for data in response:
                line = data.line
                station = data.station
                equipment = data.equipment
                section = data.section
                state = data.state
                starttime = data.startTime

                line_info = next((item for item in result if item["line"] == line), None)

                if line_info is None:
                    line_info = {
                        "line": line,
                        "stations": []
                    }
                    result.append(line_info)

                station_info = next((item for item in line_info["stations"] if item["name"] == station), None)

                if station_info is None:
                    station_info = {
                        "name": station,
                        "equipments": []
                    }
                    line_info["stations"].append(station_info)

                equipment_info = next((item for item in station_info["equipments"] if
                                       item["name"] == equipment and item["section"] == section), None)
                if equipment_info is None:
                    equipment_info = {
                        "name": equipment,
                        "section": section,
                        "starttime": starttime,
                        "states": []
                    }
                    station_info["equipments"].append(equipment_info)

                equipment_info["states"].append(state)

            jsoncachedata = json.dumps(result)

            redis_cache.flushall()

            redis_cache.set('cache_data', jsoncachedata)

            logger.info("New Data Added..")
            time.sleep(int(os.environ.get("LOOPTIME", "20")))

        except Exception as e:
            logger.error(f"An error occurred while adding data: {str(e)}")
            if db_connection:
                db_connection.close()
                logger.info("The database connection has been terminated..")
            error_limit -= 1
            if error_limit <= 0:
                logger.info("Error Limit..")
                break
            logger.critical(f"Waiting {os.environ.get('LOOPTIME', '20')} seconds before retry...")
            time.sleep(int(os.environ.get("LOOPTIME", "20")))
