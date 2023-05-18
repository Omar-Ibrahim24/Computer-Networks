import networkx as nx
import matplotlib.pyplot as plt
from tabulate import tabulate

def read_graph(filename):
    with open(filename, 'r') as f:
        # Read the first line to get the number of nodes and edges
        n, m = map(int, f.readline().strip().split(','))
        # Create the graph
        G = nx.Graph()
        # Loop over the remaining lines to add edges to the graph
        for i in range(m):
            line = f.readline().strip().split(',')
            if len(line) != 3:
                continue
            src, dest, weight = line
            G.add_edge(src, dest, weight=int(weight))
        return G
    


def dijkstra_shortest_path(G, source):
    # Initialize distance and visited dictionaries
    dist = {node: float('inf') for node in G.nodes}
    dist[source] = 0
    visited = set()

    # Iterate until all nodes are visited
    while len(visited) != len(G.nodes):
        # Find the node with the minimum distance that has not been visited
        current_node = min(set(dist.keys()) - visited, key=dist.get)
        visited.add(current_node)

        # Update the distances of the neighboring nodes
        for neighbor in G.neighbors(current_node):
            new_distance = dist[current_node] + G[current_node][neighbor]['weight']
            if new_distance < dist[neighbor]:
                dist[neighbor] = new_distance

    # Return the shortest paths
    paths = {}
    for node in G.nodes:
        if node == source:
            paths[node] = [node]
        elif dist[node] == float('inf'):
            paths[node] = []
        else:
            path = nx.dijkstra_path(G, source=source, target=node, weight='weight')
            paths[node] = path
    return paths



def compute_shortest_path_trees(G):
    shortest_path_trees = {}
    #Now use for example node 'u' as source node and get shortest path to all the other nodes 
    for node in G.nodes:
        
        #Use Implemented function 
        shortest_path_trees[node] = dijkstra_shortest_path(G, node)
        
        # Use built in function single_source_dijkstra_path in networkx library
        # shortest_path_trees[node] = nx.single_source_dijkstra_path(G, node,weight='weight')
    return shortest_path_trees


def construct_forwarding_tables(G, shortest_path_trees):
    forwarding_tables = {}
    for node in G.nodes:
        forwarding_table = {}
        for dest in G.nodes:
            if node == dest:
                forwarding_table[dest] = None
            else:
                shortest_path = shortest_path_trees[node][dest]
                if len(shortest_path) > 2:
                    forwarding_table[dest] = shortest_path[1]
                else:
                    # If the shortest path has only one hop, use the destination node as the next hop
                    forwarding_table[dest] = dest
        forwarding_tables[node] = forwarding_table
    return forwarding_tables

def print_forwarding_tables(forwarding_tables):
    for node, table in forwarding_tables.items():
        print(f"Forwarding table for node {node}:")
        headers = ["Dest", "Next hop"]
        rows = []
        for dest, next_hop in table.items():
            rows.append([dest, next_hop])
        print(tabulate(rows, headers=headers))

def draw_graph(G):
    # Set node positions manually
    pos = nx.spring_layout(G)
    
    # Draw the graph
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=500, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=2, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=14, font_family='sans-serif', font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    label_pos = {k: (v[0], v[1] + 0.05) for k, v in pos.items()}
    nx.draw_networkx_edge_labels(G, edge_labels=edge_labels, font_size=12, font_family='sans-serif', pos=label_pos)
    # Show the graph
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    G = read_graph('input1.txt')
    shortest_path_trees = compute_shortest_path_trees(G)
    forwarding_tables = construct_forwarding_tables(G, shortest_path_trees)
    print_forwarding_tables(forwarding_tables)
    draw_graph(G)
