import polars as pl

def set_cell(df, row, col, value):
    return df.with_columns(
        pl.when(pl.int_range(pl.len()) == row)
        .then(pl.lit(value))
        .otherwise(pl.col(col))
        .alias(col)
    )

#df = set_cell(df, 1, "name", "John")
