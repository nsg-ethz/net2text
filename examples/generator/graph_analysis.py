#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

"""
Script to quickly analyze all the topology zoo topologies (number of nodes and edges)
"""


import networkx as nx

if __name__ == "__main__":

    graph_files = ['Aarnet.graphml', 'BeyondTheNetwork.graphml', 'Deltacom.graphml', 'Garr201007.graphml', 'GtsSlovakia.graphml',
                   'KentmanApr2007.graphml', 'Packetexchange.graphml', 'Sunet.graphml', 'Abilene.graphml', 'Bics.graphml',
                   'DeutscheTelekom.graphml', 'Garr201008.graphml', 'Harnet.graphml', 'KentmanAug2005.graphml', 'Padi.graphml',
                   'Surfnet.graphml', 'Abvt.graphml', 'Biznet.graphml', 'Dfn.graphml', 'Garr201010.graphml', 'Heanet.graphml',
                   'KentmanFeb2008.graphml', 'Palmetto.graphml', 'Switch.graphml', 'Aconet.graphml', 'Bren.graphml', 'DialtelecomCz.graphml',
                   'Garr201012.graphml', 'HiberniaCanada.graphml', 'KentmanJan2011.graphml', 'Peer1.graphml', 'SwitchL3.graphml',
                   'Agis.graphml', 'BsonetEurope.graphml', 'Digex.graphml', 'Garr201101.graphml', 'HiberniaGlobal.graphml',
                   'KentmanJul2005.graphml', 'Pern.graphml', 'Syringa.graphml', 'Ai3.graphml', 'BtAsiaPac.graphml', 'Easynet.graphml',
                   'Garr201102.graphml', 'HiberniaIreland.graphml', 'Kreonet.graphml', 'PionierL1.graphml', 'TLex.graphml',
                   'Airtel.graphml', 'BtEurope.graphml', 'Eenet.graphml', 'Garr201103.graphml', 'HiberniaNireland.graphml',
                   'LambdaNet.graphml', 'PionierL3.graphml', 'TataNld.graphml', 'Amres.graphml', 'BtLatinAmerica.graphml',
                   'EliBackbone.graphml', 'Garr201104.graphml', 'HiberniaUk.graphml', 'Latnet.graphml', 'Psinet.graphml',
                   'Telcove.graphml', 'Ans.graphml', 'BtNorthAmerica.graphml', 'Epoch.graphml', 'Garr201105.graphml',
                   'HiberniaUs.graphml', 'Layer42.graphml', 'Quest.graphml', 'Telecomserbia.graphml', 'Arn.graphml',
                   'Canerie.graphml', 'Ernet.graphml', 'Garr201107.graphml', 'Highwinds.graphml', 'Litnet.graphml',
                   'RedBestel.graphml', 'Tinet.graphml', 'Arnes.graphml', 'Carnet.graphml', 'Esnet.graphml', 'Garr201108.graphml',
                   'HostwayInternational.graphml', 'Marnet.graphml', 'Rediris.graphml', 'Tw.graphml', 'Arpanet196912.graphml',
                   'Cernet.graphml', 'Eunetworks.graphml', 'Garr201109.graphml', 'HurricaneElectric.graphml', 'Marwan.graphml',
                   'Renam.graphml', 'Twaren.graphml', 'Arpanet19706.graphml', 'Cesnet1993.graphml', 'Evolink.graphml',
                   'Garr201110.graphml', 'Ibm.graphml', 'Missouri.graphml', 'Renater1999.graphml', 'Ulaknet.graphml',
                   'Arpanet19719.graphml', 'Cesnet1997.graphml', 'Fatman.graphml', 'Garr201111.graphml', 'Iij.graphml',
                   'Mren.graphml', 'Renater2001.graphml', 'UniC.graphml', 'Arpanet19723.graphml', 'Cesnet1999.graphml',
                   'Fccn.graphml', 'Garr201112.graphml', 'Iinet.graphml', 'Myren.graphml', 'Renater2004.graphml', 'Uninet.graphml',
                   'Arpanet19728.graphml', 'Cesnet2001.graphml', 'Forthnet.graphml', 'Garr201201.graphml', 'Ilan.graphml',
                   'Napnet.graphml', 'Renater2006.graphml', 'Uninett2010.graphml', 'AsnetAm.graphml', 'Cesnet200304.graphml',
                   'Funet.graphml', 'Gblnet.graphml', 'Integra.graphml', 'Navigata.graphml', 'Renater2008.graphml',
                   'Uninett2011.graphml', 'Atmnet.graphml', 'Cesnet200511.graphml', 'Gambia.graphml', 'Geant2001.graphml',
                   'Intellifiber.graphml', 'Netrail.graphml', 'Renater2010.graphml', 'Uran.graphml', 'AttMpls.graphml',
                   'Cesnet200603.graphml', 'Garr199901.graphml', 'Geant2009.graphml', 'Internetmci.graphml', 'NetworkUsa.graphml',
                   'Restena.graphml', 'UsCarrier.graphml', 'Azrena.graphml', 'Cesnet200706.graphml', 'Garr199904.graphml',
                   'Geant2010.graphml', 'Internode.graphml', 'Nextgen.graphml', 'Reuna.graphml', 'UsSignal.graphml',
                   'Bandcon.graphml', 'Cesnet201006.graphml', 'Garr199905.graphml', 'Geant2012.graphml', 'Interoute.graphml',
                   'Niif.graphml', 'Rhnet.graphml', 'Uunet.graphml', 'Basnet.graphml', 'Chinanet.graphml', 'Garr200109.graphml',
                   'Getnet.graphml', 'Intranetwork.graphml', 'Noel.graphml', 'Rnp.graphml', 'Vinaren.graphml', 'Bbnplanet.graphml',
                   'Claranet.graphml', 'Garr200112.graphml', 'Globalcenter.graphml', 'Ion.graphml', 'Nordu1989.graphml',
                   'Roedunet.graphml', 'VisionNet.graphml', 'Bellcanada.graphml', 'Cogentco.graphml', 'Garr200212.graphml',
                   'Globenet.graphml', 'IowaStatewideFiberMap.graphml', 'Nordu1997.graphml', 'RoedunetFibre.graphml',
                   'VtlWavenet2008.graphml', 'Bellsouth.graphml', 'Colt.graphml', 'Garr200404.graphml', 'Goodnet.graphml',
                   'Iris.graphml', 'Nordu2005.graphml', 'Sago.graphml', 'VtlWavenet2011.graphml', 'Belnet2003.graphml',
                   'Columbus.graphml', 'Garr200902.graphml', 'Grena.graphml', 'Istar.graphml', 'Nordu2010.graphml',
                   'Sanet.graphml', 'WideJpn.graphml', 'Belnet2004.graphml', 'Compuserve.graphml', 'Garr200908.graphml',
                   'Gridnet.graphml', 'Itnet.graphml', 'Nsfcnet.graphml', 'Sanren.graphml', 'Xeex.graphml', 'Belnet2005.graphml',
                   'CrlNetworkServices.graphml', 'Garr200909.graphml', 'Grnet.graphml', 'JanetExternal.graphml', 'Nsfnet.graphml',
                   'Savvis.graphml', 'Xspedius.graphml', 'Belnet2006.graphml', 'Cudi.graphml', 'Garr200912.graphml', 'GtsCe.graphml',
                   'Janetbackbone.graphml', 'Ntelos.graphml', 'Shentel.graphml', 'York.graphml', 'Belnet2007.graphml', 'Cwix.graphml',
                   'Garr201001.graphml', 'GtsCzechRepublic.graphml', 'Janetlense.graphml', 'Ntt.graphml', 'Sinet.graphml', 'Zamren.graphml',
                   'Belnet2008.graphml', 'Cynet.graphml', 'Garr201003.graphml', 'GtsHungary.graphml', 'Jgn2Plus.graphml', 'Oteglobe.graphml',
                   'Singaren.graphml', 'Belnet2009.graphml', 'Darkstrand.graphml', 'Garr201004.graphml', 'GtsPoland.graphml', 'Karen.graphml',
                   'Oxford.graphml', 'Spiralight.graphml', 'Belnet2010.graphml', 'Dataxchange.graphml', 'Garr201005.graphml',
                   'GtsRomania.graphml', 'Kdl.graphml', 'Pacificwave.graphml', 'Sprint.graphml'
    ]

    networks = list()
    for graph_file in graph_files:
        # load graph from file
        graph = nx.read_graphml(graph_file)
        networks.append((graph_file, graph.number_of_nodes(), graph.number_of_edges()))

    i = 0
    for graph_file, num_nodes, num_edges in sorted(networks, key=lambda x: x[1], reverse=True):
        i += 1
        print '%s: Nodes %d, Edges %d' % (graph_file, num_nodes, num_edges)
        if i > 10:
            break
