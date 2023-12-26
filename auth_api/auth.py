import os
from asyncio import run

from octodiary.asyncApi.myschool import AsyncMobileAPI, AsyncWebAPI
from octodiary.types.captcha import Captcha


async def handle_captcha(captcha: Captcha, api: AsyncWebAPI | AsyncMobileAPI):
    if captcha.question:
        answer = input(captcha.question + ": ")
        response = await captcha.async_asnwer_captcha(answer)
        if isinstance(response, bool):  # Требуется MFA код
            code_mfa = int(input("MFA Code: ").strip())  # запрашиваем у пользователя код (SMS/TOTP)
            return await api.esia_enter_mfa(code=code_mfa)
        else:
            return response
    else:
        with open("captcha.png", "wb") as image:
            image.write(captcha.image_bytes)

        answer = input("Решите капчу из файла captcha.png: ")
        response = await captcha.async_verify_captcha(answer)
        os.remove("captcha.png")
        if isinstance(response, bool):  # Требуется MFA код
            code_mfa = int(input("MFA Code: ").strip())  # запрашиваем у пользователя код (SMS/TOTP)
            return await api.esia_enter_mfa(code=code_mfa)
        else:
            return response


async def login_gosuslugi(
        login: str,
        password: str,
        api: AsyncWebAPI = AsyncWebAPI()
):
    response: bool | Captcha = await api.esia_login(login, password)
    if isinstance(response, bool):  # Требуется MFA код

        code_mfa = int(input("MFA Code: ").strip())  # запрашиваем у пользователя код (SMS/TOTP)
        response2 = await api.esia_enter_mfa(code=code_mfa)
        TOKEN = response2 if isinstance(response2, str) else await handle_captcha(response2)
    elif isinstance(response, Captcha):  # Капча
        TOKEN = await handle_captcha(response, api)

    api.token = TOKEN  # сохраняем токен
    return TOKEN


async def web_api():
    """
    API методы и запросы, которые делают web-сайты myschool.mosreg.ru и authedu.mosreg.ru
    """

    api = AsyncWebAPI()

    # получение и сохранение токена по логину и паролю от госуслуг
    await login_gosuslugi(api, "test", "test")

    # получить информацию о сессии и пользователе
    session_info = await api.get_session_info()
    print(session_info)


async def main():
    await web_api()


if __name__ == "__main__":
    run(main())
