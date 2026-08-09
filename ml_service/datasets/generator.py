import pandas as pd
import numpy as np
import random
from datetime import datetime
from pathlib import Path

np.random.seed(42)
random.seed(42)

genres_list = [i for i in range(0, 20)]

countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Italy', 'Spain', 'Australia', 'Japan', 'South Korea', 'India']
directors = list(range(0, 101))
writers = list(range(0, 101))
producers = list(range(0, 101))


def generate_dataset(n):
    print(f"creating random dataset with {n} rows...")
    data = []
    print(".")
    for i in range(n):
        user_id = random.randint(1, 1000)
        account_age_days = random.randint(1, 1095)
        active_days = random.randint(1, account_age_days)

        total_views = random.randint(0, 2000)
        total_likes = random.randint(0, 500)
        total_saves = random.randint(0, 200)
        total_shares = random.randint(0, 100)
        total_comments = random.randint(0, 300)
        total_searches = random.randint(0, 800)
        total_watches = random.randint(0, 500)
        total_completes = random.randint(0, total_watches)

        weights = {'View': 0.2, 'Like': 1.0, 'Save': 1.5, 'Comment': 0.5,
                   'Share': 1.2, 'Search': 0.1, 'Watch': 0.7, 'Complete': 1.2}

        interactions = [
            weights['View'] * total_views,
            weights['Like'] * total_likes,
            weights['Save'] * total_saves,
            weights['Share'] * total_shares,
            weights['Comment'] * total_comments,
            weights['Search'] * total_searches,
            weights['Watch'] * total_watches,
            weights['Complete'] * total_completes
        ]
        total_interaction_count = sum([
            total_views, total_likes, total_saves, total_shares,
            total_comments, total_searches, total_watches, total_completes
        ])
        avg_interaction_weight = sum(interactions) / total_interaction_count if total_interaction_count > 0 else 0

        favorite_genres = random.sample(genres_list, 5)

        preferred_runtime = random.randint(60, 180)
        preferred_release_year = random.randint(1980, 2024)

        favorite_directors = random.sample(directors, 5)
        favorite_writers = random.sample(writers, 5)

        movie_id = random.randint(1000, 9999)
        genres = random.sample(genres_list, 5)
        rate = round(random.uniform(1.0, 10.0), 1)
        release_year = random.randint(1980, 2024)
        runtime = random.randint(60, 180)
        country = random.choice(countries)
        is_series = random.choice([True, False])
        adult = random.choice([True, False])
        director_id = random.randint(1, 100)
        writer_id = random.randint(1, 100)
        producer_id = random.randint(1, 100)

        popularity = random.randint(0, 10000)

        user_movie_interactions = {
            'View': random.randint(0, 10),
            'Like': random.randint(0, 1),
            'Save': random.randint(0, 1),
            'Share': random.randint(0, 1),
            'Comment': random.randint(0, 3),
            'Search': random.randint(0, 5),
            'Watch': random.randint(0, 1),
            'Complete': random.randint(0, 1)
        }

        target_score = sum([
            weights['View'] * user_movie_interactions['View'],
            weights['Like'] * user_movie_interactions['Like'],
            weights['Save'] * user_movie_interactions['Save'],
            weights['Share'] * user_movie_interactions['Share'],
            weights['Comment'] * user_movie_interactions['Comment'],
            weights['Search'] * user_movie_interactions['Search'],
            weights['Watch'] * user_movie_interactions['Watch'],
            weights['Complete'] * user_movie_interactions['Complete']
        ])
        target_score = round(target_score, 2)

        data.append({
            "user_id": user_id,
            "movie_id": movie_id,
            "target_score": target_score,
            "account_age_days": account_age_days,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_saves": total_saves,
            "total_shares": total_shares,
            "total_comments": total_comments,
            "total_searches": total_searches,
            "total_watches": total_watches,
            "total_completes": total_completes,
            "avg_interaction_weight": round(avg_interaction_weight, 2),
            "favorite_genres": favorite_genres,
            "preferred_runtime": preferred_runtime,
            "preferred_release_year": preferred_release_year,
            "favorite_directors": favorite_directors,
            "favorite_writers": favorite_writers,
            "user_interaction_count": total_interaction_count,
            "active_days": active_days,
            "genres": genres,
            "rate": rate,
            "release_year": release_year,
            "runtime": runtime,
            "country": country,
            "is_series": is_series,
            "adult": adult,
            "director_id": director_id,
            "writer_id": writer_id,
            "producer_id": producer_id,
            "popularity": popularity,
        })
    print(".")
    return pd.DataFrame(data)


df = generate_dataset(10000)

output_dir = Path("raw")
output_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"dataset_{timestamp}.csv"
print(".")
df.to_csv(output_file, index=False)
print("dataset created.")
