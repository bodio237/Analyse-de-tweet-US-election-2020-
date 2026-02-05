from __future__ import annotations
import pandas as pd
import re
from dataclasses import dataclass

@dataclass
class GeographyAnalyzer:
    """
    Object-Oriented geographic analysis based on a 'location' column.

    - load(): read CSV safely
    - compare(): compare Biden vs Trump tweet counts by location
    """
    sep: str = ";"
    encoding: str = "utf-8"

    def load(self, path: str) -> pd.DataFrame:
        return pd.read_csv(
            path,
            sep=self.sep,
            dtype=str,
            encoding=self.encoding,
            low_memory=False,
            on_bad_lines="skip"
        )

    @staticmethod
    def find_location_column(df: pd.DataFrame) -> str:
        for col in df.columns:
            if "location" in col.lower():
                return col
        raise ValueError("No location column found")

    @staticmethod
    def clean_location(text) -> str | None:
        if pd.isna(text):
            return None
        s = str(text).lower()
        s = re.sub(r"[^a-zA-Z\s]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s if s else None

    def tweets_by_location(self, df: pd.DataFrame) -> pd.Series:
        loc_col = self.find_location_column(df)
        locations = df[loc_col].dropna().apply(self.clean_location).dropna()
        return locations.value_counts()

    def compare(self, biden_df: pd.DataFrame, trump_df: pd.DataFrame) -> pd.DataFrame:
        biden_counts = self.tweets_by_location(biden_df)
        trump_counts = self.tweets_by_location(trump_df)

        comparison = pd.DataFrame({"Biden": biden_counts, "Trump": trump_counts}).fillna(0)
        comparison["diff"] = comparison["Biden"] - comparison["Trump"]
        comparison["total"] = comparison["Biden"] + comparison["Trump"]

        return comparison.reset_index().rename(columns={"index": "user_location"})


# ---- Compatibilité (si ancien code utilise encore ces fonctions)
def load_twitter_csv(path: str) -> pd.DataFrame:
    return GeographyAnalyzer().load(path)

def compare_candidates(biden_df: pd.DataFrame, trump_df: pd.DataFrame) -> pd.DataFrame:
    return GeographyAnalyzer().compare(biden_df, trump_df)