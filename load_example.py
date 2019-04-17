#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

import argparse
import networkx as nx
import os
import pickle
import random


def load_example(topo_path, data_path):

    # read data from file
    with open(data_path, 'r') as infile:
        data = pickle.load(infile)

    destination_to_prefix = data['destination_to_prefix']
    prefix_to_destination = data['prefix_to_destination']

    node_to_name = data['node_to_name']
    name_to_node = data['name_to_node']

    # topology
    topo = nx.read_gpickle(topo_path)

    paths = list()
    for path in data['paths']:
        shortest_path = len(path[0]) <= len(nx.shortest_path(topo, source=path[0][0], target=path[0][-1]))
        paths.append(NDBEntry(path[0], path[1], path[2], shortest_path, path[4], path[3]))

    return paths, topo, destination_to_prefix, prefix_to_destination, node_to_name, name_to_node


class NDBEntry(object):
    def __init__(self, path, destination, prefix, shortest_path, additional_features, traffic_size=1):
        self.path = path
        self.prefix = prefix
        self.destination = destination
        self.shortest_path = shortest_path
        self.additional_features = additional_features

        self.traffic_size = traffic_size

    def get(self, key):
        if key == 'path':
            return tuple(self.path)
        elif key == 'prefix':
            return self.prefix
        elif key == 'destination':
            return self.destination
        elif key == 'egress':
            return self.path[-1]
        elif key == 'ingress':
            return self.path[0]
        elif key == 'shortest_path':
            return self.shortest_path
        elif 'feature_' in key:
            feature_id = int(key.split('_')[1])
            return self.additional_features[feature_id]
        else:
            print 'UNKNOWN FEATURE: %s' % key

    def __str__(self):
        return "{path} - {destination} - {prefix} - {size}".format(path=" -> ".join(self.path),
                                                                   destination=self.destination,
                                                                   prefix=self.prefix,
                                                                   size=self.traffic_size)

    def __repr__(self):
        return self.__str__()


def main(example_path):
    topo_file = "ndb_topo.out"
    data_file = "ndb_dump.out"

    topo_path = os.path.join(example_path, topo_file)
    data_path = os.path.join(example_path, data_file)

    paths, topo, dest_to_prefix, prefix_to_dest, node_to_name, name_to_node = load_example(topo_path, data_path)

    output = "Successfully read the example files.\n"
    output += "There is a total of {} flows in a topology with {} nodes and {} edges.\n\n".format(len(paths),
                                                                                                  len(topo.nodes()),
                                                                                                  len(topo.edges()))
    output += "This is a random flow: {}".format(random.choice(paths))

    print output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to the directory containing the example', type=str)
    parsed_args = parser.parse_args()

    main(parsed_args.path)
