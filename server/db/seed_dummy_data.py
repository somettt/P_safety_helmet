from db_writer import insert_analysis_result


DUMMY_RESULTS = [
    {
        "device_id": "helmet_001",
        "helmet": 1,
        "risk": "LOW",
        "sensor": {
            "temp": 25.4,
            "noise": 63.2,
        },
    },
    {
        "device_id": "helmet_002",
        "helmet": 1,
        "risk": "MID",
        "sensor": {
            "temp": 33.8,
            "noise": 76.5,
        },
    },
    {
        "device_id": "helmet_003",
        "helmet": 0,
        "risk": "HIGH",
        "sensor": {
            "temp": 29.1,
            "noise": 82.4,
        },
    },
    {
        "device_id": "helmet_004",
        "helmet": 1,
        "risk": "HIGH",
        "sensor": {
            "temp": 61.2,
            "noise": 88.9,
        },
    },
]


def main():
    for result in DUMMY_RESULTS:
        insert_analysis_result(result)
        print(
            f"[DUMMY INSERTED] "
            f"device_id={result['device_id']} "
            f"risk={result['risk']} "
            f"temp={result['sensor']['temp']} "
            f"noise={result['sensor']['noise']}"
        )

    print("Dummy data insert complete")


if __name__ == "__main__":
    main()
