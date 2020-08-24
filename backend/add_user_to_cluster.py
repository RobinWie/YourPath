# this script adds a user to a cluster when a new profile is added

# IMPORT
import sys
import pymongo
from sklearn.cluster import KMeans
from random import randrange

# READ INPUT PARAMS
username = sys.argv[1]
cluster_id = int(sys.argv[2])
DATABASE = sys.argv[3]

# CONNECT TO MONGODB
client = pymongo.MongoClient(DATABASE) # connect to db
users = client["Cluster0"]["users"]
cluster = client["Cluster0"]["cluster"]

user = users.find_one({"username": username})
cur_cluster = cluster.find_one({"id": cluster_id})

user_list = cur_cluster["user"]
user_list.append(user)

myquery = { "id": cluster_id }
newvalues = { "$set": { "user": user_list } }
cluster.update_one(myquery, newvalues)

print(cluster["user"])