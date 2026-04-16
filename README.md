Dashboard de Detección de Fraude

Dashboard analítico interactivo sobre transacciones de pago de la Unión Europea.

Disponible online en: [paymenttransactionseudashpy.onrender.com](https://paymenttransactionseudashpy.onrender.com/)

> El servidor de Render puede tardar ~30 segundos en despertar si lleva tiempo inactivo.

---

## Requisitos

- Python 3.9 o superior

---

## Instalación y uso

```bash
# 1. Clonar el repositorio
git clone https://github.com/T1fff/PaymentTransactionsEUDashPy.git
cd PaymentTransactionsEUDashPy
desde VS Code: **File → Open Folder** y selecciona la carpeta clonada.

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Correr la app
python app.py

# 6. Abrir en el navegador
# http://127.0.0.1:8051
```

## Datos

El dataset se encuentra cargado en el repositorio.

De la misma manera, está almacenado con **Git LFS** en: [https://media.githubusercontent.com/media/T1fff/data/refs/heads/main/data_payments.csv].

O descarga directamente del BCE:  
[sdw.ecb.europa.eu](https://sdw.ecb.europa.eu/browse.do?node=9691136)

---

## Estructura del proyecto

```
PaymentTransactionsEUDashPy/
├── app.py                    # Archivo principal Dash
├── requirements.txt
├── assets/
│   └── style.css             # Estilos personalizados
├── data/
│   └── payments_eu.csv       # Dataset de transacciones (Git LFS)
├── pages/
│   ├── introduccion.py
│   ├── objetivos.py
│   ├── problema.py
│   ├── univariado.py
│   ├── multivariado.py
│   └── conclusiones.py
└── utils/
    └── data_loader.py        # Carga y preprocesamiento
```

---

## Autores

Tiffany Mendoza S. y Sergio Rada · 2026


```
