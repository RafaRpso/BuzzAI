from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import google.generativeai as genai
import time 
import json

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
DEFAULT_ALL_RESPONSES=False 
with open("./data/gemini.json") as file:
    gkey = json.load(file)['googlekey']  
genai.configure(api_key=gkey)




def get_credentials() -> (str): 
    with open("./data/buzz_monitor.json", 'r') as cdata : 
        ncdata=json.load(cdata)
        user=ncdata["email"]
        password=ncdata["password"]
        return user, password 
    

def login() -> None : 

    driver.get("https://app.buzzmonitor.com.br/tickets")
    
    if("https://app.buzzmonitor.com.br/tickets" in driver.current_url ):
        print("[SUCESS] PULANDO CAPTCHA E LOGIN, INDO PARA TELA DE TICKETS ... ")
        time.sleep(2)
        
        return 
        
    email_input = driver.find_element(By.CSS_SELECTOR, "#username")
    pass_input = driver.find_element(By.CSS_SELECTOR, "#password")
    email, senha = get_credentials() 
    email_input.send_keys(email)
    pass_input.send_keys(senha)
    

    button = driver.find_element(By.CSS_SELECTOR, "input.bt")
    button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.user-alert:nth-child(2)"))
    )
    print("[WARNING] RESOLVA O CAPTCHA. ")
    pass_input = driver.find_element(By.CSS_SELECTOR, "#password")
    pass_input.send_keys(senha)
    
    WebDriverWait(driver, 120).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".topbar"))
    )
    print("[SUCESS] CAPTCHA BEM SUCEDIDO. ENTRANDO NA PÁGINA INICIAL.")


def go_to_ticket_page() -> None : 
    driver.get("https://app.buzzmonitor.com.br/tickets/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ticket-post"))
    )
    print("[SUCESS] ENTRAMOS NA PÁGINA DE TICKET")





def into_ticket() -> list:
    global DEFAULT_ALL_RESPONSES
    
    tickets = driver.find_elements(By.CSS_SELECTOR, ".ticket-post-content")
    
    for index, ticket in enumerate(tickets):
        try: 
            print(f"[SUCESS] ACESSANDO O {index + 1}° TICKET")
            ticket.click()
            user_comments = get_all_comments()

                
            print(f"[SUCESS] TODOS OS COMENTÁRIOS FORAM ACESSADOS: {user_comments}")
            print("[WAITING] AGUARDANDO RESPOSTA DA IA")
            response = generate_response(user_comments)
            send_response = int(input("Deseja enviar essa resposta? [0/1/2] \n-0=Não enviar\n-1=Enviar\n-2=Enviar todas\n")) if not DEFAULT_ALL_RESPONSES else 1
            
            if send_response == 0:
                continue
            elif send_response == 2:
                DEFAULT_ALL_RESPONSES = True

            if DEFAULT_ALL_RESPONSES or send_response == 1:
                send_reply(response)
        except: 
            continue 
    time.sleep(2)
    print(f"Resposta enviada: {send_response}")



def saving_exception()->bool:
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#loading-screen > div:nth-child(1)"))
        )
        print("[OK] Elemento #loading-screen > div:nth-child(1) não está mais visível")
        print("[SUCESS] RESPOSTA ENVIADA COM SUCESSO")
        return True
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")
        return False

def send_reply(response) -> None:

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#send-reply-button"))
        )
        reply_message_field = driver.find_element(By.CSS_SELECTOR, "#reply-message")
        send_button = driver.find_element(By.CSS_SELECTOR, "#send-reply-button")
        
        reply_message_field.clear()
        reply_message_field.send_keys(response)
        send_button.click()

        #Meio aberração, eu sei. Me lembrou golang 
        try :
         #SweetAlert Exception: Se o alerta aparecer, é necessário confirmar a resposta
            is_sweet_alert =WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sweet-alert"))
            )
            if is_sweet_alert:
                print("[WAITING] AGUARDANDO CONFIRMAÇÃO DA RESPOSTA")
                confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm")
                confirm_button.click()
                time.sleep(2)
                
        except Exception as e:
            print(f"[OK] Não houve dupla confirmação")
       
        r = saving_exception()
        if r : return 
        
        return None
    except Exception as e:
        print(f"[ERRO] Falha ao enviar a resposta: {e}")

def get_all_comments() -> list : 
    time.sleep(2)
    all_comments = driver.find_elements(By.CLASS_NAME, 'container.twitter.fixedIndex')
    user_comments = []
    print("[SUCESS] ACESSANDO TODOS OS COMENTÁRIOS DO TICKET")

    for comment in all_comments:
        try:
            reply_link = comment.find_element(By.TAG_NAME, 'p')
            print("reply: ", reply_link.text) 
            user_comments.append(reply_link.text)
        except Exception as e:
            print(f"[ERRO] Falha ao acessar comentário: {e}")
            pass
        
    return user_comments


def generate_response(conversation_text) -> str:
    def get_prompt() -> str : 
        prompt : str = "Você está em um serviço de atendimento ao cliente, o histórico de conversas desse chat é o seguinte: \n"
        for idx, text in enumerate(conversation_text):
            prompt += str(idx) + "°- "+ text + "\n"
        prompt += "Responda de modo adequado, tendo em vista nosso contexto de negócio que é o atendimento ao cliente para redes sociais, não seja excessivamente carismático, tente resolver o problema."
        return prompt 
    
    prompt : str = get_prompt()    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    print(f"[RESPOSTA] {response.text}")

    return response.text 
        



def main() -> None : 

    driver.get("https://app.buzzmonitor.com.br/tickets")
    login()
    while True  : # DEUS ME PERDOE, ESSE WHILE TRUE ...   
        go_to_ticket_page()
        into_ticket()

        time.sleep(10*60) 


if __name__ == '__main__': 
    main() 
