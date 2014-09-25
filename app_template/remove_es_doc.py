from elasticsearch import Elasticsearch

es = Elasticsearch([{"host":"9.181.27.234","port":9200}])

all_docs = es.search(index="grafana-dash",doc_type="dashboard")
#print(all_docs)
for doc in all_docs["hits"]["hits"]:
	did = doc["_id"]
	print(did)
	es.delete(index="grafana-dash",doc_type="dashboard",id=did)

