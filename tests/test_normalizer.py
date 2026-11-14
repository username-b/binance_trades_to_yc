import pandas as pd

from normalizer import TradesNormalizer


def test_normalizer_preserves_individual_trades() -> None:
    source = pd.DataFrame(
        [
            [2, "1.5", "3", "4.5", 1704067200001, False],
            [1, "1.0", "2", "2.0", 1704067200000, True],
        ],
        columns=["id", "price", "qty", "quote_qty", "time", "is_buyer_maker"],
    )

    result = TradesNormalizer().normalize(source)

    assert result["trade_id"].tolist() == [1, 2]
    assert len(result) == len(source)
    assert result["is_buyer_maker"].tolist() == [True, False]
