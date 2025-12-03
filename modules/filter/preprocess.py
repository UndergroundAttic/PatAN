import re
from typing import Literal, Union
from konlpy.tag import Okt, Hannanum, Komoran
import pandas as pd
import numpy as np

from modules.utils import elapsed


STOP_TAGS = {
    "Number",
    "Josa",
    "Verb",
    "JKS",
    "JKC",
    "JKO",
    "JKB",
    "JKV",
    "JKQ",
    "JX",
    "JC",
    "SN",
    "SF",
    "SP",
    "SS",
    "SE",
    "SO",
}


def preprocess_text(
    text, tagger_instance: Union[Okt, Hannanum, Komoran], join: bool = True
) -> list[str]:
    """
    전처리 함수: 텍스트를 입력받아 명사 추출 및 필터링을 수행합니다.
    """
    from .stopword import PATENT_STOPWORDS

    text = re.sub(r"\([^)]*\)", "", str(text))

    # 특수문자 제거
    text = re.sub(r"[^\w\s]", " ", text)

    # 명사 추출
    if isinstance(tagger_instance, Okt):
        tagged = tagger_instance.pos(text, stem=True)
    else:
        tagged = tagger_instance.pos(text)

    # 필터링: 한 글자 단어 제거, 불용어 제거, 숫자만 있는 단어 제거, 순수 영문자 제거

    taggedset = set(tagged)

    def _helper(item):
        try:
            taggedset.remove(item)
        except:
            return False
        return True

    unique_filtered_words = [
        item
        for item in [
            "/".join((word, tag))
            for word, tag in tagged
            if (tag not in STOP_TAGS)
            and (word not in PATENT_STOPWORDS)
            and len(word) > 1
        ]
        if _helper(item)
    ]
    # TODO: 조사 제거, 일정 숫자마다 프린트

    return unique_filtered_words if not join else " ".join(unique_filtered_words)


@elapsed
def preprocess_df(
    df: pd.DataFrame,
    tagger_type: Literal["Hannanum", "Komoran", "Okt"] = "Hannanum",
    title_weight: int | float = 3,
    abstract_weight: int | float = 1,
) -> pd.DataFrame:
    title_weight = int(title_weight)
    abstract_weight = int(abstract_weight)

    match tagger_type.upper():
        case "HANNANUM":
            tagger_instance = Hannanum()
        case "KOMORAN":
            tagger_instance = Komoran()
        case "OKT":
            tagger_instance = Okt()
        case _:
            raise ValueError(
                "Invalid tagger type. Choose from 'Hannanum', 'Komoran', 'Okt'."
            )

    def _wrap(*args):
        t, a, tw, aw = args
        return " ".join(
            aw * preprocess_text(a, tagger_instance),
            tw * preprocess_text(t, tagger_instance),
        )

    df["processed_text"] = [
        _wrap(title, abstract, title_weight, abstract_weight)
        for title, abstract in zip(df["title"], df["abstract"])
    ]

    return df


def dummy_df():
    return pd.DataFrame([1, 2, 3, 4])


def break_text(text: str) -> list[str]:
    """
    문장을 입력받아 단어 리스트로 반환합니다.
    """
    hannanum = Hannanum()
    okt = Okt()
    komoran = Komoran()
    # 명사 추출
    tagged = (
        hannanum.pos(text, ntags=22, flatten=True)
        + okt.pos(text, stem=True)
        + komoran.pos(text)
    )
    arrayed_pos = np.array(okt.pos(text, stem=True))
    mask = (arrayed_pos[0] not in PATENT_STOPWORDS) & (arrayed_pos[1] not in STOP_TAGS)
    print(mask)
    print(arrayed_pos[mask])

    words = [f"{word}/{tag}" for word, tag in tagged]
    return words


if __name__ == "__main__":
    from stopword import PATENT_STOPWORDS

    sample_text = "아버지가 방에 들어가셨다"
    print(break_text(sample_text))

    word = "발명"
    print(word in PATENT_STOPWORDS)
