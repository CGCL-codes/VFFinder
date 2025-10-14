import networkx as nx


def deepwalk_embed(G):
    n = G.number_of_nodes()
    if n == 0:
        return [0.0] * 21
    m = G.number_of_edges()
    degrees = [d for _, d in G.degree()]
    mean_deg = sum(degrees) / float(n)
    max_deg = max(degrees)
    min_deg = min(degrees)
    hist_bins = [0] * 10
    for d in degrees:
        idx = d if d < 9 else 9
        hist_bins[idx] += 1
    hist = [x / float(n) for x in hist_bins]
    try:
        c = nx.average_clustering(G.to_undirected())
    except Exception:
        c = 0.0
    try:
        pr = nx.pagerank(G.to_undirected())
        top_pr = sorted(pr.values(), reverse=True)[:5]
    except Exception:
        top_pr = []
    while len(top_pr) < 5:
        top_pr.append(0.0)
    vec = [float(n), float(m), float(mean_deg), float(max_deg), float(min_deg), float(c)] + [float(x) for x in hist] + [float(x) for x in top_pr]
    return vec


