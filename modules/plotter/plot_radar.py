import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def radar_chart(df, output_path=None):
    # 폰트 설정
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    # ---------------------------------------------------------
    # [수정] Topic 1 제거하기
    # ---------------------------------------------------------
    # Topic_ID가 'Topic 1'이 아닌 것만 남깁니다.
    # df = df[df['Topic_ID'] != 'Topic 1']

    # (선택) 인덱스 재설정 (깔끔하게)
    df = df.reset_index(drop=True)
    # ---------------------------------------------------------

    # 데이터 준비
    labels = df["Label"].tolist()
    stats = df["Proportion"].tolist()
    num_vars = len(labels)  # 19개로 줄어듦

    # 2. 각도 계산 (19개에 맞춰서 원을 쪼갭니다)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # 3. 도형 닫기 (시작점과 끝점 연결)
    stats += stats[:1]
    angles += angles[:1]
    # labels는 그대로 둡니다 (축 눈금용)

    # 4. 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # (1) 배경 디자인
    ax.set_theta_offset(np.pi / 2)  # 12시 방향 시작
    ax.set_theta_direction(-1)  # 시계 방향

    # (2) 축 눈금(X축) - 토픽 라벨
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9)

    # 라벨 위치 조정
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        if angle in (0, np.pi):
            label.set_horizontalalignment("center")
        elif 0 < angle < np.pi:
            label.set_horizontalalignment("left")
        else:
            label.set_horizontalalignment("right")

    # (3) Y축(비중) 눈금 설정
    # 최대값에 맞춰 유동적으로 조절
    max_val = max(stats) + 0.01
    ax.set_ylim(0, max_val)
    ax.set_rlabel_position(0)

    # 눈금 표시 (필요에 따라 수치 조정 가능)
    # 예: 0.05, 0.10 지점에 회색선 표시
    plt.yticks([0.05, 0.10], ["5%", "10%"], color="grey", size=8)

    # (4) 데이터 플롯
    ax.plot(angles, stats, color="#1f77b4", linewidth=2, linestyle="solid")
    ax.fill(angles, stats, color="#1f77b4", alpha=0.25)
    ax.scatter(angles, stats, color="#1f77b4", s=50, zorder=10)

    # (5) 타이틀
    plt.title("STM 토픽 비중 구조", size=20, color="black", y=1.08)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Radar chart saved to {output_path}")

    plt.show()
    plt.close(fig)
