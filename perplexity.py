import requests
from pydantic import BaseModel

from typing import List

class AnswerFormat(BaseModel):
    clothing_name1: str
    price1: int
    sustainibility_score1: int
    purchase_link1: str
    clothing_name2: str
    price2: int
    sustainibility_score2: int
    purchase_link2: str
    clothing_name3: str
    price3: int
    sustainibility_score3: int
    purchase_link3: str


def perplexity(x):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": "Bearer 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"}
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "you will be given a very detailed description of a clothing search for similar pieces of clothing and respond in the json schema provided by user, sustainibility score will be given by how sustainible the materials of clothes are or how ethically the brand sources clothes are( give a integer value betwenn 1 and 100) all fields given are rquired, also image link will be the link to the image of the clothing, purchase link will be to buy the similar clothing options. if the brand you find is famous for being expensive or high quality they are likely to have a high sustainibility score"},
            {"role": "user", "content": (
                f"{x}"
                "Please output a JSON object containing the following fields: "
                "clothing_name, price, sustainibility_score, purchase_link "
            )},
        ],
        "response_format": {
        "type": "json_schema",
        "json_schema": {"schema": AnswerFormat.model_json_schema()},
    },
    }
    response = requests.post(url, headers=headers, json=payload).json()
    response_data = response["choices"][0]["message"]["content"]
    return response_data