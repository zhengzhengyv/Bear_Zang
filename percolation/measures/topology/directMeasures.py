import networkx as x
import numpy as n
import percolation as P
__doc__ = "for topological measures"


# @profile  # uncomment for lineprofiling
def topologicalMeasures(gg=x.Graph()):
    """A detailed info about one graph.

    Information about date, number of friends, friendships,
    interactions, etc.
    Average degree, average clustering, etc.

    Input: networkx Graph
    Used by: P.renderLegacy.topologicalTextualCharacterization.Analysis()
    Uses: P.topology.measures.overallMeasures()
    ToDo: implement homophily
    """
    degrees = gg.degree()
    degrees_ = list(degrees.values())
    if gg.is_directed():
        in_degrees = gg.in_degree()
        out_degrees = gg.out_degree()
        strengths = gg.degree(weight="weight")
        in_strengths = gg.in_degree(weight="weight")
        out_strengths = gg.out_degree(weight="weight")
        strengths_ = list(strengths.values())
        gg_ = gg.to_undirected()
    else:
        gg_ = gg
    # betweenness = x.betweenness.betweenness_centrality(gg)
    clustering = x.clustering(gg_)
    clustering_ = list(clustering.values())
    # clustering_w = x.clustering(gg_, weight="weight")
    # clustering_w_ = list(clustering_w.values())
    # square_clustering = x.square_clustering(gg)
    # square_clustering_ = list(square_clustering.values())
    transitivity = x.transitivity(gg)
    transitivity_u = x.transitivity(gg_)
    # closeness = x.closeness_centrality(gg)
    # closeness_ = list(closeness.values())
    # eccentricity = x.eccentricity(gg_)
    # eccentricity_ = list(eccentricity.values())
    comp_ = max(x.connected_component_subgraphs(gg_), key=len)
    # eccentricity_comp = x.eccentricity(comp_)
    # diameter = x.diameter(comp_, eccentricity_comp)
    # radius = x.radius(comp_, eccentricity_comp)
    # nperiphery = len(x.periphery(comp_, eccentricity_comp))
    # ncenter = len(x.center(comp_, eccentricity_comp))
    size_component = comp_.number_of_nodes()
    # ashort_path_u = x.average_shortest_path_length(comp_)
    nnodes = gg.number_of_nodes()
    nedges = gg.number_of_edges()
    frac_connected = 100*comp_.number_of_nodes()/nnodes
    if gg.is_directed():
        comp = max(x.weakly_connected_component_subgraphs(gg), key=len)
        ashort_path = x.average_shortest_path_length(comp)
        ashort_path_w = x.average_shortest_path_length(comp, weight="weight")
        frac_weakly_connected = 100*comp.number_of_nodes()/nnodes
        # ashort_path_uw = x.average_shortest_path_length(comp_,weight = "weight")
        weights = [i[2]["weight"] for i in gg.edges(data=True)]
        frac_strongly_connected = 100*x.strongly_connected_component_subgraphs(gg)[0].number_of_nodes()/nnodes
    else:
        comp = comp_
        weights = [1]*nedges
        frac_strongly_connected = frac_connected

    # nodes_edge  = 100*nnodes/nedges # correlated to degree
    # fraction of participants in the largest component
    # and strongly connected components
    overall_measures = _overallMeasures(locals())
    return locals()


def _overallMeasures(topom_dict):
    """Overall measures of a network.

    Used by: P.topology.measures.topologicalMeasures()"""
    vertex_measures = "degrees_", "strengths_", "clustering_", "clustering_w_", "square_clustering_", "closeness_", "eccentricity_"
    max_measures = "weights", "strengths_"
    network_measures = "nnodes", "nedges", "prob", "max_degree_empirical", "transitivity", "transitivity_u", "diameter", "radius", "frac_connected", "size_component", "ashort_path", "ashort_path_u", "ashort_path_w", "ashort_path_uw", "ncenter", "nperiphery", "frac_strongly_connected", "frac_weakly_connected",
    sector_measures = "sectorialized_nagents__",
    sector_vertex_measures = "sectorialized_degrees__",
    data_ = [(n.mean(topom_dict[i]), n.std(topom_dict[i])) for i in vertex_measures if i in topom_dict]
    data = [i for j in data_ for i in j]
    data += [max(topom_dict[i]) for i in max_measures if i in topom_dict]
    data += [topom_dict[i] for i in network_measures if i in topom_dict]
    # data_ = [(n.mean(topom_dict[i][j]), n.std(topom_dict[i][j])) for i in sector_vertex_measures for j in range(3)]
    # data += [i for j in data_ for i in j]
    # data += [topom_dict[i][j] for i in sector_vertex_measures for j in range(3)]
    # del data_, topom_dict
    del topom_dict
    return locals()

if __name__ == '__main__':
    # profiling with:
    # kernprof -l directMeasures.py
    # and then
    # python3 -m line_profiler directMeasures.py.lprof
    prefix = 'PREFIX po: <http://purl.org/socialparticipation/po/>\n'
    client = P.rdf.sparql.classes.LegacyClient('http://127.0.0.1:3030/adbname')
    snapshots = P.rdf.sparql.functions.plainQueryValues(client.retrieveQuery(prefix+'SELECT DISTINCT ?snap WHERE { ?s po:snapshot ?snap }'))
    for snapshot in snapshots[2:3]:
        q = '''SELECT ?friend1 ?friend2 WHERE {{
                ?friendshipfoo po:snapshot <{}> .
                ?friendshipfoo a po:Friendship .
                ?friendshipfoo po:member ?friend1 .
                ?friendshipfoo po:member ?friend2 .
                }}
        '''.format(snapshot, )
        friends = P.rdf.sparql.functions.plainQueryValues(client.retrieveQuery(prefix+q))
        g = x.Graph()
        for friend1, friend2 in friends:
            g.add_edge(friend1, friend2)
        topom_dict = P.measures.topology.directMeasures.topologicalMeasures(g)
