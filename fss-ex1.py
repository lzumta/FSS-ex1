import requests

from timeit import default_timer as timer
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import csv
import pickle

import ipfshttpclient  # ipfsapi is outdated


def deserialize(lib, name):
    infile = open(name, 'rb')
    file = lib.load(infile)
    infile.close()
    return file


def serialize(lib, filecontent, filename):
    outfile = open(filename, "wb")
    lib.dump(filecontent, outfile)
    outfile.close()


def download_file_http(url):
    t0 = timer()
    r = requests.get(url, allow_redirects=True)
    t1 = timer()
    data = r.content
    return data, t1-t0


def download_image_http(url, name):
    t0 = timer()
    r = requests.get(url, allow_redirects=True)
    t1 = timer()
    data = r.content
    with open(name, 'wb') as f:
        f.write(r.content)
        f.close()
    return data, t1-t0


def store(data):
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    res = client.add(data)
    return res['Hash']


def retrieve(hash):
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    file = client.cat(hash)
    return file


def serialize_and_store(lib, filecontent, filename):
    t0 = timer()
    serialize(lib, filecontent, filename)
    t1 = timer()
    hash = store(filename)
    t2 = timer()
    serialize_time = t1 - t0
    store_time = t2 - t1
    return serialize_time, store_time, hash


def retrieve_and_deserialize(lib, hash, filename):
    t0 = timer()
    retrieve(hash)
    t1 = timer()
    file = deserialize(lib, filename)
    t2 = timer()
    retrieve_time = t1 - t0
    deserialize_time = t2 - t1
    return retrieve_time, deserialize_time


if __name__ == "__main__":
    # download files using HTTP
    file1mb, time_1mb = download_file_http('https://filesender.switch.ch/filesender2/download.php?token=6de159f9-55ba-4661-9329-2cca0f4c9e67&files_ids=26095')
    file100mb, time_100mb = download_file_http('https://filesender.switch.ch/filesender2/download.php?token=d6cba8dd-b844-47fb-aefe-2404ca503146&files_ids=26090')
    file1gb, time_1gb = download_file_http('https://filesender.switch.ch/filesender2/download.php?token=47471388-24bf-48b7-a28b-0a270c0f40c3&files_ids=26089')
    filecontents = [file1mb, file100mb, file1gb]
    filenames = ['1mb.txt', '100mb.txt', '1gb.txt']
    http_times = [time_1mb, time_100mb, time_1gb]


    # for TWO different serialization algorithms
    serializers = [pickle, csv]

    a_serializers_average_times = [[],[]]
    b_deserializers_average_times = [[],[]]
    for serializer in serializers:
        # for each file size
        a_average_times = []
        b_average_times = []
        for filecontent in filecontents:
            a_times = []
            b_times = []
            for i in range(10):
                # a) Time elapsed to serialize and store
                serialize_time, store_time, hash = serialize_and_store(serializer, filecontent, filenames[filecontents.index(filecontent)])
                # b) Time elapsed to retrieve and deserialize
                retrieve_time, deserialize_time = retrieve_and_deserialize(serializer, hash, filenames[filecontents.index(filecontent)])
                a_times.append(serialize_time + store_time)
                b_times.append(retrieve_time + deserialize_time)
            a_average_times.append(np.mean(a_times))
            b_average_times.append(np.mean(b_times))
        s = serializers.index(serializer)
        a_serializers_average_times[s] = a_average_times
        a_serializers_average_times[s] = b_average_times


        print(f"The average times (to download using HTTP) were the following:\n"
              f"|\t1mb\t\t|\t100mb\t|\t1gb\t\t|\n"
              f"|\t{http_times[0]:.3f}\t|\t{http_times[1]:.3f}\t|\t{http_times[2]:.3f}\t|\n\n")

        print(f"The average times (to serialize and store) were the following:\n"
              f"|\t1mb\t\t|\t100mb\t|\t1gb\t\t|\n"
              f"|\t{a_average_times[0]:.3f}\t|\t{a_average_times[1]:.3f}\t|\t{a_average_times[2]:.3f}\t|\n\n")

        print(f"The average times (to retrieve and deserialize) were the following:\n"
              f"|\t1mb\t\t|\t100mb\t|\t1gb\t\t|\n"
              f"|\t{b_average_times[0]:.3f}\t|\t{b_average_times[1]:.3f}\t|\t{b_average_times[2]:.3f}\t|\n\n")
        break



    sizes = ["1","100","1000"]
    X_axis = np.arange(len(sizes))

    # Compare Serialization Algorithms (2.2 point 3 in the exercise sheet)
    plt.figure()
    plt.plot(sizes, a_average_times, 'ro')
    plt.plot(sizes, b_average_times, 'bo')
    plt.title('Duration Comparison Serialize and Store')
    plt.xlabel('file size (MB)')
    plt.ylabel('avg duration (s) of 10 runs')
    for a, b in zip(sizes, a_average_times):
        b = round(b, 3)
        plt.text(a, b, str(b))
    for a, b in zip(sizes, b_average_times):
        b = round(b, 3)
        plt.text(a, b, str(b))
    plt.bar(X_axis-0.2, a_average_times, 0.4, edgecolor="gray", label="Pickle", color="red")
    plt.bar(X_axis+0.2, b_average_times, 0.4, edgecolor="gray", label="CSV", color="blue")
    plt.xticks(X_axis, sizes)
    plt.legend()
    plt.savefig('Duration Comparison Serialize and Store.jpg')
    plt.show()


    # Compare IPFS with HTTP on deserialization (2.2 point 5 in the exercise sheet)
    plt.figure()
    plt.plot(sizes,b_average_times, 'ro')
    plt.plot(sizes,http_times, 'bo')
    plt.title('Duration Comparison Retrieve and Deserialize')
    plt.xlabel('file size (MB)')
    plt.ylabel('avg duration (s) of 5 runs')
    for a, b in zip(sizes, b_average_times):
        b = round(b, 3)
        plt.text(a, b, str(b))
    for a, b in zip(sizes, http_times):
        b = round(b, 3)
        plt.text(a, b, str(b))
    plt.bar(X_axis-0.2, b_average_times, 0.4, edgecolor="gray", label="IPFS", color="red")
    plt.bar(X_axis+0.2, http_times, 0.4, edgecolor="gray", label="HTTP", color="blue")
    plt.xticks(X_axis, sizes)
    plt.legend()
    plt.savefig('Duration Comparison Retrieve and Deserialize.jpg')
    plt.show()


    # Download unstructured data (2.2 point 4 in the exercise sheet)
    sizes = ["UZH Logo"]
    X_axis = np.arange(len(sizes))

    filecontent, http_time = download_image_http('https://www.uzh.ch/uzh/authoring/images/uzh_logo_e_pos_web_assoc.jpg', "uzhLogo.jpg")
    serialize_time, store_time, hash = serialize_and_store(pickle, filecontent, "uzhLogo.jpg")
    retrieve_time, deserialize_time = retrieve_and_deserialize(pickle, hash, "uzhLogo.jpg")

    plt.figure()
    plt.plot(sizes, retrieve_time + deserialize_time, 'ro')
    plt.plot(sizes, http_time, 'bo')
    plt.title('Duration Comparison of Unstructured Data')
    plt.xlabel('')
    plt.ylabel('avg duration (s) of 5 runs')
    plt.bar(X_axis-0.2, retrieve_time + deserialize_time, 0.4, edgecolor="gray", label="IPFS", color="red")
    plt.bar(X_axis+0.2, http_time, 0.4, edgecolor="gray", label="HTTP", color="blue")
    plt.xticks(X_axis, sizes)
    plt.legend()
    plt.savefig('Duration Comparison of Unstructured Data.jpg')
    plt.show()

