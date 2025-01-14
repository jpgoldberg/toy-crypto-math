from typing import Any
import pydot  # types: ignore
from toy_crypto.sec_games import Ind, IndEav, IndCpa, IndCca1, IndCca2


games: dict[str, object] = {
    "IND-EAV": IndEav,
    "IND-CPA": IndCpa,
    "IND-CCA1": IndCca1,
    "IND-CCA2": IndCca2,
}


def make_graph(game: Ind[Any], name: str) -> pydot.Graph:
    ttable = game.T_TABLE
    states: list[str] = list(ttable.keys())
    label = f"State transitions in {name} game"
    graph = pydot.Dot(name, graph_type="digraph", label=label, rankdir="LR")
    graph.set_node_defaults(shape="circle")

    for state in states:
        for label, destination in ttable[state].items():
            label = label + "()"
            label = f"  {label}  "
            edge = pydot.Edge(
                state,
                destination,
                label=label,
                fontname="courier",
                fontsize=12,
                labelfloat=True,
            )
            graph.add_edge(edge)

    return graph


for name, game in games.items():
    graph = make_graph(game, name)  # type: ignore[arg-type]
    graph.write_svg(f"{name}.svg")
