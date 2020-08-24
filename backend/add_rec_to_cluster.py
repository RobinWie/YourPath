# this script adds a recommendation to a cluster on click of a like button

# IMPORTS
import sys
import pymongo

# READ INPUT PARAMS
cluster_id = int(sys.argv[1])
rec_id = sys.argv[2]
platform = sys.argv[3]
DATABASE = sys.argv[4]

# CONNECT TO MONGODB
client = pymongo.MongoClient(DATABASE) # connect to db
users = client["Cluster0"]["users"]
cluster = client["Cluster0"]["cluster"]



cur_cluster = cluster.find_one({"id": cluster_id})
if platform == "youtube":
    rec_list = cur_cluster["yt_rec"]
    if rec_id in rec_list:
        pass
    else:
        rec_list.append(rec_id)
        myquery = { "id": cluster_id }
        newvalues = { "$set": { "yt_rec": rec_list } }
        print(cur_cluster["yt_rec"])
        cluster.update_one(myquery, newvalues)
else:
    rec_list = cur_cluster["sf_rec"]
    if rec_id in rec_list:
        pass
    else:
        rec_list.append(rec_id)
        myquery = { "id": cluster_id }
        newvalues = { "$set": { "sf_rec": rec_list } }
        cluster.update_one(myquery, newvalues)

print(cluster.find_one({"id": cluster_id}))