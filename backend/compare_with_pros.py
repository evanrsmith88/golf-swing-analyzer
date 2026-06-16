import json
import os
from analyze_swing_pipeline import process_video

PHASE_LABELS = {
    "setup": "Setup",
    "takeaway": "Takeaway",
    "top_of_backswing": "Top of backswing",
    "downswing": "Downswing",
    "impact": "Impact",
    "follow_through": "Follow-through",
}

METRIC_LABELS = {
    "left_arm_angle": "Left arm angle",
    "right_arm_angle": "Right arm angle",
    "spine_angle": "Spine angle",
    "hip_angle": "Hip angle",
    "shoulder_tilt": "Shoulder tilt",
    "knee_bend": "Knee bend",
    "shoulder_rotation": "Shoulder rotation",
    "hip_rotation": "Hip rotation",
    "x_factor": "X-factor",
}


def load_statistics(stats_path):
    if not os.path.exists(stats_path):
        raise FileNotFoundError(
            f"Statistics file not found: {stats_path}. Run compute_statistics.py first."
        )

    with open(stats_path, "r") as f:
        return json.load(f)


def build_feedback_rules():
    rules = {
        "top_of_backswing": {
            "left_arm_angle": {
                "low": "Your lead arm bends more than pro range at the top. Keep the lead arm longer to create a wider arc and improve consistency.",
                "high": "Your lead arm looks very rigid at the top. Keep structure, but avoid locking the elbow so the backswing stays athletic.",
            },
            "x_factor": {
                "low": "Your shoulders and hips are turning too much together at the top. Try adding shoulder turn while keeping your lower body quieter.",
                "high": "You create a lot of separation at the top. Great power potential, but make sure you can sequence down without getting stuck.",
            },
            "hip_rotation": {
                "low": "You have less hip turn than pro patterns at the top. Let the trail hip rotate back a bit more to reduce arm lift compensation.",
                "high": "Your hips are rotating more than pro range at the top. Keep some resistance in the lower body to preserve stretch.",
            },
        },
        "downswing": {
            "knee_bend": {
                "low": "You are losing knee flex early in transition. Keep posture longer before extending to improve strike control.",
                "high": "You keep a lot of knee flex in transition. Allow pressure to move and extend through the ground to free up rotation.",
            },
            "hip_rotation": {
                "low": "Your hips are not opening enough in the downswing. Start from the ground up and clear the lead hip earlier.",
                "high": "Your hips may be opening too quickly relative to your arms. Smooth sequencing can help avoid blocks and wipes.",
            },
            "spine_angle": {
                "low": "You may be standing up in transition. Keep chest inclination more stable as you move down.",
                "high": "You keep a lot of forward bend in transition. Maintain room for your arms so you do not get trapped.",
            },
        },
        "impact": {
            "left_arm_angle": {
                "low": "Lead arm is more bent than pro range at impact. Focus on width and handle control through strike.",
                "high": "Lead arm is very extended at impact. Good compression pattern, just make sure you are not over-reaching.",
            },
            "hip_rotation": {
                "low": "Hips are less open than pro range at impact. Work on clearing the lead side earlier.",
                "high": "Hips are very open at impact. Great if centered, but watch for blocks if the arms lag behind.",
            },
            "spine_angle": {
                "low": "Your posture appears to rise through impact. Try to stay in posture longer for cleaner contact.",
                "high": "You maintain significant bend through impact. Good if centered, but avoid crowding your arms.",
            },
            "x_factor": {
                "low": "Separation at impact is below pro range. Improve rotational sequence: lower body leads, torso follows, then arms.",
                "high": "Separation at impact is high. Powerful move, but ensure timing so face/path remain controlled.",
            },
        },
        "setup": {
            "knee_bend": {
                "low": "Setup knee flex is lower than pro range. Add slight athletic flex for balance and ground force use.",
                "high": "Setup knee flex is deeper than pro range. Stand a touch taller to improve turn freedom.",
            },
            "spine_angle": {
                "low": "Setup posture is more upright than pro range. Add a bit more hip hinge to create space for arm swing.",
                "high": "Setup posture is more bent than pro range. Reduce hinge slightly to stay dynamic and avoid getting stuck.",
            },
        },
    }
    return rules


def compare_phase(phase_name, user_phase_data, benchmark_phase_data, rules):
    comparisons = {}
    feedback = []

    if not user_phase_data or not benchmark_phase_data:
        return comparisons, feedback

    for metric, user_value in user_phase_data.items():
        if metric not in benchmark_phase_data:
            continue

        benchmark = benchmark_phase_data[metric]
        mean = benchmark["mean"]
        std = benchmark["std"]

        lower = mean - std
        upper = mean + std

        if user_value < lower:
            status = "below_pro_range"
        elif user_value > upper:
            status = "above_pro_range"
        else:
            status = "within_pro_range"

        comparisons[metric] = {
            "user": round(float(user_value), 2),
            "pro_mean": mean,
            "pro_std": std,
            "pro_range_1std": [round(lower, 2), round(upper, 2)],
            "status": status,
            "delta_from_mean": round(float(user_value - mean), 2),
        }

        if phase_name in rules and metric in rules[phase_name] and status != "within_pro_range":
            direction = "low" if status == "below_pro_range" else "high"
            feedback.append(rules[phase_name][metric][direction])

    return comparisons, feedback


def pick_top_feedback(feedback_items, max_items=3):
    unique = []
    seen = set()

    for item in feedback_items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:max_items]


def compare_user_swing(
    user_video_path="sample_videos/swing.mp4",
    stats_path="swing_angles_data/swing_statistics.json",
    benchmark_type="all",
    output_dir="swing_angles_data",
):
    os.makedirs(output_dir, exist_ok=True)

    stats = load_statistics(stats_path)
    if benchmark_type not in stats:
        raise ValueError(
            f"benchmark_type must be one of {list(stats.keys())}, got '{benchmark_type}'"
        )

    benchmark_stats = stats[benchmark_type]

    print(f"Processing user swing video: {user_video_path}")
    user_phases = process_video(user_video_path)

    if not user_phases:
        raise RuntimeError("Could not extract angles from user swing video.")

    rules = build_feedback_rules()

    comparison_result = {
        "benchmark_type": benchmark_type,
        "user_video": user_video_path,
        "phase_analysis": {},
        "summary_feedback": [],
    }

    all_feedback = []

    for phase_name, user_phase_data in user_phases.items():
        benchmark_phase_data = benchmark_stats.get(phase_name)

        comparisons, phase_feedback = compare_phase(
            phase_name,
            user_phase_data,
            benchmark_phase_data,
            rules,
        )

        if phase_feedback:
            all_feedback.extend([f"[{PHASE_LABELS.get(phase_name, phase_name)}] {msg}" for msg in phase_feedback])

        comparison_result["phase_analysis"][phase_name] = {
            "phase_label": PHASE_LABELS.get(phase_name, phase_name),
            "metrics": comparisons,
            "feedback": pick_top_feedback(phase_feedback, max_items=3),
        }

    comparison_result["summary_feedback"] = pick_top_feedback(all_feedback, max_items=10)

    output_json = os.path.join(output_dir, "swing_vs_pro_feedback.json")
    with open(output_json, "w") as f:
        json.dump(comparison_result, f, indent=2)

    output_txt = os.path.join(output_dir, "swing_vs_pro_feedback.txt")
    with open(output_txt, "w") as f:
        f.write(f"User swing vs {benchmark_type} pro benchmark\n")
        f.write("=" * 70 + "\n\n")

        for phase_name, phase_data in comparison_result["phase_analysis"].items():
            f.write(f"{phase_data['phase_label']}\n")
            f.write("-" * 70 + "\n")

            if not phase_data["metrics"]:
                f.write("No metric data available for this phase.\n\n")
                continue

            for metric, details in phase_data["metrics"].items():
                f.write(
                    f"{METRIC_LABELS.get(metric, metric)}: "
                    f"user={details['user']}°, "
                    f"pro={details['pro_mean']}° ± {details['pro_std']}°, "
                    f"status={details['status']}\n"
                )

            if phase_data["feedback"]:
                f.write("Coaching feedback:\n")
                for item in phase_data["feedback"]:
                    f.write(f"- {item}\n")

            f.write("\n")

        if comparison_result["summary_feedback"]:
            f.write("Top actionable priorities\n")
            f.write("-" * 70 + "\n")
            for item in comparison_result["summary_feedback"]:
                f.write(f"- {item}\n")

    print(f"Comparison JSON saved to: {output_json}")
    print(f"Comparison report saved to: {output_txt}")

    print("\nTop actionable priorities:")
    for item in comparison_result["summary_feedback"][:5]:
        print(f"- {item}")

    return comparison_result


if __name__ == "__main__":
    compare_user_swing(
        user_video_path="sample_videos/swing.mp4",
        stats_path="swing_angles_data/swing_statistics.json",
        benchmark_type="all",
        output_dir="swing_angles_data",
    )
