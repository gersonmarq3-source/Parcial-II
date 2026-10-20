import pandas as pd
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

import matplotlib
matplotlib.use('Qt5Agg')  # Configura Matplotlib para usar PyQt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

app = QApplication(sys.argv)
csv_path = Path(__file__).with_name('inventario_sucursales.csv')

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    QMessageBox.critical(None, 'Error al cargar inventario',
                         f'No se encontró el archivo:\n{csv_path}')
    sys.exit(1)
except pd.errors.EmptyDataError:
    QMessageBox.critical(None, 'Error al cargar inventario',
                         'El archivo CSV está vacío.')
    sys.exit(1)
except pd.errors.ParserError as error:
    QMessageBox.critical(None, 'Error al cargar inventario',
                         f'El archivo CSV tiene un formato inválido:\n{error}')
    sys.exit(1)
except (OSError, UnicodeDecodeError) as error:
    QMessageBox.critical(None, 'Error al cargar inventario',
                         f'No se pudo leer el archivo CSV:\n{error}')
    sys.exit(1)

required_columns = {'Sucursal', 'Categoria', 'Stock', 'Precio_Unitario_USD'}
missing_columns = required_columns.difference(df.columns)
if missing_columns:
    QMessageBox.critical(
        None,
        'Error en el inventario',
        f'Faltan columnas requeridas en el CSV: {", ".join(sorted(missing_columns))}',
    )
    sys.exit(1)

if df.empty:
    QMessageBox.critical(None, 'Error en el inventario',
                         'El archivo CSV no contiene productos.')
    sys.exit(1)

numeric_columns = ['Stock', 'Precio_Unitario_USD']
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

invalid_numeric = df[numeric_columns].isna().any(axis=1)
if invalid_numeric.any():
    rows = ', '.join(str(index + 2) for index in df.index[invalid_numeric][:10])
    QMessageBox.critical(
        None,
        'Error en el inventario',
        f'Hay valores numéricos vacíos o inválidos en las filas: {rows}.',
    )
    sys.exit(1)

missing_labels = df[['Sucursal', 'Categoria']].isna().any(axis=1)
if missing_labels.any():
    rows = ', '.join(str(index + 2) for index in df.index[missing_labels][:10])
    QMessageBox.critical(
        None,
        'Error en el inventario',
        f'Faltan la sucursal o categoría en las filas: {rows}.',
    )
    sys.exit(1)

#Analizando la estructura del DataFrame
print(df.head())

#Tipos de datos
print(df.dtypes)

#Estadisticas basicas del inventario
print(df.describe())

#Desarrolle una interfaz gráfica en PyQt5 que integre gráficos generados con Matplotlib
#para mostrar visualmente la información relevante del inventario

window = QMainWindow()
window.setWindowTitle('Inventario de Sucursales')
window.setGeometry(100, 100, 905, 650)

central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

tabs = QTabWidget()
layout.addWidget(tabs)

tab1 = QWidget()
layout1 = QVBoxLayout(tab1)
fig1 = Figure(figsize=(8, 5))
canvas1 = FigureCanvas(fig1)
layout1.addWidget(canvas1)

ax1 = fig1.add_subplot(111)
stock_sucursal = df.groupby('Sucursal')['Stock'].sum()
stock_sucursal.plot(kind='bar', ax=ax1, color='#2b5c8f', edgecolor='black')
ax1.set_title('Stock Total por Sucursal', fontweight='bold')
ax1.set_ylabel('Unidades')
fig1.tight_layout()
canvas1.draw()
tabs.addTab(tab1, "Stock por Sucursal")

tab2 = QWidget()
layout2 = QVBoxLayout(tab2)
fig2 = Figure(figsize=(8, 5))
canvas2 = FigureCanvas(fig2)
layout2.addWidget(canvas2)

#grafico de pastel para mostrar el precio promedio por categoría
ax2 = fig2.add_subplot(111)
precio_cat = df.groupby('Categoria')['Precio_Unitario_USD'].mean()
precio_cat.plot(kind='bar', ax=ax2, color='#d9534f', edgecolor='black')
ax2.set_title('Precio Promedio por Categoría ($)', fontweight='bold')
ax2.set_ylabel('USD')
ax2.tick_params(axis='x', rotation=15)
fig2.tight_layout()
canvas2.draw()
tabs.addTab(tab2, "Precio por Categoría")

tab3 = QWidget()
layout3 = QVBoxLayout(tab3)
fig3 = Figure(figsize=(8, 5))
canvas3 = FigureCanvas(fig3)
layout3.addWidget(canvas3)

ax3 = fig3.add_subplot(111)
df['Valor_Total'] = df['Stock'] * df['Precio_Unitario_USD']
valor_suc = df.groupby('Sucursal')['Valor_Total'].sum()
valor_suc.plot(kind='barh', ax=ax3, color='#5cb85c', edgecolor='black')
ax3.set_title('Valor Monetario Total del Inventario ($)', fontweight='bold')
ax3.set_xlabel('USD')
fig3.tight_layout()
canvas3.draw()
tabs.addTab(tab3, "Valor del Inventario")

# Mostrar la ventana
window.show()

sys.exit(app.exec_())

