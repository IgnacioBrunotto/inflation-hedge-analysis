"""
Run the full data pipeline in order. Run from the repo root: python src/pipeline.py
"""

from ingest import main as run_ingest
from load import main as run_load
from validate import main as run_validate 
from transform import main as run_transform
from export import main as run_export

STEPS = [
    ("ingest", run_ingest),
    ("load", run_load),
    ("validate", run_validate),
    ("transform", run_transform),
    ("export", run_export),
]


def main():
    for step_number, (step_name, step_function) in enumerate(STEPS, start=1):
        print(f"===Step {step_number}/{len(STEPS)}: {step_name}")
        step_function()


    print("Pipeline finished sucesfully")


if __name__ == "__main__":
    main()