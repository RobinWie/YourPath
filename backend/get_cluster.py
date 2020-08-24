# this script gets the right cluster for a user when a new profile is added

# IMPORT
from sklearn.cluster import KMeans
from random import randrange
import sys
import pymongo

# LOAD PROPERTIES FROM INPUT PARAMS
new_user_prop_list = [[sys.argv[1], sys.argv[2], sys.argv[3]]]
DATABASE = sys.argv[4]

# CONNECT TO MONGODB
client = pymongo.MongoClient(DATABASE)
users = client["Cluster0"]["users"]

prop_list = []
for user in users.find():
    cur_prop_list = [] # /prop_1, prop_2, prop_3, ...
    for key, value in user.items():
        if key[0:4] == "prop":
            cur_prop_list.append(value)
    prop_list.append(cur_prop_list)

# LOAD MODEL # WORKAROUND: RELEARN MODEL WITH SAME RANDOM STATE
model = KMeans(n_clusters = 3, random_state = 12)
model.fit(prop_list)

print(model.predict(new_user_prop_list))