import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# =========================================================
# 0. 기본 설정 (저장 경로 + 폰트)
# =========================================================
OUTPUT_DIR = Path(r"C:\Users\user\Documents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rc("font", family="Malgun Gothic")   # 윈도우: 맑은 고딕
plt.rc("axes", unicode_minus=False)

# 기관별 색상 지정
group_colors = {
    "기업": "orange",      # 오렌지
    "대학": "#1f77b4",     # matplotlib blue
    "연구소": "green",     # 초록
}

# ---------------------------------------------------------
# 1. 덴드로그램 기반 토픽 순서 만들기 (전체 코퍼스 기준)
# ---------------------------------------------------------
# lda_model.components_: (토픽 수 x 단어 수)
dist_matrix = 1 - cosine_similarity(lda_model.components_)   # 거리 = 1 - 코사인유사도
Z = linkage(dist_matrix, method="ward")

# 덴드로그램은 그리지 않고, leaf 순서만 가져오기
dendro = dendrogram(Z, no_plot=True)
ordered_indices = dendro["leaves"]                 # 0부터 시작하는 인덱스
ordered_topics = [i + 1 for i in ordered_indices]  # 사람이 보기 좋은 1~K 번호

print("덴드로그램 기반 토픽 순서:", ordered_topics)

# ---------------------------------------------------------
# 2. 기관 유형(기업/대학/연구소)별 토픽 평균 비중 계산
# ---------------------------------------------------------
group_list = ["기업", "대학", "연구소"]   # df['org_type']에 들어있는 값 기준으로 조정

group_topic_weights = {}

for g in group_list:
    mask = (df["org_type"] == g)

    if not mask.any():
        print(f"⚠ 경고: '{g}' 에 해당하는 문서가 없습니다.")
        group_topic_weights[g] = np.zeros(n_topics)
    else:
        # 선택된 문서들의 토픽 분포 평균 (axis=0 → 토픽 방향 평균)
        group_topic_weights[g] = doc_topic_dist[mask.values, :].mean(axis=0)

# 덴드로그램 순서대로 재정렬
for g in group_list:
    group_topic_weights[g] = group_topic_weights[g][ordered_indices]

# ---------------------------------------------------------
# 3. 레이더 차트 그리기 (기관별 하나씩, 색상 고정)
# ---------------------------------------------------------
num_topics = n_topics

# 각도: 토픽 수만큼 등분
angles = np.linspace(0, 2 * np.pi, num_topics, endpoint=False)
angles = np.concatenate([angles, angles[:1]])  # 폐곡선 만들기 위해 첫 각도 다시 추가

# y축 최대값 (세 기관 중 최대값 기준으로 약간 여유)
max_val = max(w.max() for w in group_topic_weights.values()) * 1.1

fig, axes = plt.subplots(
    1, len(group_list),
    subplot_kw={"polar": True},
    figsize=(6 * len(group_list), 6)
)

if len(group_list) == 1:
    axes = [axes]  # 기관이 1개인 경우에도 리스트로 처리하기 위함

for ax, g in zip(axes, group_list):
    vals = group_topic_weights[g]
    vals = np.concatenate([vals, vals[:1]])   # 폐곡선

    color = group_colors.get(g, "gray")      # 혹시 정의 안된 그룹이면 회색

    # 선과 면에 동일 색상 적용
    ax.plot(angles, vals, linewidth=2, color=color)
    ax.fill(angles, vals, alpha=0.25, color=color)

    # 덴드로그램 순서에 맞춘 토픽 라벨 (T번호)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f"T{t}" for t in ordered_topics], fontsize=9)

    ax.set_ylim(0, max_val)
    ax.set_title(g, fontsize=16, pad=40)

plt.suptitle("기관 유형별 토픽 분포 (덴드로그램 기반 토픽 순서)", fontsize=20, y=1.05)
plt.tight_layout()

# ---------------------------------------------------------
# 4. 저장
# ---------------------------------------------------------
save_path = OUTPUT_DIR / "기관별_topic_radar_dendro_order_colored.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print("=" * 80)
print("✅ 기관별 레이더 차트 시각화 완료! (기업=오렌지, 대학=#1f77b4, 연구소=green)")
print("📂 저장 경로:", save_path)
print("=" * 80)
