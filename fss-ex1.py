import requests
from timeit import default_timer as timer
import numpy as np
import matplotlib.pyplot as plt

import ipfshttpclient
# import ipfsapi  # outdated


def downloadHTTP(URL):
    durations = []
    n = 1
    for i in range(n):
        start_time = timer()
        r = requests.get(URL, allow_redirects=True)
        end_time = timer()
        duration = end_time - start_time
        print(duration)
        durations.append(duration)
    avrg_duration = sum(durations)/n
    return avrg_duration

def serialize(file):
    durations = []
    n = 2
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    for i in range(n):
        start_time = timer()
        res = client.add(file)
        end_time = timer()
        duration = end_time - start_time
        print(duration)
        durations.append(duration)
    avrg_duration = sum(durations)/n
    return avrg_duration, res["Hash"]

def deserialize(contentId):
    durations = []
    n = 2
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    for i in range(n):
        start_time = timer()
        getfile = client.cat(contentId)
        end_time = timer()
        duration = end_time - start_time
        print(duration)
        durations.append(duration)
    avrg_duration = sum(durations)/n
    return avrg_duration




if __name__ == "__main__":
    sizes = ["1","100","1000"]
    X_axis = np.arange(len(sizes))
    # http_1mb = downloadHTTP('https://filesender.switch.ch/filesender2/download.php?token=6de159f9-55ba-4661-9329-2cca0f4c9e67&files_ids=26095')
    # http_100mb = downloadHTTP('https://filesender.switch.ch/filesender2/download.php?token=d6cba8dd-b844-47fb-aefe-2404ca503146&files_ids=26090')
    # http_1000mb = downloadHTTP('https://filesender.switch.ch/filesender2/download.php?token=47471388-24bf-48b7-a28b-0a270c0f40c3&files_ids=26089')
    # avg_http = [http_1mb,http_100mb,http_1000mb]

    ipfs_1mb_serialize, hash_1mb = serialize('1mb.txt')
    ipfs_100mb_serialize, hash_100mb = serialize('100mb.txt')
    ipfs_1000mb_serialize, hash_1000mb = serialize('1gb.txt')
    avg_ipfs_serialize = [ipfs_1mb_serialize,ipfs_100mb_serialize,ipfs_1000mb_serialize]

    ipfs_1mb_deserialize = deserialize(hash_1mb)
    ipfs_100mb_deserialize = deserialize(hash_100mb)
    ipfs_1000mb_deserialize = deserialize(hash_1000mb)
    avg_ipfs_deserialize = [ipfs_1mb_deserialize,ipfs_100mb_deserialize,ipfs_1000mb_deserialize]


    # ************ PLOT ***********
    plt.figure()
    plt.plot(sizes,avg_ipfs_serialize, 'ro')
    plt.plot(sizes,avg_ipfs_deserialize, 'bo')
    plt.title('Duration Comparison Serialization and Deserialization')
    plt.xlabel('file size (MB)')
    plt.ylabel('duration (s)')
    for a, b in zip(sizes, avg_ipfs_serialize):
        b = round(b, 3)
        plt.text(a, b, str(b))
    for a, b in zip(sizes, avg_ipfs_deserialize):
        b = round(b, 3)
        plt.text(a, b, str(b))
    plt.bar(X_axis-0.2, avg_ipfs_serialize, 0.4, edgecolor="gray", label="Serialize", color="red")
    plt.bar(X_axis+0.2, avg_ipfs_deserialize, 0.4, edgecolor="gray", label="Deserialize", color="blue")
    plt.xticks(X_axis, sizes)
    plt.legend()
    plt.show()