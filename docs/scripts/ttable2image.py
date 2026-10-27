import pydot

from toy_crypto.sec_games import Ind, IndCca1, IndCca2, IndCpa, IndEav, State


def make_graph(game: type[Ind], name: str) -> pydot.Dot:
    ttable = game.T_TABLE
    states: list[State] = list(ttable.keys())
    label = f"State transitions in {name} game"
    graph = pydot.Dot(
        name,
        graph_type="digraph",
        rankdir="LR",
        ranksep=1.5,
        nodesep=0.75,
    )
    graph.set_node_defaults(shape="circle")
    graph.set_edge_defaults(
        penwidth=0.75,
        labelfloat=True,
        fontname="Anonymous Pro Bold",
        fontsize=12,
    )

    for state in states:
        for label, destination in ttable[state].items():
            label = label + "()"
            edge = pydot.Edge(state, destination, label=label)
            graph.add_edge(edge)

    return graph

def main() -> None:

    games: dict[str, type[Ind]] = {
        "IND-EAV": IndEav,
        "IND-CPA": IndCpa,
        "IND-CCA1": IndCca1,
        "IND-CCA2": IndCca2,
    }
    for name, game in games.items():
        graph: pydot.Graph = make_graph(game, name)
        graph.write_dot(f"{name}.gv")  # type: ignore[missing-attribute]

if __name__ == '__main__':
    main()
