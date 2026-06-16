import json
import os
import numpy as np
from pathlib import Path

def compute_statistics(data_dir="swing_angles_data", output_dir="swing_angles_data"):
    """
    Compute mean and standard deviation for each metric by swing type and phase.
    """
    os.makedirs(output_dir, exist_ok=True)

    input_file = os.path.join(data_dir, "all_swing_angles.json")

    if not os.path.exists(input_file):
        print(f"Data file not found: {input_file}")
        print("Run analyze_swing_pipeline.py first to collect swing data.")
        return

    with open(input_file, 'r') as f:
        all_angles = json.load(f)

    metrics = [
        "left_arm_angle",
        "right_arm_angle",
        "spine_angle",
        "hip_angle",
        "shoulder_tilt",
        "knee_bend",
        "shoulder_rotation",
        "hip_rotation",
        "x_factor",
    ]

    stats = {
        "driver": {},
        "iron": {},
        "all": {}
    }

    for swing_type in ['driver', 'iron', 'all']:
        if swing_type == 'all':
            videos_data = {**all_angles.get('driver', {}), **all_angles.get('iron', {})}
        else:
            videos_data = all_angles.get(swing_type, {})

        if not videos_data:
            print(f"No data found for swing type: {swing_type}")
            continue

        stats[swing_type] = {}

        for phase_name in [
            "setup",
            "takeaway",
            "top_of_backswing",
            "downswing",
            "impact",
            "follow_through",
        ]:
            phase_metrics = {metric: [] for metric in metrics}

            for video_name, phases in videos_data.items():
                if phase_name in phases and phases[phase_name] is not None:
                    phase_data = phases[phase_name]
                    for metric in metrics:
                        if metric in phase_data:
                            phase_metrics[metric].append(phase_data[metric])

            if phase_metrics[metrics[0]]:
                stats[swing_type][phase_name] = {}
                print(f"\n{swing_type.upper()} - {phase_name.upper()}:")
                print(f"  (based on {len(phase_metrics[metrics[0]])} video(s))")

                for metric in metrics:
                    values = np.array(phase_metrics[metric])
                    if len(values) > 0:
                        mean = float(np.mean(values))
                        std = float(np.std(values)) if len(values) > 1 else 0.0

                        stats[swing_type][phase_name][metric] = {
                            "mean": round(mean, 2),
                            "std": round(std, 2),
                            "count": len(values)
                        }

                        print(f"  {metric}: {mean:.2f}° ± {std:.2f}°")

    output_file = os.path.join(output_dir, "swing_statistics.json")
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n\nStatistics saved to {output_file}")

    print_summary(stats)

def print_summary(stats):
    """
    Print a human-readable summary of statistics.
    """
    print("\n" + "="*80)
    print("SWING ANALYSIS SUMMARY")
    print("="*80)

    for swing_type in ['driver', 'iron', 'all']:
        if swing_type not in stats or not stats[swing_type]:
            continue

        print(f"\n{swing_type.upper()} SWING ANALYSIS:")
        print("-" * 80)

        type_data = stats[swing_type]
        for phase_name in sorted(type_data.keys()):
            phase_data = type_data[phase_name]
            if not phase_data:
                continue

            print(f"\n  {phase_name.replace('_', ' ').title()}:")
            for metric, values in sorted(phase_data.items()):
                mean = values['mean']
                std = values['std']
                count = values['count']
                print(f"    {metric.replace('_', ' ').title():25} {mean:6.2f}° ± {std:5.2f}° (n={count})")

if __name__ == "__main__":
    compute_statistics()
