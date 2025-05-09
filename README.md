# 📔 Memories App

Este projeto é um aplicativo de memórias pessoais onde os usuários podem criar, visualizar, editar e apagar registros com título, descrição, imagem e tags.


---

## 🚀 Tecnologias Utilizadas

### 🔙 Back-end (Flask)
- Python 3
- Flask
- Flask-CORS
- SQLite

### 📱 Front-end (React Native)
- React Native com Expo
- Axios
- React Navigation

---

## ⚙️ Como executar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/ClaytonLucas/memories_app.git
cd memories_app
```

### 2. Back-end (Flask)

```bash
cd memories-backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run --host=0.0.0.0
```
A API será iniciada em: http://localhost:5000

### 3. Front-end (React Native)
```bash
cd ../memories-frontend
npm install
expo start
```
Você pode escanear o QR code no terminal com o aplicativo Expo Go no celular para testar.

⚠️ Importante: certifique-se de que a URL do back-end (em api.js) esteja apontando corretamente para o IP local ou para http://localhost:5000 se estiver usando um emulador.

---

## ✨ Funcionalidades
- Criar novas memórias com título, descrição, imagem e tags

- Visualizar todas as memórias

- Editar memórias existentes

- Apagar memórias

- Interface amigável e mobile-first

---

## 📂 Organização dos Diretórios
- memories-backend/: Contém a API Flask (app.py, banco SQLite, etc)

- memories-frontend/: Contém os arquivos React Native com navegação, telas e componentes

---
## 📄 Licença
- Este projeto está sob a licença MIT.



