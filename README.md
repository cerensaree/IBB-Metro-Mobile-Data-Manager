## Proje Hakkında
Projede ElasticSearch'ten İstanbul M2 metrosundaki her istasyon için merdiven ve asansör arızası verileri çekilir ve hem database ortamına hem de önbelleğe yazdırılır, bu veriler 20 saniyede bir silinerek aynı işlemi yapmaya devam etmektedir.

## Kullanılan Kütüphaneler ve İndirme Linkleri
[![Used Library](https://img.shields.io/badge/library-psycopg2-blue)](https://pypi.org/project/psycopg2/)
[![Used Library](https://img.shields.io/badge/library-elasticsearch_dsl-blue)](https://pypi.org/project/elasticsearch-dsl/)
[![Used Library](https://img.shields.io/badge/library-time-blue)](https://docs.python.org/3/library/time.html)

## Versiyonlar
- elasticsearch==6.8.2
- elasticsearch-dsl==6.4.0
- psycopg2==2.9.9

## Kullanım
Proje çalıştırıldığında ilk önce elasticSearch sunucusuyla bağlantı kurulur. Bu kod "metro-elapsed" adlı bir indeks üzerinden belirli filtreler aracılığıyla arama yapmayı ve burdan çıkan sorgu sonuçlarını DataBase'e Line|Station|Section|Equipment|State|Tag|StartTime|Value şeklinde yazdırmayı amaçlar. DataBase yazdırılan bu veriler her 60 saniyede bir kontrol edilir ve "Tag" değişkeni (arıza durumu) "elapsedContinue" dan "elapsedEnd" e düşenleri database'den siler ve yerine elasticSearch aracılığıyla arıza durumu devam eden (elapsedContinue) asansör ve yürüyen merdiven bilgilerini yazdırır. 

## Environment Variables

- datetime months ago: "AGO_VALUE"
    - value= "180"
- error_limit: "ERROR_LIMIT"
    - value= "3"

### ElasticSearch Variables
- elasticSearch URL: "ELASTIC_SEARCH_URL" 
    - value= "http://10.8.0.34:80/esearch"
- host name: "ELASTICSEARCH"
    - value= "admin"
- password: "ELASTIC_PSWRD"
    - value= "Fs2020.."
- index: "SEARCH-INDEX"
    - value= "metro-elapsed"

### Redis Variables
- host name: "REDISHOST"
    - value= "localhost"
- port: "REDIS_PORT"
    - value= "6379"
- db: "REDIS_DB_VALUE"
    -value= "0"

### Database Variables
* host name: "METRO_HOST"
    * value= cargo.staj.svc.cluster.mantam
* database name= "METRO_DB"
    * value= cargo
* username= "METRODB"
    * value= cargo
* password = "METRO_PSWRD"
    * value= cargodb.12345
* port= "DB_PORT"
    * VALUE= 8080

## DBeaver Üzerinden Oluşturulan Tablo
```javascript
CREATE TABLE tbl_metro (
    id VARCHAR(255) NOT NULL UNIQUE,
    line VARCHAR(255) NOT NULL,
    station VARCHAR(255) NOT NULL,
    section VARCHAR(255) NOT NULL,
    equipment VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    tag VARCHAR(255) NOT NULL,
    startTime TIMESTAMP,
    value FLOAT
);
```

