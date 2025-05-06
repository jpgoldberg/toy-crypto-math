import io
import polars as pl
from polars.datatypes import UInt32, Float32
from polars.dataframe.frame import DataFrame as PolarsDF
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def load_data() -> PolarsDF:
    """Idiosyncratic things for building our specific dataframe."""

    cvs_data = b"""
        size,Sieve,IntSieve,SetSieve
        100,0.00017137499526143074,0.000017999671399593353,0.000042750034481287
        1000,0.000016292091459035873,0.00017720786854624748,0.0000866670161485672
        10000,0.00010245898738503456,0.007494000252336264,0.0008742911741137505
        100000,0.0010270839557051659,0.5487742917612195,0.009959292132407427
        1000000,0.010919792111963034,59.795512250158936,0.19800291722640395
        50,2.0833685994148254e-6,0.000013249926269054413,0.000014875084161758423
        500,1.2922100722789764e-6,0.00007804157212376595,0.00004054093733429909
        5000,1.25030055642128e-6,0.002527667209506035,0.0004529156722128391
        50000,1.3331882655620575e-6,0.14295708294957876,0.004889749921858311
        500000,7.2498805820941925e-6,15.271088582929224,0.07385779218748212
    """.replace(b" ", b"")

    # We don't need 64 bit precision
    schema = {
        "size": UInt32,
        "bitarray": Float32,
        "int": Float32,
        "set": Float32,
    }

    CVS_DATA = io.BytesIO(cvs_data)
    # CVS_FILE = "timings.csv"
    df_wide = pl.read_csv(
        CVS_DATA,
        schema=schema,
        # skip_lines=1,
        # has_header=False,
    )

    df = df_wide.unpivot(
        index="size", variable_name="sieve_type", value_name="time"
    )
    return df


def base_g(data: PolarsDF, title: str | None = None) -> Figure:
    """Returns a FacetGrid which can be the base for several plots.

    For reasons I don't understand, it appears that once a plot is shown
    or saved, the object is destroyed. And I didn't find a way create
    a copy of a plot or subplot in a usable way.
    """

    # We want to keep colors constant even for graph that
    # doesn't have "py_int"
    hue_order = ["bitarray", "set"]
    if "int" in data["sieve_type"]:
        hue_order.append("int")

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
    g._legend.set_title("Sieve type")  # type: ignore

    if title:
        g.figure.subplots_adjust(top=0.95)
        g.set(title=title)

    return g.figure


def main() -> None:
    df = load_data()

    sns.set_theme(
        style="white",
        palette="colorblind6",
        font="Fira Sans",
    )

    # Whole plot
    fig = base_g(df, title="Sieve creation timings for size up to 1 million")
    fig.savefig("all_data.png")
    plt.show()

    xmax = 10**4
    df_e4 = df.filter(pl.col("size") <= xmax)
    fig = base_g(df_e4, title="Sieve creation timings for size up to 10000")
    fig.savefig("to_10_000.png")
    plt.show()

    df_sans_int = df.filter(pl.col("sieve_type") != "int")
    fig = base_g(
        df_sans_int, title="Sieve creation times for bitarray and set only"
    )
    fig.savefig("sans_int.png")
    plt.show()


if __name__ == "__main__":
    main()
