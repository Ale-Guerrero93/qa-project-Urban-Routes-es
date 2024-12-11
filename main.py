import data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    comfort_rate_button = (By.ID, 'comfort')
    blanket_button = (By.ID, 'blanket')
    handkerchiefs_button = (By.ID, 'handkerchiefs')
    ice_creams_button = (By.ID, 'ice_creams')
    taxi_button = (By.ID, 'taxi')
    driver_info = (By.ID, 'driver_info')
    model_looking_for_taxi_locator = (By.ID, 'model_taxi_searching')

    def __init__(self, driver):
            self.driver = driver

    def find_email_field(self):
        return self.driver.find_element(By.NAME, "email")

    def find_form_input(self):
        return self.driver.find_element(By.CLASS_NAME, "form-input")

    def submit_form(self):
        return self.driver.find_element(By.XPATH, "//input[@type='submit']").click()

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from_address(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to_address(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)
        self.click_taxi_button()

    def click_taxi_button(self):
        self.driver.find_element(*self.taxi_button).click()

    def get_selected_rate(self):
        selected_rate = self.driver.find_element(*self.comfort_rate_button)
        return 'selected' in selected_rate.get_attribute('class')

    def select_comfort_rate(self):
        self.driver.find_element(*self.comfort_rate_button).click()

    def get_phone_number(self):
        return self.driver.find_element(*self.phone_number_field).get_property('value')

    def fill_phone_number(self, phone_number):
        phone_number_field = self.driver.find_element(*self.phone_number_field)
        phone_number_field.clear()
        phone_number_field.send_keys(phone_number)

    def get_card_number(self):
        return self.driver.find_element(*self.card_number_field).get_property('value')

    def add_card(self, number, code):
        card_number_field = self.driver.find_element(*self.card_number_field)
        card_number_field.click()
        card_number_field.send_keys(number)

        card_code_field = self.driver.find_element(*self.card_code_field)
        card_code_field.send_keys(code)

    def is_blanket_and_handkerchiefs_ordered(self):
        blanket_class = self.driver.find_element(*self.blanket_button).get_attribute('class')
        handkerchiefs_class = self.driver.find_element(*self.handkerchiefs_button).get_attribute('class')
        return 'selected' in blanket_class and 'selected' in handkerchiefs_class

    def ask_for_a_blanket_and_handkerchiefs(self):
        self.driver.find_element(*self.blanket_button).click()
        self.driver.find_element(*self.handkerchiefs_button).click()

    def order_ice_cream(self):
        self.driver.find_element(*self.ice_creams_button).click()

    def is_ice_cream_orders(self):
        return 'selected' in self.driver.find_element(*self.ice_creams_button).get_attribute('class')

    def get_message_for_driver(self):
        return self.driver.find_element(*self.message_for_driver_field).get_property('value')

    def message_for_driver(self, message):
        field = self.driver.find_element(*self.message_for_driver_field)
        field.clear()
        field.send_keys(message)
    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def set_message_for_driver(self, message):
        self.driver.find_element(*self.message_for_driver_field).send_keys(message)

        WebDriverWait(self.driver, 10)

    def wait_for_taxi(self):
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(self.taxi_button))

    def wait_model_looking_for_taxi(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.model_looking_for_taxi_locator)
        )

    def is_model_looking_for_taxi_visible(self):
        return self.driver.find_element(*self.model_looking_for_taxi_locator).is_displayed()

    def wait_for_driver_information(self):
        driver_info_locator = (By.ID, 'driver_info')  # Cambia según tu HTML
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(driver_info_locator))


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
            raise Exception(
                "No se encontró el código de confirmación del teléfono. "
                "Asegúrate de haber solicitado el código antes de ejecutar este método.")
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
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        assert self.routes_page.get_from_address() == data.address_from
        assert self.routes_page.get_to_address() == data.address_to

    def test_select_plan(self):
        address_from = 'East 2nd Street, 601'
        self.routes_page.set_from(address_from)
        assert address_from == self.routes_page.get_from_address(), f"Dirección de origen incorrecta: {address_from}"

        address_to = '1300 1st St'
        self.routes_page.set_to(address_to)
        assert address_to == self.routes_page.get_to_address(), f"Dirección de destino incorrecta: {address_to}"

    def test_fill_phone_number(self):
        phone_number = '+1 123 123 12 12'
        self.routes_page.fill_phone_number(phone_number)
        assert phone_number == self.routes_page.get_phone_number(), f"El número de teléfono no es correcto: {phone_number}"

    def test_fill_card(self):
        card_number = '1234 5678 9100'
        card_code = '111'
        self.routes_page.add_card(card_number, card_code)
        assert card_number == self.routes_page.get_card_number(), f"El número de tarjeta no es correcto: {card_number}"

        assert "The card link was not activated" in self.driver.page_source, "El enlace de la tarjeta no se activó correctamente."

    def test_order_blanket_and_handkerchiefs(self):
        self.routes_page.ask_for_a_blanket_and_handkerchiefs()
        assert self.routes_page.is_blanket_and_handkerchiefs_ordered(), "La manta y los pañuelos no fueron solicitados correctamente."

    def test_order_2_ice_creams(self):
        self.routes_page.order_ice_cream()
        assert self.routes_page.is_ice_cream_orders(), "Los helados no fueron solicitados correctamente."

    def test_comment_for_driver(self):
        message_for_driver = 'Traer un aperitivo'
        self.routes_page.message_for_driver(message_for_driver)
        assert message_for_driver == self.routes_page.get_message_for_driver(), "El mensaje para el conductor no es correcto."

    def test_car_search_model_appears(self):
        self.routes_page.wait_model_looking_for_taxi()
        model_searching_visible = self.routes_page.is_model_looking_for_taxi_visible()
        assert model_searching_visible, "El modal 'Buscando Taxi' no es visible."

    def test_driver_info_appears(self):
        self.routes_page.wait_for_driver_information()
        driver_info_visible = self.driver.find_element(*UrbanRoutesPage.DRIVER_INFO).is_displayed()

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    @classmethod
    def teardown_class(cls):
        if cls.driver:
            cls.driver.quit()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
