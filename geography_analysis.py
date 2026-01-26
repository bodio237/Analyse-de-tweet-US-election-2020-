# src/geography_analysis.py

import pandas as pd

class GeographyAnalyzer:
    # Liste des 50 états US + DC
    US_STATES = [
        'ALABAMA','ALASKA','ARIZONA','ARKANSAS','CALIFORNIA','COLORADO','CONNECTICUT',
        'DELAWARE','FLORIDA','GEORGIA','HAWAII','IDAHO','ILLINOIS','INDIANA','IOWA',
        'KANSAS','KENTUCKY','LOUISIANA','MAINE','MARYLAND','MASSACHUSETTS','MICHIGAN',
        'MINNESOTA','MISSISSIPPI','MISSOURI','MONTANA','NEBRASKA','NEVADA','NEW HAMPSHIRE',
        'NEW JERSEY','NEW MEXICO','NEW YORK','NORTH CAROLINA','NORTH DAKOTA','OHIO',
        'OKLAHOMA','OREGON','PENNSYLVANIA','RHODE ISLAND','SOUTH CAROLINA','SOUTH DAKOTA',
        'TENNESSEE','TEXAS','UTAH','VERMONT','VIRGINIA','WASHINGTON','WEST VIRGINIA',
        'WISCONSIN','WYOMING','DISTRICT OF COLUMBIA'
    ]

    def __init__(self, df: pd.DataFrame, candidate_name: str):
        """
        Initialise l'analyzer avec le DataFrame et le nom du candidat
        """
        self.df = df.copy()
        self.candidate = candidate_name

    def filter_us_states(self) -> pd.DataFrame:
        """
        Retourne un DataFrame filtré uniquement avec les États US
        """
        df_filtered = self.df[self.df['state'].str.upper().isin(self.US_STATES)]
        return df_filtered

    def tweets_per_state(self, top_n=None) -> pd.Series:
        """
        Retourne le nombre de tweets par État
        """
        counts = self.df['state'].value_counts()
        if top_n:
            counts = counts.head(top_n)
        return counts

    def comparison_with(self, other) -> pd.DataFrame:
        """
        Compare le nombre de tweets par État avec un autre analyzer
        """
        if not isinstance(other, GeographyAnalyzer):
            raise TypeError("L'autre objet doit être un GeographyAnalyzer")
        df_self = self.df['state'].value_counts()
        df_other = other.df['state'].value_counts()
        comparison = pd.DataFrame({
            self.candidate: df_self,
            other.candidate: df_other
        }).fillna(0)
        return comparison
