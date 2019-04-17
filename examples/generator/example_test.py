#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

"""
Script to quickly analyze a generated example (number of prefixes, paths, and prefixes per destination)
"""


import argparse
import pickle
import re

import networkx as nx

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='path to directory where input files reside', type=str)
    parser.add_argument('data', help='name of the file containing the db dump', type=str)
    parser.add_argument('topo', help='file containing the graph dump', type=str)
    parser.add_argument('-d', '--debug', help='enable debug output', action='store_true')
    parsed_args = parser.parse_args()

    loglevel = 'DEBUG' if parsed_args.debug else 'INFO'

    input_path = parsed_args.input_path
    data_file = parsed_args.data
    topo_file = parsed_args.topo

    # read data from file
    with open('%s/%s' % (input_path, data_file), 'r') as infile:
        data = pickle.load(infile)

    destination_to_prefix = data['destination_to_prefix']
    prefix_to_destination = data['prefix_to_destination']
    paths = data['paths']

    # GENERAL INFORMATION ABOUT THE FORWARDING STATE
    print 'There are %d paths for %d destinations with a total of %d prefixes' % \
          (len(paths), len(destination_to_prefix), len(prefix_to_destination))

    #
    if True:
        for destination, prefixes in destination_to_prefix.iteritems():
            print 'Destination %s has %d prefixes.' % (destination, len(prefixes))
            # print str(prefixes)

    # GENERAL INFORMATION ABOUT THE UNDERLYING TOPOLOGY
    topo = nx.read_gpickle('%s/%s' % (input_path, topo_file))
    print 'The graph has %d nodes and %d edges' % (topo.number_of_nodes(), topo.number_of_edges())

    # COMPUTE SCORE OF THE DIFFERENT SPECS (specified below in all_fvs)
    if False:
        all_fvs = [[('egress', 2), ('ingress', 24)],
                   [('egress', 2)],
                   [('egress', 2), ('destination', 'Hydro One Telecom Inc.')],
                   [('egress', 2), ('destination', 'Hydro One Telecom Inc.'), ('ingress', 6)]]

        for feature_values in all_fvs:
            traffic = 0
            num_paths = 0
            for path in paths:
                matches = True

                for feature, value in feature_values:
                    if feature == 'egress' and str(value) != path[0][-1]:
                        matches = False
                        break

                    if feature == 'ingress' and str(value) != path[0][0]:
                        matches = False
                        break

                    if feature == 'destination' and re.sub('[^a-zA-Z0-9]', '', str(value)) != re.sub('[^a-zA-Z0-9]', '', path[1]):
                        matches = False
                        break

                if matches:
                    traffic += path[3]
                    num_paths += 1

            print 'TRAFFIC %f FOR %s WITH %d PATHS' % (traffic, feature_values, num_paths)

    if True:
        egresses = set()
        for path in paths:
            egresses.add(path[0][-1])

        print 'THERE ARE %d EGRESSES' % (len(egresses), )
        print ', '.join([str(x) for x in list(egresses)])
