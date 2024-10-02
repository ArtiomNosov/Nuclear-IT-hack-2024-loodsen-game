giga_token = API_connection.token(API_connection.auth_key)
chat = GigaChat(credentials=API_connection.auth_key, scope ="GIGACHAT_API_PERS", verify_ssl_certs= False,model="GigaChat-Pro")


def paraphrase(human_message):
    messages.append(HumanMessage(human_message))
    res = chat.invoke(messages)
    messages.append(res)
    print(res.content)
    return res.content

while True:
    hm = input()
    ans = paraphrase(hm)
    print(ans)
