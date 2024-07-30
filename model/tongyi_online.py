import os
from langchain_qianwen import Qwen_v1
import util.constant as CONSTANT

os.environ["DASHSCOPE_API_KEY"] = CONSTANT.DASHSCOPE_API_KEY


def create_model():
    llm = Qwen_v1(
        model_name="qwen-7b-chat",
        # model_name="qwen2-72b-instruct",
        temperature=0
    )
    return llm


if __name__ == "__main__":
    tongyi = create_model()
    pass
