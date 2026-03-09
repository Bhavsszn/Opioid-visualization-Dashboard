import pandas as pd
import psycopg2

# connection
conn = psycopg2.connect(
    host="ep-silent-hall-a4jqxmf3-pooler.us-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_3lpZ6TCJPAmB",
    port=5432,
    sslmode="require"
)

cursor = conn.cursor()

# load dataset
df = pd.read_csv("data/overdoses_state_year_clean_typed.csv")

for _, row in df.iterrows():
    cursor.execute(
        """
        INSERT INTO analytics.state_year_overdoses
        (state, year, deaths, population, crude_rate, age_adjusted_rate)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (state, year)
        DO UPDATE SET
            deaths = EXCLUDED.deaths,
            population = EXCLUDED.population,
            crude_rate = EXCLUDED.crude_rate,
            age_adjusted_rate = EXCLUDED.age_adjusted_rate;
        """,
        (
            row["state"],
            int(row["year"]),
            None if pd.isna(row["deaths"]) else float(row["deaths"]),
            None if pd.isna(row["population"]) else float(row["population"]),
            None if pd.isna(row["crude_rate"]) else float(row["crude_rate"]),
            None if pd.isna(row["age_adjusted_rate"]) else float(row["age_adjusted_rate"]),
        ),
    )

conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully")
