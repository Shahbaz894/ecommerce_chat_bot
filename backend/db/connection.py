from cassandra.cluster import Cluster
from config.setting import ASTRA_DB_KEYSPACE, ASTRA_DB_HOST



cluster = Cluster(["<ASTRA_DB_HOST>"])
db_session = cluster.connect("<KEYSPACE>")
