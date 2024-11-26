from lib2to3.pgen2 import driver
import data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    phone_number_field = (By.ID, 'phone')
    card_number_field = (By.ID, 'number')
    card_code_field = (By.ID, 'code')
    message_for_driver_field = (By.ID, 'message')
    tarifa_comfort_button = (By.ID, 'comfort')
    manta_button = (By.ID, 'manta')
    panuelos_button = (By.ID, 'panuelos')
    helados_button = (By.ID, 'helados')
    esperar_taxi_field = (By.ID, 'taxi')
    driver.find_element = (By.NAME, "email")
    driver.find_element = (By.CLASS_NAME, "form-input")
    driver.find_element = (By.XPATH, "//input[@type='submit']")

    def __init__(self, driver):
        self.driver = driver

    def find_email_field(self):
            # Usando CSS Selector para localizar el campo de email
        return self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def seleccionar_tarifa_comfort(self):
        comfort = self.driver.find_element(*self.tarifa_comfort_button)
        comfort.click()

    def rellenar_telefono(self, phone):
        phone_number = self.driver.find_element(*self.phone_number_field)
        (phone_number.clear())
        phone_number.send_keys(phone)

    def agregar_tarjeta(self, number, code):
        self.driver.find_element(*self.card_number_field).click()
        self.driver.find_element(*self.card_number_field).send_keys(number)
        self.driver.find_element(*self.card_code_field).send_keys(code)
        self.driver.find_element(*self.card_code_field).send_keys(Keys.TAB)
        self.driver.find_element(*self.card_code_field).send

    def pedir_manta_y_panuelos(self):
        self.driver.find_element(*self.manta_button).click()
        self.driver.find_element(*self.panuelos_button).click()

        WebDriverWait(self.driver, 10)

    def esperar_taxi(self):

        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(self.esperar_taxi()))

    def esperar_informacion_conductor(self):

        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(self.esperar_informacion_conductor()))




# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class TestUrbanRoutes:

    driver = None



    @classmethod
    def setup_class(cls):
      # No modificar, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
       options = Options()
       options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
       cls.driver = webdriver.Chrome(options=options)
       cls.driver.get(data.urban_routes_url)
       cls.routes_page = UrbanRoutesPage(cls.driver)


    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_route(address_from, address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_pedir_taxi_completo(self):
        address_from = 'East 2nd Street, 601'
        self.page.configurar_direccion(address_from)
        assert address_from == self.page.get_direccion_origen(), f"Dirección de origen incorrecta: {address_from}"

        address_to = '1300 1st St'
        self.page.configurar_direccion(address_to)
        assert address_to == self.page.get_direccion_destino(), f"Dirección de destino incorrecta: {address_to}"

        self.page.seleccionar_tarifa_comfort()
        tarifa_comfort_seleccionada = self.page.obtener_tarifa_seleccionada()
        assert tarifa_comfort_seleccionada == "Comfort", "La tarifa seleccionada no es 'Comfort'"

        phone_number = '+1 123 123 12 12'
        self.page.rellenar_telefono(phone_number)
        assert phone_number == self.page.obtener_telefono(), f"El número de teléfono no es correcto: {phone_number}"

        card_number = '1234 5678 9100'
        card_code = '111'
        self.page.agregar_tarjeta(card_number, card_code)
        assert card_number == self.page.obtener_numero_tarjeta(), f"El número de tarjeta no es correcto: {card_number}"

        self.driver.get('https://around-v1.es.practicum-services.com/')
        assert "The card link was not activated" in self.driver.page_source, "El enlace de la tarjeta no se activó correctamente."

        self.page.pedir_manta_y_panuelos()
        assert self.page.is_manta_y_panuelos_pedidos(), "La manta y los pañuelos no fueron solicitados correctamente."

        self.page.pedir_helados()
        assert self.page.is_helados_pedidos(), "Los helados no fueron solicitados correctamente."

        message_for_driver = 'Traiga un aperitivo'
        self.page.message_for_driver(message_for_driver)
        assert message_for_driver == self.page.obtener_mensaje_para_conductor(), "El mensaje para el conductor no es correcto."

        self.page.esperar_modal_buscando_taxi()
        modal_buscando_visible = self.page.is_modal_buscando_taxi_visible()
        assert modal_buscando_visible, "El modal 'Buscando Taxi' no es visible."

        self.page.esperar_informacion_conductor()
        conductor_info_visible = self.driver.find_element(*UrbanRoutesPage.CONDUCTOR_INFO).is_displayed()
        assert conductor_info_visible, "La información del conductor no está visible."

    def tearDown(self):
        self.driver.quit()


    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
