from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def radar_chart(df, output_path=None, group_column="orgType", max_groups=4):
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    if df is None or len(df) == 0:
        print("No data provided for radar chart.")
        return

    df = df.copy().reset_index(drop=True)
    group_col = group_column if group_column and group_column in df.columns else None

    groups = []
    if group_col:
        for value in df[group_col].tolist():
            if value in (None, "") or pd.isna(value):
                continue
            if value not in groups:
                groups.append(value)

    fallback_col = "__group__"
    if not groups:
        df[fallback_col] = "Overall"
        group_col = fallback_col
        groups = ["Overall"]

    if len(groups) > max_groups:
        print(
            f"More than {max_groups} org types detected; keeping the first {max_groups}: {groups[:max_groups]}"
        )
        groups = groups[:max_groups]

    global_max = df["Proportion"].max()
    if pd.isna(global_max) or global_max == 0:
        global_max = 0.1
    global_max *= 1.1

    group_colors = {
        "individual": "#BBBBBB",
        "firm": "#ff8c00",
        "univ": "#1f77b4",
        "research": "#2ca02c",
    }
    group_to_str = {
        "individual": "개인",
        "firm": "기업",
        "univ": "대학",
        "research": "연구소",
        "Overall": "전체",
    }

    color_cycle = plt.rcParams.get("axes.prop_cycle", None)
    fallback_colors = color_cycle.by_key()["color"] if color_cycle else ["#999999"]

    n_panels = len(groups)
    fig, axes = plt.subplots(
        1,
        n_panels,
        figsize=(6 * len(groups), 6),
        subplot_kw=dict(polar=True),
    )
    if n_panels == 1:
        axes = [axes]

    for idx, (ax, group) in enumerate(zip(axes, groups)):
        subset = df[df[group_col] == group].reset_index(drop=True)
        color = group_colors.get(group, fallback_colors[idx % len(fallback_colors)])
        _plot_radar(
            ax,
            subset,
            title=group_to_str[str(group)],
            color=color,
            max_radius=global_max,
        )

    for ax in axes[len(groups) :]:
        ax.set_axis_off()

    fig.suptitle("기관 유형별 토픽 분포", fontsize=20, y=1.05)
    plt.tight_layout()
    # fig.subplots_adjust(wspace=0.2)
    # plt.subplots_adjust(top=0.85)

    resolved_path = _resolve_output_path(output_path)
    if resolved_path:
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(resolved_path, dpi=300, bbox_inches="tight")
        print(f"Radar chart saved to {resolved_path}")

    plt.show()
    plt.close(fig)


def _plot_radar(ax, df: pd.DataFrame, title: str, color: str, max_radius: float):
    if df is None or len(df) == 0:
        ax.set_axis_off()
        ax.set_title(f"{title} (no data)")
        return

    labels = df["Label"].tolist()
    stats = df["Proportion"].tolist()
    num_vars = len(labels)
    if num_vars == 0:
        ax.set_axis_off()
        ax.set_title(f"{title} (no topics)")
        return

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    stats_cycle = stats + stats[:1]
    angles_cycle = angles + angles[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=8)

    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment("center")
        elif 0 < angle < np.pi:
            label.set_horizontalalignment("left")
        else:
            label.set_horizontalalignment("right")

    upper = max_radius
    ax.set_ylim(0, upper)
    ax.set_rlabel_position(0)
    tick_vals = np.linspace(0, upper, 4)[1:]
    ax.set_yticks(tick_vals)
    ax.set_yticklabels([f"{val:.2f}" for val in tick_vals], fontsize=8)

    ax.plot(angles_cycle, stats_cycle, color=color, linewidth=2)
    ax.fill(angles_cycle, stats_cycle, color=color, alpha=0.25)
    ax.scatter(angles_cycle, stats_cycle, color=color, s=30, zorder=10)
    ax.grid(True, color="#bfbfbf", alpha=0.4)
    ax.set_title(title, size=16, pad=20)


def _resolve_output_path(output_path):
    if not output_path:
        return None
    path = Path(output_path)
    if path.suffix:
        return path
    path.mkdir(parents=True, exist_ok=True)
    return path / "topic_radar_chart.png"
