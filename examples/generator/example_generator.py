#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

"""
Script to generate example datasets based on a topology zoo topology (graphml format), an ASN to organization mapping
(as_to_org.txt) and a full-rib (full-ipv4-rib.out)
"""

import argparse
import pickle
import random
import math
import json
import os
from collections import defaultdict
import itertools
import sys
import scipy.stats

import networkx as nx
import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from matplotlib import rc_file
rc_file('matplotlibrc')


class ExampleGenerator(object):
    def __init__(self, graph_file, output_path, automatically):

        STATS = True
        self.output_path = output_path
        self.automatically = automatically

        # probabilities
        self.egress_exception_probability = 0.01
        self.shortest_path_exception_probability = 0.05
        self.multi_path_probability = 0.1

        # skew used for additional features
        self.num_feature_values = np.random.uniform(2, 100, 12)

        # stats
        self.stats = dict()
        self.stats['num_egresses'] = list()
        self.stats['organisation_size'] = list()
        self.stats['organisation_size2'] = defaultdict(int)
        self.stats['egress_size'] = defaultdict(int)
        self.stats['ingress_size'] = defaultdict(int)
        self.stats['organisation_prefixes'] = list()

        # get graph from file
        self.graph, self.egress_nodes, self.name_to_node, self.node_to_name, self.shortest_path_lengths, \
        self.shortest_paths, self.non_shortest_paths = self.get_graph(graph_file)

        print 'GRAPH DONE'

        # get organisations and their prefixes from file
        organisation_file = 'as_to_org.txt'
        self.asn_to_organisation, self.organisations = self.load_organisations(organisation_file)
        # self.asn_to_organisation, self.organisations = self.load_few_organisations()

        print 'ORGANISATIONS DONE'

        # specify the number of prefixes if you want to restrict the number of prefixes considered. You can also specify
        # multiple numbers in the list and one example is generated for each number specified. To use all prefixes,
        # just put None
        num_prefixes = [100, 1000, 10000]

        for n_p in num_prefixes:
            if n_p:
                tmp_op = '%s_%d' % (output_path, n_p)
            else:
                tmp_op = '%s_all' % (output_path, )

            if not os.path.exists(tmp_op):
                os.makedirs(tmp_op)

            self.full_rib = 'full-ipv4-rib.out'
            self.organisation_to_prefix, self.prefix_to_organisation = self.use_full_rib(n_p, None)

            # create the paths for all nodes to all prefixes
            # parameter for flow size exponential distribution
            paths = self.get_paths()

            # write data to file for network db
            data = {
                'paths': paths,
                'destination_to_prefix': self.organisation_to_prefix,
                'prefix_to_destination': self.prefix_to_organisation,
                'node_to_name': self.node_to_name,
                'name_to_node': self.name_to_node
            }

            output_file = '%s/ndb_dump.out' % tmp_op
            with open(output_file, 'w') as outfile:
                pickle.dump(data, outfile)

            output_graph_file = '%s/ndb_topo.out' % tmp_op
            nx.write_gpickle(self.graph, output_graph_file)

            # self.create_grammar_mappings(tmp_op)

            if STATS:
                self.produce_stats(tmp_op)

            print 'PATHS DONE FOR %s' % (str(n_p) if n_p else 'all', )

            # add config file

            config_data = {
                "ndb_conf": {
                    "db_type": "generated",
                    "path": os.path.basename(os.path.normpath(tmp_op)),
                    "data": "ndb_dump.out",
                    "topo": "ndb_topo.out"
                },
                "summarizer_conf": {
                    "summary_mode": "tree",
                    "tree_mode": "balanced",
                    "splitting_mode": "traffic_size",
                    "sampling_rate": -1
                },
                "features": [
                    "ingress",
                    "egress",
                    "destination",
                    "shortest_path",
                    "path"
                ]
            }

            output_file = '%s/config.json' % tmp_op
            with open(output_file, 'w') as outfile:
                json.dump(config_data, outfile)

    def get_graph(self, graph_file):
        # load graph from file
        print 'reading graph file'
        graph = nx.read_graphml(graph_file)

        # compute the length of the shortest path between any two nodes
        print 'computing shortest path lengths'
        sp_lengths = nx.all_pairs_dijkstra_path_length(graph)

        # compute all shortest paths between any two nodes
        print 'computing shortest paths'
        shortest_paths = defaultdict(dict)
        nodes = nx.nodes(graph)
        for n1, n2 in itertools.product(nodes, nodes):
            shortest_paths[n1][n2] = list(nx.all_shortest_paths(graph, n1, n2))

        # compute some non shortest paths between any two nodes
        if False:
            print 'computing non-shortest paths'
            non_shortest_paths = defaultdict(dict)
            for n1, n2 in itertools.product(nodes, nodes):
                cutoff = sp_lengths[n1][n2] + 1
                tmp_paths = nx.all_simple_paths(graph, n1, n2, cutoff)
                non_shortest_paths[n1][n2] = [tmp_path for tmp_path in tmp_paths if len(tmp_path) == cutoff]
        else:
            non_shortest_paths = shortest_paths

        # create node abbreviation to actual name mapping
        print 'node to name mapping'
        node_to_name = dict()
        name_to_node = dict()
        if not self.automatically:
            for node in nx.nodes(graph):
                name = raw_input('What is the full name of %s?\n' % node)
                node_to_name[node] = name
                name_to_node[name] = node
        else:
            for node in nx.nodes(graph):
                name = 'router_%s' % node
                node_to_name[node] = name
                name_to_node[name] = node

        # get egress nodes
        print 'egress nodes'
        invalid_input = True
        egress_nodes = list()
        if not self.automatically:
            while invalid_input:
                print 'Which of the following nodes are egress nodes?\n%s\nEnd with empty line' \
                      % ', '.join([str(node) for node in nx.nodes(graph)])
                more_input = True
                while more_input:
                    input = raw_input()
                    if not input:
                        more_input = False
                    elif input not in nx.nodes(graph):
                        print 'Error the given node is unknown'
                    else:
                        egress_nodes.append(input)

                if egress_nodes:
                    invalid_input = False
                else:
                    print 'You need to specify at least one egress node'
        else:
            num_egresses = int(raw_input('Number of Egresses? (Total number of nodes: %d)\n' % len(nodes)))
            egress_nodes = np.random.choice(nodes, num_egresses, replace=False)

        return graph, egress_nodes, name_to_node, node_to_name, sp_lengths, shortest_paths, non_shortest_paths

    def load_few_organisations(self):
        # load organisations and their prefixes from the file
        asn_to_name = dict()
        names = list()

        with open('few_orgs.txt', 'r') as infile:
            for tmp_line in infile:
                line = tmp_line.strip()
                org_name, tmp_asn = line.split('-')
                asn = int(tmp_asn)

                asn_to_name[asn] = org_name
                names.append(org_name)

        return asn_to_name, names

    def load_organisations(self, file):
        # load organisations and their prefixes from the file
        asn_to_org_id = dict()
        org_id_to_name = dict()

        names = list()

        with open(file, 'r') as infile:
            mode = -1
            for tmp_line in infile:
                line = tmp_line.strip()
                if line.startswith('#'):
                    if line.startswith('# format:org_id'):
                        mode = 1
                    elif line.startswith('# format:aut'):
                        mode = 2
                else:
                    if mode == -1:
                        print 'NOT READY - NO FORMAT DEFINITION'
                        sys.exit(0)
                    elif mode == 1:
                        # format:org_id|changed|org_name|country|source
                        org_id, _, org_name, _, _ = line.split('|')
                        org_id_to_name[org_id] = org_name
                        names.append(org_name)
                    elif mode == 2:
                        # format:aut|changed|aut_name|org_id|source
                        tmp_asn, _, _, org_id, _ = line.split('|')
                        asn = int(tmp_asn)
                        asn_to_org_id[asn] = org_id

        asn_to_name = dict()
        for asn, org_id in asn_to_org_id.iteritems():
            asn_to_name[asn] = org_id_to_name[org_id]

        return asn_to_name, names

    def use_full_rib(self, limit, variance):
        organisation_to_prefix = defaultdict(list)
        prefix_to_organisation = dict()

        prefixes = list()
        only_prefixes = list()
        with open(self.full_rib, 'r') as infile:
            for line in infile:
                tmp_data = line.strip().split(' ')
                prefix = tmp_data[0]

                # deal with AS sets
                if '{' in tmp_data[-1]:
                    origin = int(tmp_data[-1].replace('{', '').replace('}', '').split(',')[0])
                else:
                    origin = int(tmp_data[-1])

                prefixes.append((prefix, origin))
                only_prefixes.append(prefix)

        random.shuffle(prefixes)

        if not limit:
            limit = len(prefixes)

        # create the mapping of prefixes to their organisation (AS)
        unknown = list()
        if True:
            # use the real ASN to Org mapping and link prefixes to organisations using the origin observed in the
            # relevant route announcement.
            for prefix, origin in prefixes:
                if origin in self.asn_to_organisation:
                    organisation = self.asn_to_organisation[origin]
                else:
                    organisation = 'UNKNOWN'
                    unknown.append(origin)
                    continue

                organisation_to_prefix[organisation].append(prefix)
                prefix_to_organisation[prefix] = organisation

                if len(prefix_to_organisation) > limit:
                    break
        elif False:
            # assign the prefixes to the organisations according to a normal distribution.

            prefixes_to_split = only_prefixes[len(self.organisations):]

            total_p = 0
            o_p = dict()
            var = scipy.stats.norm(0, variance)
            for i, org in enumerate(self.organisations):
                p = var.pdf(i - len(self.organisations) / 2)
                o_p[org] = p
                total_p += p

                # make sure each organisation has at least one prefix
                organisation_to_prefix[org].append(only_prefixes[i])

            prev = 0
            for org, p in o_p.iteritems():
                next = prev + int(len(prefixes_to_split) * p / total_p)
                organisation_to_prefix[org] = only_prefixes[prev:next]
                for prefix in only_prefixes[prev:next]:
                    prefix_to_organisation[prefix] = org

                prev = next

        else:
            # assign each organisation the same number of prefixes.

            num_prefixes = math.ceil(float(len(prefixes))/float(len(self.organisations)))

            j = 0
            for prefix, _ in prefixes:
                org = j % num_prefixes

                organisation_to_prefix[org].append(prefix)
                prefix_to_organisation[prefix] = org

                j += 1

        print 'THERE WERE %d UNKNOWN ORGANIZATIONS' % (len(unknown), )

        for organisation, prefixes in organisation_to_prefix.iteritems():
            self.stats['organisation_prefixes'].append(len(prefixes))

        return organisation_to_prefix, prefix_to_organisation

    def get_egresses(self):
        # beta=1/lambda for the egress exponential distribution - this sets the median of the number of egress to a 4th
        # of all egresses. This is roughly according to "Understanding BGP Next-hop Diversity".
        egress_beta = float(len(self.egress_nodes))/(4.0 * np.log(2.0))
        egress_beta = 4.0/np.log(2.0)

        # Pick the number of egresses using an exponential distribution with the scale parameter as described above
        num_egress = int(np.random.exponential(scale=egress_beta))
        if num_egress < 1:
            num_egress = 1
        elif num_egress > len(self.egress_nodes):
            num_egress = len(self.egress_nodes)

        egress_nodes = np.random.choice(self.egress_nodes, num_egress, replace=False)
        return egress_nodes

    def get_flow_mean(self, num_prefixes):
        # Choose size of entire organisation according to exponential distribution, then divide it by the number of
        # of prefixes of that organisation. Use this value as mean of a normal distribution to introduce some variance
        # amongst the different prefixes of that organisation.

        flow_beta = 1000000.0
        total_organisation_size = np.random.exponential(scale=flow_beta)
        self.stats['organisation_size'].append(total_organisation_size)

        per_prefix_mean = total_organisation_size/float(num_prefixes)
        return per_prefix_mean

    def get_flow_size(self):
        # Choose size of entire organisation according to exponential distribution, then divide it by the number of
        # of prefixes of that organisation. Use this value as mean of a normal distribution to introduce some variance
        # amongst the different prefixes of that organisation.

        flow_beta = 1000.0
        flow_size = np.random.exponential(scale=flow_beta)
        return flow_size

    def get_paths(self):
        paths = list()

        i = 0
        j = 0
        k = 0

        additional_feature_values = defaultdict(set)

        print 'start computing all the paths'
        for organisation, prefixes in self.organisation_to_prefix.iteritems():
            # decide whether the node is multi-exit (hot-potato routing) or single exit
            # aka pick the egresses
            egress_nodes = self.get_egresses()
            self.stats['num_egresses'].append(len(egress_nodes))

            # get the mean size of each flow for this organisation
            flow_mean = self.get_flow_mean(len(prefixes))

            j += 1
            for prefix in prefixes:
                # introduce with some probability behavior which differs from the general organisation
                if random.uniform(0, 1) < self.egress_exception_probability:
                    curr_egress_nodes = self.get_egresses()
                else:
                    curr_egress_nodes = egress_nodes
                k += 1

                for node in nx.nodes(self.graph):
                    # check which is the closest egress node and then this is the path it takes
                    length = 1000
                    curr_egress = ''
                    for egress_node in curr_egress_nodes:
                        if self.shortest_path_lengths[node][egress_node] < length:
                            curr_egress = egress_node
                            length = self.shortest_path_lengths[node][egress_node]

                    # either shortest or not shortest path
                    if random.uniform(0, 1) < self.shortest_path_exception_probability:
                        tmp_paths = self.non_shortest_paths[node][curr_egress]
                    else:
                        tmp_paths = self.shortest_paths[node][curr_egress]

                    if not tmp_paths:
                        if curr_egress == node:
                            tmp_paths = [[curr_egress]]
                        else:
                            print 'THERE IS A PROBLEM WITH THE PATH FROM %s TO %s' % (node, curr_egress)

                    # if there are equal cost paths, use them
                    for path in tmp_paths:
                        additional_features = list()
                        for q, limit in enumerate(self.num_feature_values):
                            value = int(np.random.exponential(scale=5)) % int(limit)
                            additional_features.append(value)
                            additional_feature_values[q].add(value)

                        # get the size of this flow
                        # flow_size = np.random.normal(loc=flow_mean)
                        flow_size = self.get_flow_size()
                        self.stats['organisation_size2'][organisation] += flow_size
                        self.stats['egress_size'][curr_egress] += flow_size
                        self.stats['ingress_size'][node] += flow_size
                        paths.append((path, organisation, prefix, flow_size, additional_features))

                        if random.uniform(0, 1) > self.multi_path_probability:
                            break

                    i += 1

        print 'i: %d, j: %d, k: %d' % (i, j, k)

        print 'NUM VALUES PER ADDITIONAL FEATURE:'
        for q, values in additional_feature_values.iteritems():
            print '%d' % (len(values), )

        return paths

    def create_grammar_mappings(self, output_path):
        with open('%s/destinations.grammar' % output_path, 'w') as outfile:
            outfile.write('# Destinations\n')
            for destination in self.organisation_to_prefix.keys():
                outfile.write('(rule $Destination (%s) (ConstantFn (string %s)))\n' % (destination.lower(), destination))

        with open('%s/waypoints.grammar' % output_path, 'w') as outfile:
            outfile.write('# Waypoints\n')
            for node, name in self.node_to_name.iteritems():
                outfile.write('(rule $Hop (%s) (ConstantFn (string %s)))\n' % (name.lower(), str(node)))

    def produce_stats(self, output_path):
        num_plots = len(self.stats)
        cols = 3
        rows = int(math.ceil(num_plots/3.0))

        fig, axes = plt.subplots(cols, rows, sharex=False, sharey=True)

        print 'N-%d, R-%d, C-%d, 1-%d 2-%d' % (num_plots, rows, cols, len(axes), len(axes[0]))

        i = 0
        for name, stats in self.stats.iteritems():
            col = int(i/rows)
            row = i % rows

            ax = axes[col, row]

            if isinstance(stats, dict):
                stats = stats.values()

            min_value = np.floor(min(stats))
            max_value = np.ceil(max(stats))
            value_range = (min_value - 0.1, max_value + 0.1)

            num_bins = 1000
            p1 = ax.hist(stats, range=value_range, bins=num_bins, normed=1, histtype='step', cumulative='True')

            ax.set_title('CDF: %s' % name.replace('_', ' '))
            ax.set_ylim(0, 1)
            ax.set_xlim(min_value, max_value)
            i += 1

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.savefig('%s/cdfs.pdf' % (output_path, ), bbox_inches='tight')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_file', help='name of the file containing the graph in graphml format', type=str)
    parser.add_argument('output_path', help='path to the directory where the output should be stored', type=str)
    parser.add_argument('-a', '--automatically', help='automatically generate names and pick egresses', action='store_true')
    parser.add_argument('-d', '--debug', help='enable debug output', action='store_true')
    parsed_args = parser.parse_args()

    loglevel = 'DEBUG' if parsed_args.debug else 'INFO'

    output_path = parsed_args.output_path
    automatically = parsed_args.automatically

    if output_path[-1] == '/':
        output_path = output_path[:-1]

    graph_file = parsed_args.graph_file

    example_generator = ExampleGenerator(graph_file,
                                         output_path,
                                         automatically)
