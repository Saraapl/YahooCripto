from dataclasses import dataclass
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
from urllib.request import urlopen
import requests


@dataclass
class Criptomoneda:
  simbolo: str
  nombre: str
  precio: float
  cambio: float
  porcentaje_cambio: float
  market_cap: str


class Extractor:

  @staticmethod
  def extraer_criptos(n: int = 25) -> list[Criptomoneda]:
    r = requests.get('https://finance.yahoo.com/crypto')
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.table
    if table is None:
      print("No se ha encontrado la tabla de criptomonedas")
      return []

    def extract_symbol(cell):
      return cell.find('a').text

    def extract_name(cell):
      return cell.text

    def extract_price(cell):
      return float(cell.text.replace(',', ''))

    def extract_change(cell):
      return float(cell.text)

    def extract_percent_change(cell):
      return float(cell.text[:-1])

    def extract_market_cap(cell):
      return cell.text

    criptos = []
    for row in table.find_all('tr')[1:n + 1]:
      cells = row.find_all('td')
      cells = cells[0:6]
      symbol = extract_symbol(cells[0])
      name = extract_name(cells[1])
      price = extract_price(cells[2])
      change = extract_change(cells[3])
      percent_change = extract_percent_change(cells[4])
      market_cap = extract_market_cap(cells[5])
      criptos.append(
        Criptomoneda(symbol, name, price, change, percent_change, market_cap))

    return criptos

  @staticmethod
  def extraer_uno(url):
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    objeto = BeautifulSoup(req.text, "html.parser")
    precio = objeto.find("fin-streamer",
                         {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    nombre = objeto.find("h1", {"class": "D(ib) Fz(18px)"})
    cambio = objeto.find("fin-streamer",
                         {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    tasa_de_cambio = objeto.find("fin-streamer",
                                 {"class": "Fw(500) Pstart(8px) Fz(24px)"})
    nombre = nombre.get_text()
    precio = float(precio.get_text())
    cambio = float(cambio.get_text())
    tasa_de_cambio = float(tasa_de_cambio.get_text())
    url = urllib.parse.urlparse(url)
    simbolo = url.path.split('/')[-1]
    return Criptomoneda(simbolo, nombre, precio, cambio, tasa_de_cambio, "N/A")



class Controlador:
  db: list[Criptomoneda]

  def __init__(self):
    self.db = []

  def actualizar_criptos(self):
    print("Actualizando base de datos de criptomonedas...")
    self.db = Extractor.extraer_criptos()

  def visualizar_criptos(self, criptos: list[Criptomoneda]):
    for i, cripto in enumerate(criptos):
      print(f"{i + 1}. {cripto}")

  def visualizar_mejores_por_precio(self):
    n = int(input("Introduce el número de criptomonedas a visualizar: "))
    criptos = self.db.copy()
    criptos.sort(key=lambda x: x.precio)
    criptos = criptos[:n]
    self.visualizar_criptos(criptos)

  def visualizar_mejores_por_cambio(self):
    n = int(input("Introduce el número de criptomonedas a visualizar: "))
    criptos = self.db.copy()
    criptos.sort(key=lambda x: x.porcentaje_cambio, reverse=True)
    criptos = criptos[:n]
    self.visualizar_criptos(criptos)

  def visualizar_todas(self):
    criptos = self.db.copy()
    self.visualizar_criptos(criptos)

  def buscar_cripto(self):
    print("¿Cuál cripto quiere consultar?")
    nombre = input()
    criptos = self.db.copy()
    for crypto in criptos:
      if crypto.nombre == nombre:
        print(crypto)

  def las_mas_caras(self):
    n = int(input("Introduce el número de criptomonedas a visualizar: "))
    criptos = self.db.copy()
    criptos.sort(key=lambda x: x.cambio)
    criptos = criptos[:n]
    self.visualizar_criptos(criptos)

  def agregar_cripto(self):
    url = input("Introduce la url de la criptomoneda: ")
    url_parsed = urllib.parse.urlparse(url)
    #procesa
    simbolo = url_parsed.path.split('/')[-1]
    for cripto in self.db:
      if cripto.simbolo == simbolo:
        print("La criptomoneda ya existe en la base de datos")
        return
    cripto = Extractor.extraer_uno(url)
    self.db.append(cripto)
    print("Criptomoneda agregada con éxito")

  def monto(self, urls, monto):
    las_que_agregue = []
    for i in range(len(urls)):
      cripto1 = Extractor.extraer_uno(urls[i])
      guardar = True
      las_que_agregue.append(cripto1)
      for cripto in self.db:
        if cripto.simbolo == cripto1.simbolo:
          print("No se puede agregar, ya existe la criptomoneda")
          guardar = False
      if guardar == True:
        self.db.append(cripto1)
    for cripto in las_que_agregue:
      print(f"Con {monto} puedes comprar {monto/cripto.precio} {cripto.nombre}")

class Menu:
  controlador: Controlador

  def __init__(self):
    self.controlador = Controlador()
    self.controlador.actualizar_criptos()

  def mostrar_menu(self):
    print("Bienvenido, las opciones son:")
    print("1. Visualizar todas las criptomonedas")
    print("2. Visualizar las n mejores criptomonedas por menor precio")
    print("3. Visualizar las n mejores criptomonedas por mayor % cambio")
    print("4. Visualizar una cripto de su preferencia")
    print("5. Visualizar las más caras por tasa de cambio")
    print("6. Actualizar criptomonedas")
    print("7. Agregar criptomoneda desde url")
    print("8. Salir")
    print("9. Ver monto")
    opcion = int(input("Introduce una opción: "))

    if opcion == 1:
      self.controlador.visualizar_todas()
    elif opcion == 2:
      self.controlador.visualizar_mejores_por_precio()
    elif opcion == 3:
      self.controlador.visualizar_mejores_por_cambio()
    elif opcion == 4:
      self.controlador.buscar_cripto()
    elif opcion == 5:
      self.controlador.las_mas_caras()
    elif opcion == 6:
      self.controlador.actualizar_criptos()
    elif opcion == 7:
      self.controlador.agregar_cripto()
    elif opcion == 8:
      print("Adios")
      exit()
    elif opcion == 9:
      self.controlador.monto(["https://finance.yahoo.com/quote/HEX-USD", "https://finance.yahoo.com/quote/FIL-USD"], 100)
    else:
      print("Opción no válida")

  def run(self):
    while True:
      self.mostrar_menu()


if __name__ == '__main__':
  menu = Menu()
  menu.run()

Menu()
