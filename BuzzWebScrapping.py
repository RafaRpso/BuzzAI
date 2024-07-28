from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import google.generativeai as genai
import time 
import json


#TODO:Alterar essa classe, criar um arquivo para configuração de IA (default prompt, qual ia será, etc. Deixar mais abstrato)
class Prompt :
    @staticmethod 
    def get_prompt() -> str : 
        return "Responda de modo adequado, tendo em vista nosso contexto de negócio que é o atendimento ao cliente para redes sociais, não seja excessivamente carismático, tente resolver o problema. Para resposta das dúvidas"
            
            
class BuzzWebScrapping: 
#REQUISITOS PARA UM CÓDIGO COMPLETO E FUNCIONAL 
#TODO: Classe para AI (pode ser open ai, claud, gemini, etc.)
#TODO: Destrinchar isso em classes para outras funções: Como por exemplo "Coletar perguntas", "Análise de dados", etc.
#TODO: Deixar em uma interface intuitiva e, se possível, colocar junto notificações para o usuário
#TODO: Melhorar a estrutura do código e deixar intuitivo a "chave de API" do GEMINI + sua conta do Buzzmonitor

    def __init__(self) -> None:
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service)

        self.DEFAULT_ALL_RESPONSES=False 
        self.DEFAULT_PROMPT = Prompt.get_prompt()

        with open("./data/gemini.json") as file:
            gkey = json.load(file)['googlekey']  
        genai.configure(api_key=gkey)


    def get_credentials(self) -> (str): 
        with open("./data/buzz_monitor.json", 'r') as cdata : 
            ncdata=json.load(cdata)
            user=ncdata["email"]
            password=ncdata["password"]
            return user, password 
        

    #INICIANDO LOGIN PARA FAZER O CAPTCHA
    def login(self) -> None : 

        self.driver.get("https://app.buzzmonitor.com.br/tickets")
        
        if("https://app.buzzmonitor.com.br/tickets" in self.driver.current_url ):
            print("[SUCESS] PULANDO CAPTCHA E LOGIN, INDO PARA TELA DE TICKETS ... ")
            time.sleep(2)
            
            return 
            
        email_input = self.driver.find_element(By.CSS_SELECTOR, "#username")
        pass_input = self.driver.find_element(By.CSS_SELECTOR, "#password")
        email, senha = self.get_credentials() 
        email_input.send_keys(email)
        pass_input.send_keys(senha)
        

        button = self.driver.find_element(By.CSS_SELECTOR, "input.bt")
        button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.user-alert:nth-child(2)"))
        )
        print("[WARNING] RESOLVA O CAPTCHA. ")
        pass_input = self.driver.find_element(By.CSS_SELECTOR, "#password")
        pass_input.send_keys(senha)
        
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".topbar"))
        )
        print("[SUCESS] CAPTCHA BEM SUCEDIDO. ENTRANDO NA PÁGINA INICIAL.")


    def go_to_ticket_page(self) -> None : 
        self.driver.get("https://app.buzzmonitor.com.br/tickets/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ticket-post"))
        )
        print("[SUCESS] ENTRAMOS NA PÁGINA DE TICKET")





    def into_ticket(self) -> list:
        global DEFAULT_ALL_RESPONSES
        
        tickets = self.driver.find_elements(By.CSS_SELECTOR, ".ticket-post-content")
        
        for index, ticket in enumerate(tickets):
            try: 
                print(f"[SUCESS] ACESSANDO O {index + 1}° TICKET")
                ticket.click()
                user_comments =self. get_all_comments()

                    
                print(f"[SUCESS] TODOS OS COMENTÁRIOS FORAM ACESSADOS: {user_comments}")
                print("[WAITING] AGUARDANDO RESPOSTA DA IA")
                response = self.generate_response(user_comments)
                send_response = int(input("Deseja enviar essa resposta? [0/1/2] \n-0=Não enviar\n-1=Enviar\n-2=Enviar todas\n")) if not DEFAULT_ALL_RESPONSES else 1
                
                if send_response == 0:
                    continue
                elif send_response == 2:
                    DEFAULT_ALL_RESPONSES = True
                    
                if DEFAULT_ALL_RESPONSES or send_response == 1:
                    self.send_reply(response)
            except: 
                continue 
        time.sleep(2)
        print(f"Resposta enviada: {send_response}")



    def saving_exception(self)->bool:
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "#loading-screen > div:nth-child(1)"))
            )
            print("[OK] Elemento #loading-screen > div:nth-child(1) não está mais visível")
            print("[SUCESS] RESPOSTA ENVIADA COM SUCESSO")
            return True
        except Exception as e:
            print(f"[ERRO] Ocorreu um erro: {e}")
            return False

    def send_reply(self,response) -> None:

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#send-reply-button"))
            )
            reply_message_field = self.driver.find_element(By.CSS_SELECTOR, "#reply-message")
            send_button = self.driver.find_element(By.CSS_SELECTOR, "#send-reply-button")
            
            reply_message_field.clear()
            reply_message_field.send_keys(response)
            send_button.click()

            #Meio aberração, eu sei. Me lembrou golang 
            try :
            #SweetAlert Exception: Se o alerta aparecer, é necessário confirmar a resposta
                is_sweet_alert =WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sweet-alert"))
                )
                if is_sweet_alert:
                    print("[WAITING] AGUARDANDO CONFIRMAÇÃO DA RESPOSTA")
                    confirm_button = self.driver.find_element(By.CSS_SELECTOR, ".confirm")
                    confirm_button.click()
                    time.sleep(2)
                    
            except Exception as e:
                print(f"[OK] Não houve dupla confirmação")
        
            r = self.saving_exception()
            if r : return 
            
            return None
        except Exception as e:
            print(f"[ERRO] Falha ao enviar a resposta: {e}")

    def get_all_comments(self) -> list : 
        time.sleep(2)
        all_comments = self.driver.find_elements(By.CLASS_NAME, 'container.twitter.fixedIndex')
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
        global DEFAULT_PROMPT
        #TODO: Melhorar lembro
        # PARTE DE PROMPT DO GOOGLE 
        def get_prompt(self) -> str : 
            prompt : str = "Você está em um serviço de atendimento ao cliente, o histórico de conversas desse chat é o seguinte: \n"
            for idx, text in enumerate(conversation_text):
                prompt += str(idx) + "°- "+ text + "\n"
            prompt += DEFAULT_PROMPT
            return prompt 
        
        prompt : str = get_prompt()    
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        print(f"[RESPOSTA] {response.text}")

        return response.text 
        

    def run(self) -> None : 

        self.driver.get("https://app.buzzmonitor.com.br/tickets")
        self.login()
        while True  : # DEUS ME PERDOE, ESSE WHILE TRUE ...   
            self.go_to_ticket_page()
            self.into_ticket()

            time.sleep(10*60) 

if __name__ == '__main__':
    print("Use the file run.py!")