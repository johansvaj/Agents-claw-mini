# modules/knowledge_graph.py
import json
import os
import networkx as nx

class KnowledgeGraph:
    def __init__(self, store_path: str = "~/.nexcorix/kg.json"):
        self.store_path = os.path.expanduser(store_path)
        self.graph = nx.DiGraph()
        self.load()

    def load(self):
        if os.path.exists(self.store_path):
            with open(self.store_path, 'r') as f:
                data = json.load(f)
                self.graph = nx.node_link_graph(data)

    def save(self):
        data = nx.node_link_data(self.graph)
        with open(self.store_path, 'w') as f:
            json.dump(data, f)

    def add_fact(self, subject: str, predicate: str, obj: str):
        self.graph.add_edge(subject, obj, label=predicate)
        self.save()

    def query(self, subject: str, predicate: str = None) -> list:
        if predicate:
            return [v for u,v,data in self.graph.out_edges(subject, data=True) if data.get('label') == predicate]
        return list(self.graph.successors(subject))
