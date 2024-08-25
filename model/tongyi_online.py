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
    # For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
    from http import HTTPStatus
    import dashscope


    def sample_sync_call():
        prompt_text = '用萝卜、土豆、茄子做饭，给我个菜谱。'
        resp = tongyi
        # The response status_code is HTTPStatus.OK indicate success,
        # otherwise indicate request is failed, you can get error code
        # and message from code and message.
        if resp.status_code == HTTPStatus.OK:
            print(resp.output)  # The output text
            print(resp.usage)  # The usage information
        else:
            print(resp.code)  # The error code.
            print(resp.message)  # The error message.


    sample_sync_call()

    pass
