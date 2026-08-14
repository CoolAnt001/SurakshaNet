import random
import math
from datetime import datetime
from data.database import get_db_connection

def generate_laplace_noise(sensitivity: float, epsilon: float) -> float:
    """
    Generates noise from a Laplace distribution with mean 0 and scale (sensitivity / epsilon).
    Using pure Python inverse transform sampling to avoid dependency failures.
    """
    if epsilon <= 0:
        raise ValueError("Epsilon must be greater than 0")
    
    scale = sensitivity / epsilon
    u = random.random() - 0.5
    # Sign of u, times -scale, times natural log of (1 - 2*|u|)
    return -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))

def process_local_data(
    raw_records: list, 
    area_id: str, 
    epsilon: float = 1.0, 
    sensitivity: float = 1.0, 
    min_group_size: int = 10
) -> dict:
    """
    Simulates local node processing:
    1. Identifier removal (PII scrubbing)
    2. Aggregation by symptom category
    3. Small group protection (suppression of low aggregates)
    4. Differential Privacy (Laplace noise)
    5. Database audit logging
    """
    # 1. Identifier Removal (Only keep symptom category for aggregation)
    scrubbed_records = []
    for record in raw_records:
        scrubbed_records.append({
            "symptom": record.get("symptom")
        })

    # 2. Aggregation
    aggregates = {}
    for rec in scrubbed_records:
        symptom = rec["symptom"]
        if symptom:
            aggregates[symptom] = aggregates.get(symptom, 0) + 1

    # 3 & 4. Suppression & Noise addition
    payload = {}
    conn = get_db_connection()
    cursor = conn.cursor()

    for symptom, count in aggregates.items():
        # Match symptom to database signal_id
        signal_map = {
            "diarrhea": "gastrointestinal",
            "fever": "fever",
            "cough": "respiratory"
        }
        signal_id = signal_map.get(symptom.lower(), symptom)

        # Check suppression
        if count < min_group_size:
            status = "SUPPRESSED"
            noise = 0.0
            noised_count = None
            payload[signal_id] = "SUPPRESSED"
        else:
            status = "TRANSMITTED"
            noise = generate_laplace_noise(sensitivity, epsilon)
            # Round for readable reporting but keep float accuracy
            noised_count = round(count + noise, 2)
            payload[signal_id] = noised_count

        # 5. Audit log
        cursor.execute("""
        INSERT INTO privacy_audits (area_id, signal_id, raw_count, noise_added, noised_count, epsilon, sensitivity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (area_id, signal_id, count, noise if status == "TRANSMITTED" else None, noised_count, epsilon, sensitivity, status))

    conn.commit()
    conn.close()

    return payload
