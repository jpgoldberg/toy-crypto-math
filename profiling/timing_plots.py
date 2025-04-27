import polars as pl
from polars.dataframe.frame import DataFrame as PolarsDF
import seaborn as sns
import matplotlib.pyplot as plt
from seaborn import FacetGrid


def load_data() -> PolarsDF:
    """Idiosyncratic things for building our specific dataframe."""

    """
    size,Sieve,IntSieve,SetSieve
    100,0.0002202501054853201,0.00001795799471437931,0.000032499898225069046
    1000,0.000016040867194533348,0.0002026669681072235,0.00008208304643630981
    10000,0.00011612498201429844,0.007421791087836027,0.0008759999182075262
    100000,0.0010569170117378235,0.5530140828341246,0.010142415994778275
    1000000,0.011054749833419919,60.09357604198158,0.1988552080001682
    """

    CVS_FILE = "timings.csv"
    df_wide = pl.read_csv(
        CVS_FILE, new_columns=["size", "bitarray", "py_int", "py_set"]
    )
    df = df_wide.unpivot(
        index="size", variable_name="sieve_type", value_name="time"
    )
    return df


CVS_FILE = "timings.csv"

"""
size,Sieve,IntSieve,SetSieve
100,0.0002202501054853201,0.00001795799471437931,0.000032499898225069046
1000,0.000016040867194533348,0.0002026669681072235,0.00008208304643630981
10000,0.00011612498201429844,0.007421791087836027,0.0008759999182075262
100000,0.0010569170117378235,0.5530140828341246,0.010142415994778275
1000000,0.011054749833419919,60.09357604198158,0.1988552080001682
"""


def base_g(data: PolarsDF, title: str | None = None) -> FacetGrid:
    """Returns a FacetGrid which can be the base for several plots.

    For reasons I don't understand, it appears that once a plot is shown
    or saved, the object is destroyed. And I didn't find a way create
    a copy of a plot or subplot in a usable way.
    """

    # We want to keep colors constant even for graph that
    # doesn't have "py_int"
    hue_order = ["bitarray", "py_set"]
    if "py_int" in data["sieve_type"]:
        hue_order.append("py_int")

    g = sns.relplot(
        data=data,
        kind="line",
        x="size",
        y="time",
        hue="sieve_type",
        hue_order=hue_order,
        linewidth=2,
    )
    g.set(
        xscale="log",
        xlabel="Sieve size",
        ylabel="Time (seconds)",
    )
    # This does not feel cool, but is the best I can do for now
    g._legend.set_title("Sieve type")
    if title:
        g.set(title=title)
    return g


def main() -> None:
    df = load_data()

    sns.set_theme(
        style="white",
        palette="colorblind6",
        font="Fira Sans",
    )

    # Whole plot
    _ = base_g(df, title="Sieve creation timings for size up to 1 million")
    plt.show()

    xmax = 10**4
    df_e4 = df.filter(pl.col("size") <= xmax)
    _ = base_g(df_e4, title="Sieve creation timings for size up to 10000")
    plt.show()

    df_sans_int = df.filter(pl.col("sieve_type") != "py_int")
    _ = base_g(
        df_sans_int, title="Sieve creation times for bitarray and set only"
    )
    plt.show()


if __name__ == "__main__":
    main()
