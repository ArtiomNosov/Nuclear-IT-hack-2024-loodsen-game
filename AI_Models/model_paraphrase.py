import API_connection
import gigachat
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models.gigachat import GigaChat

giga_token = API_connection.token(API_connection.auth_key)
chat = GigaChat(credentials=API_connection.auth_key, scope ="GIGACHAT_API_PERS", verify_ssl_certs= False,model="GigaChat-Pro")
with open('model_paraphrase/task.txt') as file:
    content = file.read()
messages = [SystemMessage(content = content)]
with open('model_paraphrase/promt_paraphrase.txt') as file:
    prompt = file.read()
def paraphrase(human_message):
    messages.append(HumanMessage(human_message))
    res = chat.invoke(messages)
    messages.append(res)
    print(res.content)
    return res.content

hm = prompt
ans = paraphrase(hm)
with open('ans_paraphrase.txt',"w") as file:
    file.write(ans)
