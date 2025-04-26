import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

CVS_FILE = "timings.csv"

"""
size,Sieve,IntSieve,SetSieve
100,0.0002202501054853201,0.00001795799471437931,0.000032499898225069046
1000,0.000016040867194533348,0.0002026669681072235,0.00008208304643630981
10000,0.00011612498201429844,0.007421791087836027,0.0008759999182075262
100000,0.0010569170117378235,0.5530140828341246,0.010142415994778275
1000000,0.011054749833419919,60.09357604198158,0.1988552080001682
"""


def main() -> None:
    df_wide = pl.read_csv(
        CVS_FILE, new_columns=["size", "bitarray", "py_int", "py_set"]
    )
    df = df_wide.unpivot(
        index="size", variable_name="sieve_type", value_name="time"
    )

    # print(df)

    p=sns.relplot(
        data=df,
        kind="line",
        x="size",
        y="time",
        hue="sieve_type",
        
    )
    p.set(xscale="log")

    # plt.show()

    p.set(xlim=(100, 10**4), ylim=(0, 0.01))
    plt.show()


if __name__ == "__main__":
    main()
