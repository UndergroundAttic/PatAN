import re
from typing import Literal
from konlpy.tag import Okt, Hannanum, Komoran
from konlpy.tag import Hannanum
import pandas as pd
from .stopword import PATENT_STOPWORDS

STOP_TAGS = {
    "Number",
    "Josa",
}


def preprocess_text(text, tagger: Literal["Hannanum", "Komoran", "Okt"]) -> list[str]:
    """
    전처리 함수: 텍스트를 입력받아 명사 추출 및 필터링을 수행합니다.
    """
    text = re.sub(r"\([^)]*\)", "", str(text))

    # 특수문자 제거
    text = re.sub(r"[^\w\s]", " ", text)

    # 명사 추출
    match tagger:
        case "Hannanum":
            tagger_instance = Hannanum()
            tagged = tagger_instance.pos(text, ntags=9, flatten=True)
        case "Komoran":
            tagger_instance = Komoran()
            tagged = tagger_instance.pos(text)
        case "Okt":
            tagger_instance = Okt()
            tagged = tagger_instance.pos(text, stem=True)
        case _:
            raise ValueError("Unsupported tagger type")

    # 필터링: 한 글자 단어 제거, 불용어 제거, 숫자만 있는 단어 제거, 순수 영문자 제거
    filtered_tagged_words = [
        f"{word}/{tag}"
        for word, tag in tagged
        if len(word) > 1 and (word not in PATENT_STOPWORDS) and (tag not in STOP_TAGS)
    ]

    # TODO: 조사 제거, 일정 숫자마다 프린트

    return unique_list(filtered_tagged_words)


def unique_list(seq):
    seen = set()
    unique_seq = []
    i = 0
    for item in seq:
        if item not in seen:
            seen.add(item)
            unique_seq.append(item)

            i += 1
            if i % 1000 == 0:
                print(f"Processed {i} unique items...")
    return unique_seq


def preprocess_df(
    df: pd.DataFrame,
    tagger_type: Literal["Hannanum", "Komoran", "Okt"] = "Hannanum",
    title_weight: int | float = 3,
    abstract_weight: int | float = 1,
) -> pd.DataFrame:
    title_weight = int(title_weight)
    abstract_weight = int(abstract_weight)

    def _wrap(*args):
        t, a, tw, aw = args
        return " ".join(
            aw * preprocess_text(a, tagger_type) + tw * preprocess_text(t, tagger_type)
        )

    df["processed_text"] = df.apply(
        lambda row: _wrap(row["title"], row["abstract"], title_weight, abstract_weight),
        axis=1,
    )

    return df


def dummy_df():
    return pd.DataFrame([1, 2, 3, 4])


def break_text(text: str) -> list[str]:
    """
    문장을 입력받아 단어 리스트로 반환합니다.
    """
    hannanum = Hannanum()
    # 명사 추출
    tagged = hannanum.pos(text, ntags=9, flatten=True)

    words = [f"{word}/{tag}" for word, tag in tagged]
    return words


if __name__ == "__main__":
    from stopword import PATENT_STOPWORDS

    sample_text = "아버지가방에들어가셨다"
    print(break_text(sample_text))

    word = "발명"
    print(word in PATENT_STOPWORDS)
