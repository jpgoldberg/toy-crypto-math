from collections import defaultdict
from typing import Any
import pydot  # types: ignore
from toy_crypto.sec_games import Ind, IndEav, IndCpa, IndCca1, IndCca2
from toy_crypto.sec_games import (
    STATE_CHALLANGE_CREATED,
    STATE_INITIALIZED,
    STATE_STARTED,
)


games: dict[str, object] = {
    "IND-EAV": IndEav,
    "IND-CPA": IndCpa,
    "IND-CCA1": IndCca1,
    "IND-CCA2": IndCca2,
}

extra_state_abbr: list[str] = list("αβγδεζηθικλμνξπρστφχψω")[::-1]


def missing_abbr() -> str:
    return extra_state_abbr.pop()


state_abbr = defaultdict(
    missing_abbr,
    {STATE_STARTED: "S", STATE_INITIALIZED: "I", STATE_CHALLANGE_CREATED: "C"},
)


def make_graph(game: Ind[Any], name: str) -> pydot.Graph:
    ttable = game.T_TABLE
    states: list[str] = list(ttable.keys())
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
            label = f"  {label}  "
            edge = pydot.Edge(
                state_abbr[state],
                state_abbr[destination],
                label=label,
            )
            graph.add_edge(edge)

    return graph


for name, game in games.items():
    graph: pydot.Graph = make_graph(game, name)  # type: ignore[arg-type]
    graph.write_raw(f"{name}.gv")
