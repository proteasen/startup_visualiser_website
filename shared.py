from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "Sustainability_Startups_in_ASEAN_Startups.csv")
df_additional = pd.read_csv(app_dir / "Southeast_Asia_Startups_with_Funding_Rounds_Green_Economy_past_to_Q3_2024.csv")
