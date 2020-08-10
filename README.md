# Example: Text Search in CockroachDB

![alt text](./CRDB_Text_Search_Stemming_40ms.png "Example text search in CockroachDB")

This is a simple example of doing full text indexing and search on a set of
HTML documents.  What is shown here is based on Ubuntu 18.04 (running on a
locally deployed VM), and I am assuming a CockroachDB instance is running on
the network, in insecure mode.  My experimental setup uses a 3 node CockroachDB
instance with HAProxy listening on port 5432 (the traditional PostgreSQL port),
all running locally on a MacBook Pro.

## Dependencies
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#quick-start),
a Python library for working with HTML documents:
```
$ sudo apt-get install python3-bs4
```

* The _Pip_ Python package installer:
```
$ sudo apt install python-pip
```

* [Natural Language Toolkit (NLTK)](https://www.nltk.org/), a leading platform
for building Python programs to work with human language data:
```
$ pip install --user -U nltk
```

## References
[Set up a local CockroachDB cluster](https://www.cockroachlabs.com/docs/stable/start-a-local-cluster.html)

[HAProxy setup](https://www.cockroachlabs.com/docs/stable/deploy-cockroachdb-on-premises-insecure.html#step-5-set-up-load-balancing)



## TODO
* Add a Flask REST API to the indexer code, to support search
* Build Docker image of this

