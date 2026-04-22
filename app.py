from flask import Flask, request, redirect, session, render_template_string, send_file
from datetime import datetime
from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import os
import json

app = Flask(__name__)
app.secret_key = "ebd"

usuarios = {"professor@gmail.com": "1234"}

alunos = []
import uuid
presencas = []
aulas = []
professores = []
turmas = []

# 🎨 TEMPLATE BASE (MANTIDO)
from io import BytesIO


# =========================
# 🧾 MODELO DO CERTIFICADO
# =========================
CERTIFICADO_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        font-family: Arial;
        text-align: center;
        background: #f5f5f5;
    }

    .certificado {
        width: 1000px;
        height: 700px;
        margin: auto;
        background: white;
        border: 10px solid #c9a227;
        padding: 50px;
        position: relative;
    }

    .titulo {
        font-size: 40px;
        font-weight: bold;
    }

    .nome {
        font-size: 50px;
        font-weight: bold;
        margin: 50px 0;
        color: #0b3d1f;
    }

    .texto {
        font-size: 20px;
    }

    .assinatura {
        position: absolute;
        bottom: 80px;
        width: 100%;
        display: flex;
        justify-content: space-around;
    }

    .linha {
        border-top: 1px solid #000;
        width: 250px;
        margin: auto;
    }
</style>
</head>

<body>
    <div class="certificado">

        <div class="titulo">CERTIFICADO DE CONCLUSÃO</div>

        <div class="texto">Escola Bíblica Dominical</div>

        <div class="texto">Certificamos que</div>

        <div class="nome">{{ nome }}</div>

        <div class="texto">
            concluiu com êxito as atividades da Escola Dominical.
        </div>

        <div class="assinatura">
            <div>
                <div class="linha"></div>
                Professor
            </div>

            <div>
                <div class="linha"></div>
                Pastor
            </div>
        </div>

    </div>
</body>
</html>
"""

base = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>EBD</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI';background:#f5f7fb;}
.app{display:flex;height:100vh}
.sidebar{width:240px;background:#0b3d1f;color:white;padding:20px;}
.sidebar a{display:block;color:white;padding:10px;text-decoration:none}
.main{flex:1}
.content{padding:20px}
.card{background:white;padding:20px;margin-bottom:15px;border-radius:10px}
</style>
</head>
<body>

<div class="app">
<div class="sidebar">
<h2>EBD</h2>
<a href="/dashboard">Dashboard</a>
<a href="/alunos">Alunos</a>
<a href="/chamada">Chamada</a>
<a href="/aulas">Aulas</a>
<a href="/relatorio">Relatório</a>
<a href="/certificados">Certificados</a>
<a href="/logout">Sair</a>
</div>

<div class="main">
<div class="content">
<span>{{ titulo }}</span>
{{ conteudo|safe }}
</div>
</div>
</div>

</body>
</html>
<style>
*{margin:0;padding:0;box-sizing:border-box}

body{
    font-family:'Segoe UI';
    background:#f5f7fb;
}

/* LAYOUT PRINCIPAL */
.app{
    display:flex;
    min-height:100vh;
}

/* SIDEBAR */
.sidebar{
    width:240px;
    background:#0b3d1f;
    color:white;
    padding:20px;
    flex-shrink:0;
}

.sidebar a{
    display:block;
    color:white;
    padding:10px;
    text-decoration:none;
}

/* CONTEÚDO */
.main{
    flex:1;
    width:100%;
}

.content{
    padding:20px;
}

/* CARDS */
.card{
    background:white;
    padding:20px;
    margin-bottom:15px;
    border-radius:10px;
    overflow-x:auto;
}

/* GRID */
.grid-3{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:15px;
}

/* =========================
   📱 MOBILE RESPONSIVO
========================= */
@media (max-width: 768px){

    .app{
        flex-direction:column;
    }

    .sidebar{
        width:100%;
        display:flex;
        overflow-x:auto;
        white-space:nowrap;
    }

    .sidebar a{
        display:inline-block;
        padding:10px 15px;
    }

    .content{
        padding:10px;
    }

    .grid-3{
        grid-template-columns:1fr;
    }

    table{
        font-size:12px;
    }

    input, select, textarea{
        width:100%;
        font-size:14px;
    }
}
</style>
"""


# 🔐 LOGIN (CORRIGIDO)
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if usuarios.get(request.form["email"]) == request.form["senha"]:
            session["user"] = True
            return redirect("/dashboard")

        erro = "E-mail ou senha inválidos"
    else:
        erro = ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Login - EBD</title>

    <style>
    body {{
        margin:0;
        font-family: 'Segoe UI', Arial;
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        background: linear-gradient(135deg, #0b3d1f, #145a32, #1e8449);
    }}

    .login-box {{
        background:#fff;
        width:360px;
        padding:30px;
        border-radius:15px;
        box-shadow:0 10px 30px rgba(0,0,0,0.3);
        text-align:center;
    }}

    .login-box h2 {{
        margin-bottom:20px;
        color:#0b3d1f;
    }}

    .input {{
        width:100%;
        padding:12px;
        margin:10px 0;
        border:1px solid #ddd;
        border-radius:8px;
        outline:none;
        transition:0.3s;
    }}

    .input:focus {{
        border-color:#1e8449;
        box-shadow:0 0 5px rgba(30,132,73,0.3);
    }}

    .btn {{
        width:100%;
        padding:12px;
        background:#1e8449;
        color:white;
        border:none;
        border-radius:8px;
        cursor:pointer;
        font-weight:bold;
        transition:0.3s;
    }}

    .btn:hover {{
        background:#145a32;
    }}

    .error {{
        color:red;
        font-size:14px;
        margin-top:10px;
    }}

    .logo {{
        font-size:26px;
        font-weight:bold;
        color:#0b3d1f;
        margin-bottom:10px;
    }}
    </style>
    </head>

    <body>

    <div class="login-box">
        <div class="logo">📖 EBD System</div>
        <h2>Entrar</h2>

        <form method="POST">
            <input class="input" name="email" placeholder="E-mail">
            <input class="input" type="password" name="senha" placeholder="Senha">
            <button class="btn">Acessar</button>
        </form>

        <div class="error">{erro}</div>
        
    </div>

    </body>
    </html>
    """

@app.route("/dashboard")
def dashboard():

    # =========================
    # 📊 CÁLCULOS DE PRESENÇA
    # =========================
    total_presencas = 0
    total_faltas = 0

    por_aluno = {}

    for r in presencas:
        for d in r.get("dados", []):
            nome = d["nome"]

            if nome not in por_aluno:
                por_aluno[nome] = {"presente": 0, "falta": 0}

            if d["status"] == "presente":
                por_aluno[nome]["presente"] += 1
                total_presencas += 1
            else:
                por_aluno[nome]["falta"] += 1
                total_faltas += 1

    # =========================
    # 📚 AULAS POR DATA
    # =========================
    aulas_por_data = {}

    for r in presencas:
        data = r["data"]
        aulas_por_data[data] = aulas_por_data.get(data, 0) + 1

    # =========================
    # 📦 DADOS PARA JS
    # =========================
    alunos_labels = list(por_aluno.keys())
    presencas_data = [por_aluno[a]["presente"] for a in alunos_labels]
    faltas_data = [por_aluno[a]["falta"] for a in alunos_labels]

    datas_aulas = list(aulas_por_data.keys())
    aulas_qtd = list(aulas_por_data.values())

    taxa_freq = 0
    if (total_presencas + total_faltas) > 0:
        taxa_freq = round((total_presencas / (total_presencas + total_faltas)) * 100, 1)

    # =========================
    # 👨‍🎓 ALUNOS MATRICULADOS
    # =========================
    total_alunos = len(alunos)

    # =========================
    # 🏫 ALUNOS POR TURMA
    # =========================
    alunos_por_turma = {}

    for a in alunos:
        turma = a.get("turma", "Sem turma")
        alunos_por_turma[turma] = alunos_por_turma.get(turma, 0) + 1

    # =========================
    # 🥇 RANKING PRESENÇAS / FALTAS
    # =========================
    ranking = {}

    for r in presencas:
        for d in r.get("dados", []):
            nome = d["nome"]

            if nome not in ranking:
                ranking[nome] = {"presente": 0, "falta": 0}

            if d["status"] == "presente":
                ranking[nome]["presente"] += 1
            else:
                ranking[nome]["falta"] += 1

    ranking_presenca = sorted(
        ranking.items(),
        key=lambda x: x[1]["presente"],
        reverse=True
    )

    ranking_falta = sorted(
        ranking.items(),
        key=lambda x: x[1]["falta"],
        reverse=True
    )

    # =========================
    # 📊 HTML DO DASHBOARD
    # =========================
    conteudo = f"""
    <div class="grid-3">

        <div class="card">
            <h3>👨‍🎓 Alunos Matriculados</h3>
            <h2>{total_alunos}</h2>
        </div>

        <div class="card">
            <h3>📊 Presenças</h3>
            <h2>{total_presencas}</h2>
        </div>

        <div class="card">
            <h3>❌ Faltas</h3>
            <h2>{total_faltas}</h2>
        </div>

    </div>

    <div class="card">
        <h3>🏫 Alunos por Turma</h3>
        <canvas id="graficoTurmas"></canvas>
    </div>

    <div class="card">
        <h3>📈 Frequência por Aluno</h3>
        <canvas id="graficoAlunos"></canvas>
    </div>

    <div class="grid-3">

        <div class="card">
            <h3>🥇 Mais Presentes</h3>
            {"".join([
                f"<p>{n[0]} - {n[1]['presente']} presenças</p>"
                for n in ranking_presenca[:5]
            ])}
        </div>

        <div class="card">
            <h3>📉 Mais Faltas</h3>
            {"".join([
                f"<p>{n[0]} - {n[1]['falta']} faltas</p>"
                for n in ranking_falta[:5]
            ])}
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>

    // =========================
    // 📊 ALUNOS
    // =========================
    new Chart(document.getElementById('graficoAlunos'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(alunos_labels)},
            datasets: [
                {{
                    label: 'Presenças',
                    data: {json.dumps(presencas_data)},
                    backgroundColor: '#1e8449'
                }},
                {{
                    label: 'Faltas',
                    data: {json.dumps(faltas_data)},
                    backgroundColor: '#c0392b'
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false
        }}
    }});

    // =========================
    // 🏫 TURMAS
    // =========================
    new Chart(document.getElementById('graficoTurmas'), {{
        type: 'doughnut',
        data: {{
            labels: {json.dumps(list(alunos_por_turma.keys()))},
            datasets: [{{
                data: {json.dumps(list(alunos_por_turma.values()))},
                backgroundColor: ['#2980b9','#27ae60','#8e44ad','#f39c12','#c0392b']
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false
        }}
    }});

    </script>
    """

    return render_template_string(base, titulo="Dashboard Inteligente", conteudo=conteudo)
    
#CADASTRO DO PROFESSOR

@app.route("/professores", methods=["GET","POST"])
def professores_view():

    if request.method == "POST":
        professores.append({
            "id": len(professores) + 1,
            "nome": request.form["nome"],
            "email": request.form["email"],
            "especialidade": request.form["especialidade"]
        })

    conteudo = """
    <div class="card">
        <h2>👨‍🏫 Cadastro de Professores</h2>

        <form method="POST">
            <input name="nome" placeholder="Nome"><br><br>
            <input name="email" placeholder="Email"><br><br>
            <input name="especialidade" placeholder="Especialidade"><br><br>

            <button style="padding:10px;background:#1e8449;color:white;border:none;">
                Salvar Professor
            </button>
        </form>
    </div>
    """

    for p in professores:
        conteudo += f"""
        <div class="card">
            <b>{p['nome']}</b><br>
            {p['email']}<br>
            {p['especialidade']}
        </div>
        """

    return render_template_string(base, titulo="Professores", conteudo=conteudo)

# CADASTRO DE TURMAS

@app.route("/turmas", methods=["GET","POST"])
def turmas_view():

    if request.method == "POST":
        turmas.append({
            "id": len(turmas) + 1,
            "nome": request.form["nome"],
            "professor": request.form["professor"],
            "duracao": request.form["duracao"]
        })

    conteudo = """
    <div class="card">
        <h2>🏫 Cadastro de Turmas</h2>

        <form method="POST">
            <input name="nome" placeholder="Nome da turma"><br><br>

            <input name="professor" placeholder="Professor responsável"><br><br>

            <input name="duracao" placeholder="Duração (ex: 6 meses, 1 ano)"><br><br>

            <button style="padding:10px;background:#2980b9;color:white;border:none;">
                Criar Turma
            </button>
        </form>
    </div>
    """

    for t in turmas:
        conteudo += f"""
        <div class="card">
            <h3>🏫 {t['nome']}</h3>
            👨‍🏫 {t['professor']}<br>
            ⏳ {t['duracao']}
        </div>
        """

    return render_template_string(base, titulo="Turmas", conteudo=conteudo)

# ALUNOS
@app.route("/alunos", methods=["GET","POST"])
def alunos_view():

    # =========================
    # 📌 CADASTRO
    # =========================
    if request.method == "POST":
        alunos.append({
            "codigo": str(uuid.uuid4())[:8],  # 👈 CÓDIGO DO ALUNO
            "nome": request.form["nome"],
            "email": request.form["email"],
            "telefone": request.form["telefone"],
            "nascimento": request.form["nascimento"],
            "turma": request.form["turma"],
            "responsavel": request.form["responsavel"],
            "cpf": request.form["cpf"],
            "status": "ativo",
            "data_matricula": datetime.now().strftime("%d/%m/%Y")
        })
        return redirect("/alunos")

    # =========================
    # 📌 LISTA PROFISSIONAL
    # =========================
    lista = ""

    for a in alunos:
        lista += f"""
        <div class="card">
            <h3>👨‍🎓 {a['nome']}</h3>

            <p><b>Código:</b> {a.get('codigo','-')}</p>
            <p>📧 {a.get('email','-')}</p>
            <p>📱 {a.get('telefone','-')}</p>
            <p>🎂 {a.get('nascimento','-')}</p>
            <p>🏫 {a.get('turma','-')}</p>
            <p>👨‍👩‍👧 {a.get('responsavel','-')}</p>
            <p>🆔 {a.get('cpf','-')}</p>
            <p>📅 {a.get('data_matricula','-')}</p>

            <p>
                <b>Status:</b>
                <span style="color:{'green' if a['status']=='ativo' else 'red'}">
                    {a['status'].upper()}
                </span>
            </p>

            <a href="/alunos/editar/{a['codigo']}" 
               style="display:inline-block;margin-top:10px;
               padding:8px 12px;background:#2980b9;color:white;
               border-radius:6px;text-decoration:none;">
               ✏️ Editar
            </a>
        </div>
        """

    # =========================
    # 📌 FORMULÁRIO PROFISSIONAL
    # =========================
    conteudo = f"""
    <div class="card">
        <h2>🎓 Matrícula de Aluno</h2>

        <form method="POST"
        style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">

            <input name="nome" placeholder="Nome completo" required>
            <input name="email" placeholder="E-mail" required>

            <input name="telefone" placeholder="Telefone" required>
            <input type="date" name="nascimento" required>

            <input name="cpf" placeholder="CPF" required>
            <input name="responsavel" placeholder="Responsável" required>

            <input name="turma" placeholder="Turma" style="grid-column:span 2" required>

            <button style="grid-column:span 2;
            padding:12px;background:#0b3d1f;color:white;
            border:none;border-radius:8px;">
                Matricular
            </button>

        </form>
    </div>

    <div style="margin-top:20px;">
        {lista}
    </div>
    """

    return render_template_string(base, titulo="Gestão de Alunos", conteudo=conteudo)

# ✏️ EDITAR ALUNO
@app.route("/alunos/editar/<codigo>", methods=["GET","POST"])
def editar_aluno(codigo):

    aluno = next((a for a in alunos if a["codigo"] == codigo), None)

    if not aluno:
        return "Aluno não encontrado"

    if request.method == "POST":
        aluno["nome"] = request.form["nome"]
        aluno["email"] = request.form["email"]
        aluno["telefone"] = request.form["telefone"]
        aluno["turma"] = request.form["turma"]
        aluno["status"] = request.form["status"]

        return redirect("/alunos")

    conteudo = f"""
    <div class="card">
        <h2>✏️ Editar Aluno</h2>

        <form method="POST">

            <input name="nome" value="{aluno['nome']}" required>
            <input name="email" value="{aluno['email']}" required>
            <input name="telefone" value="{aluno['telefone']}" required>
            <input name="turma" value="{aluno['turma']}" required>
            <input name="turma" placeholder="Turma do aluno">

            <select name="status">
                <option value="ativo" {"selected" if aluno["status"]=="ativo" else ""}>Ativo</option>
                <option value="inativo" {"selected" if aluno["status"]=="inativo" else ""}>Inativo</option>
            </select>

            <button style="margin-top:10px;padding:10px;background:#1e8449;color:white;border:none;">
                Salvar
            </button>

        </form>
    </div>
    """

    return render_template_string(base, titulo="Editar Aluno", conteudo=conteudo)

@app.route("/chamada", methods=["GET","POST"])
def chamada():

    if request.method == "POST":
        registro = {
            "data": request.form["data"],
            "dados": []
        }

        for a in alunos:
            nome = a["nome"]
            status = request.form.get(nome)
            justificativa = request.form.get(f"just_{nome}", "")

            registro["dados"].append({
                "nome": nome,
                "status": status,
                "justificativa": justificativa
            })

        presencas.append(registro)
        return redirect("/relatorio")

    # =========================
    # 🎓 TELA PROFISSIONAL (DIÁRIO DE CLASSE)
    # =========================

    tabela = ""

    for a in alunos:
        tabela += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #eee;">
                👨‍🎓 {a['nome']}
            </td>

            <td style="padding:10px;border-bottom:1px solid #eee;">
                {a['turma']}
            </td>

            <td style="padding:10px;border-bottom:1px solid #eee;">
                <select name="{a['nome']}" style="
                    padding:6px;
                    border-radius:6px;
                    border:1px solid #ccc;
                ">
                    <option value="presente">✔ Presente</option>
                    <option value="falta">❌ Falta</option>
                </select>
            </td>

            <td style="padding:10px;border-bottom:1px solid #eee;">
                <input name="just_{a['nome']}" placeholder="Justificativa"
                    style="padding:6px;width:100%;border:1px solid #ddd;border-radius:6px;">
            </td>
        </tr>
        """

    conteudo = f"""
<div class="card">

    <h2>📖 Diário de Classe - Chamada</h2>
    <p style="color:#666;margin-bottom:15px;">
        Registre a presença dos alunos como em uma escola real
    </p>

    <form method="POST">

        <div style="margin-bottom:15px;">
            <label>📅 Data da Aula</label><br>
            <input type="date" name="data" style="
                padding:8px;
                border:1px solid #ccc;
                border-radius:6px;
                margin-top:5px;
            ">
        </div>

        <div class="table-container">
            <table style="width:100%;border-collapse:collapse;">

                <thead>
                    <tr style="background:#0b3d1f;color:white;">
                        <th style="padding:10px;text-align:left;">Aluno</th>
                        <th style="padding:10px;text-align:left;">Turma</th>
                        <th style="padding:10px;text-align:left;">Status</th>
                        <th style="padding:10px;text-align:left;">Justificativa</th>
                    </tr>
                </thead>

                <tbody>
                    {tabela}
                </tbody>

            </table>
        </div>

        <button style="
            margin-top:15px;
            padding:12px 20px;
            background:#1e8449;
            color:white;
            border:none;
            border-radius:8px;
            cursor:pointer;
            font-weight:bold;
        ">
            💾 Salvar Chamada
        </button>

    </form>

</div>
"""

    return render_template_string(base, titulo="📚 Diário de Classe", conteudo=conteudo)

# 📊 RELATÓRIO (AJUSTADO + BOTÃO PDF)
@app.route("/relatorio")
def relatorio():

    # =========================
    # 📌 CABEÇALHO ESTATÍSTICO (ESCOLA REAL)
    # =========================
    total_alunos = len(alunos)
    total_aulas = len(presencas)

    total_presencas = 0
    total_faltas = 0

    for r in presencas:
        for d in r.get("dados", []):
            if d["status"] == "presente":
                total_presencas += 1
            else:
                total_faltas += 1

    frequencia = 0
    if (total_presencas + total_faltas) > 0:
        frequencia = round((total_presencas / (total_presencas + total_faltas)) * 100, 1)

    # =========================
    # 📌 CONTEÚDO PRINCIPAL
    # =========================
    conteudo = f"""
    <div class="card">
        <h2>📊 Relatório Geral da Escola Bíblica</h2>

        <div class="grid-3">

            <div class="card">
                <h3>👨‍🎓 Alunos</h3>
                <h2>{total_alunos}</h2>
            </div>

            <div class="card">
                <h3>📚 Aulas</h3>
                <h2>{total_aulas}</h2>
            </div>

            <div class="card">
                <h3>✅ Presenças</h3>
                <h2>{total_presencas}</h2>
            </div>

            <div class="card">
                <h3>❌ Faltas</h3>
                <h2>{total_faltas}</h2>
            </div>

        </div>

        <div style="margin-top:15px;">
            <h3>📈 Frequência Geral</h3>
            <h1 style="color:#1e8449">{frequencia}%</h1>
        </div>
    </div>
    """

    # =========================
    # 📌 DETALHAMENTO POR AULA
    # =========================
    for r in presencas:

        conteudo += f"""
        <div class="card">
            <h3>📅 Aula do dia: {r['data']}</h3>

        <div class="table-container">
        <table style="width:100%;border-collapse:collapse;">

            <thead>
                <tr style="background:#0b3d1f;color:white;">
                    <th style="padding:8px;">Aluno</th>
                    <th>Status</th>
                    <th>Justificativa</th>
                </tr>
            </thead>

            <tbody>
            """

        for d in r.get("dados", []):
            cor = "#1e8449" if d["status"] == "presente" else "#c0392b"

    conteudo += f"""
        <tr style="text-align:center;">
            <td style="padding:8px;">{d['nome']}</td>
            <td style="color:{cor};font-weight:bold;">
                {d['status'].upper()}
            </td>
            <td>{d['justificativa']}</td>
        </tr>
        """

    conteudo += """
            </tbody>
        </table>
    </div>
</div>
"""

    # =========================
    # 📌 BOTÃO PDF
    # =========================
    conteudo += """
    <div class="card">
        <a href="/exportar_pdf"
           style="padding:10px 15px;background:#2980b9;
           color:white;border-radius:6px;text-decoration:none;">
           📄 Exportar Relatório PDF
        </a>
    </div>
    """
    return render_template_string(base, titulo="Relatório Escolar Completo", conteudo=conteudo)

# 📄 EXPORTAÇÃO PDF (OBRIGATÓRIA)
@app.route("/exportar_pdf")
def exportar_pdf():

    gerar_graficos_pdf()

    doc = SimpleDocTemplate("relatorio.pdf")
    styles = getSampleStyleSheet()
    elementos = []

    # =========================
    # 📌 RESUMO GERAL
    # =========================
    total_alunos = len(alunos)
    ativos = len([a for a in alunos if a.get("status") == "ativo"])
    inativos = total_alunos - ativos
    total_aulas = len(presencas)

    pres = 0
    falt = 0

    for r in presencas:
        for d in r.get("dados", []):
            if d["status"] == "presente":
                pres += 1
            else:
                falt += 1

    freq = 0
    if (pres + falt) > 0:
        freq = round((pres / (pres + falt)) * 100, 1)

    # =========================
    # 🏫 CABEÇALHO ESCOLAR
    # =========================
    elementos.append(Paragraph("RELATÓRIO OFICIAL - ESCOLA BÍBLICA DOMINICAL", styles["Title"]))
    elementos.append(Paragraph("Sistema de Gestão Escolar - Frequência e Matrículas", styles["Normal"]))
    elementos.append(Paragraph(" ", styles["Normal"]))

    # =========================
    # 📊 RESUMO EXECUTIVO
    # =========================
    elementos.append(Paragraph("RESUMO GERAL", styles["Heading2"]))
    elementos.append(Paragraph(f"Total de alunos: {total_alunos}", styles["Normal"]))
    elementos.append(Paragraph(f"Alunos ativos: {ativos}", styles["Normal"]))
    elementos.append(Paragraph(f"Alunos inativos: {inativos}", styles["Normal"]))
    elementos.append(Paragraph(f"Aulas realizadas: {total_aulas}", styles["Normal"]))
    elementos.append(Paragraph(f"Frequência geral: {freq}%", styles["Normal"]))
    elementos.append(Paragraph(" ", styles["Normal"]))

    # =========================
    # 📈 GRÁFICOS
    # =========================
    elementos.append(Paragraph("ANÁLISE GRÁFICA", styles["Heading2"]))
    elementos.append(Paragraph(" ", styles["Normal"]))

    if os.path.exists("grafico_presenca.png"):
        elementos.append(Paragraph("Presenças por aluno", styles["Heading3"]))
        elementos.append(Paragraph(" ", styles["Normal"]))

    if os.path.exists("grafico_presenca.png"):
        from reportlab.platypus import Image
        img = Image("grafico_presenca.png", width=400, height=200)
        elementos.append(img)

    elementos.append(Paragraph(" ", styles["Normal"]))

    if os.path.exists("grafico_falta.png"):
        elementos.append(Paragraph("Faltas por aluno", styles["Heading3"]))
        img2 = Image("grafico_falta.png", width=400, height=200)
        elementos.append(img2)

    elementos.append(Paragraph(" ", styles["Normal"]))

    # =========================
    # 📚 DETALHAMENTO
    # =========================
    elementos.append(Paragraph("DETALHAMENTO DAS AULAS", styles["Heading2"]))

    for r in presencas:
        elementos.append(Paragraph(f"Aula: {r['data']}", styles["Heading3"]))

        for d in r.get("dados", []):
            texto = f"{d['nome']} - {d['status']} - {d['justificativa']}"
            elementos.append(Paragraph(texto, styles["Normal"]))

        elementos.append(Paragraph(" ", styles["Normal"]))

    doc.build(elementos)

    return send_file("relatorio.pdf", as_attachment=True)

def gerar_graficos_pdf():

    nomes = []
    pres = []
    falt = []

    for a in alunos:
        nomes.append(a["nome"])
        pres.append(0)
        falt.append(0)

    for r in presencas:
        for d in r.get("dados", []):
            if d["nome"] in nomes:
                i = nomes.index(d["nome"])

                if d["status"] == "presente":
                    pres[i] += 1
                else:
                    falt[i] += 1

    # =========================
    # 📊 GRÁFICO PRESENÇA
    # =========================
    plt.figure(figsize=(6,3))
    plt.bar(nomes, pres, color="green")
    plt.title("Presenças por aluno")
    plt.xticks(rotation=45)
    plt.tight_layout()
    import matplotlib
    matplotlib.use('Agg')
    plt.close()

    # =========================
    # 📊 GRÁFICO FALTA
    # =========================
    plt.figure(figsize=(6,3))
    plt.bar(nomes, falt, color="red")
    plt.title("Faltas por aluno")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("grafico_falta.png")
    plt.close()

@app.route("/aulas", methods=["GET","POST"])
def aulas_view():

    if request.method == "POST":

        aulas.append({
            "tema": request.form["tema"],
            "versiculo": request.form.get("versiculo", ""),
            "turma": request.form.get("turma", "Geral"),
            "professor": request.form.get("professor", "Não definido"),
            "data": request.form.get("data", datetime.now().strftime("%Y-%m-%d")),
            "conteudo": request.form.get("conteudo", "")
        })

    conteudo = """
    <div class="card">
        <h2>📚 Cadastro de Aulas (SGE)</h2>

        <form method="POST">

            <input name="tema" placeholder="Tema da aula"><br><br>
            <input name="versiculo" placeholder="Versículo"><br><br>
            <input name="turma" placeholder="Turma"><br><br>
            <input name="professor" placeholder="Professor"><br><br>
            <input type="date" name="data"><br><br>
            <textarea name="conteudo" placeholder="Conteúdo da aula"></textarea><br><br>

            <button style="padding:10px;background:#0b3d1f;color:white;border:none;">
                Salvar Aula
            </button>

        </form>
    </div>
    """

    for a in aulas:
        conteudo += f"""
        <div class="card">
            <h3>📚 {a.get('tema','-')}</h3>
            📖 Versículo: {a.get('versiculo','-')}<br>
            🏫 Turma: {a.get('turma','-')}<br>
            👨‍🏫 Professor: {a.get('professor','-')}<br>
            📅 Data: {a.get('data','-')}<br>
            📝 {a.get('conteudo','-')}
        </div>
        """

    return render_template_string(base, titulo="Aulas (SGE)", conteudo=conteudo)
    


from flask import render_template_string, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from urllib.request import urlopen
from urllib.parse import quote

# =========================
# 📌 IMAGENS OFICIAIS
# =========================
LOGO_URL = "https://seeklogo.com/images/A/assembleia-de-deus-al-logo-B791E442B6-seeklogo.com.png"
WATERMARK_URL = "https://cdn.slidesharecdn.com/ss_thumbnails/ebdlicao8-1t-2019pps-190226104522-thumbnail-4.jpg?cb=1551177951"


# =========================
# 📌 LISTA DE CERTIFICADOS
# =========================
@app.route("/certificados")
def certificados():

    conteudo = "<div class='card'><h2>🏅 Certificados</h2>"

    for a in alunos:

        nome_url = quote(a["nome"])

        conteudo += f"""
        <div class="card">
            <h3>{a['nome']}</h3>

            <a href="/certificado/{nome_url}"
               style="padding:8px 12px;background:#0b3d1f;
               color:white;text-decoration:none;border-radius:6px;">
               📄 Gerar Certificado
            </a>
        </div>
        """

    conteudo += """
    <div class="card" style="margin-top:15px;">
        <a href="/certificado/lote"
           style="padding:10px 15px;background:#2980b9;
           color:white;text-decoration:none;border-radius:6px;">
           📦 Baixar Lote PDF
        </a>
    </div>
    </div>
    """

    return render_template_string(base, titulo="Certificados", conteudo=conteudo)


# =========================
# 📌 PREVIEW
# =========================
@app.route("/certificado/<nome>")
def certificado(nome):

    nome = nome.replace("%20", " ")

    html = CERTIFICADO_HTML.replace("{{ nome }}", nome)

    conteudo = f"""
    <div class="card">
        <h2>👁 Pré-visualização</h2>
    </div>

    {html}

    <div class="card" style="text-align:center;">
        <a href="/certificado/pdf/{quote(nome)}"
           style="padding:12px 20px;background:#2980b9;
           color:white;border-radius:6px;text-decoration:none;">
           📥 Baixar PDF
        </a>
    </div>
    """

    return render_template_string(base, titulo="Certificado", conteudo=conteudo)


# =========================
# 📌 PDF INDIVIDUAL (PROFISSIONAL A4 PAISAGEM)
# =========================
@app.route("/certificado/pdf/<nome>")
def certificado_pdf(nome):

    nome = nome.replace("%20", " ")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))

    width, height = landscape(A4)

    # =========================
    # 🌫️ MARCA D’ÁGUA (FUNDO)
    # =========================
    try:
        watermark = ImageReader(urlopen(WATERMARK_URL))
        pdf.saveState()
        pdf.translate(width/2, height/2)
        pdf.setFillAlpha(0.12)
        pdf.drawImage(
            watermark,
            -350, -250,
            width=700,
            height=500,
            mask='auto'
        )
        pdf.restoreState()
    except:
        pass


    # =========================
    # 🟡 LOGO TOPO
    # =========================
    try:
        logo = ImageReader(urlopen(LOGO_URL))
        pdf.drawImage(
            logo,
            width/2 - 60,
            height - 110,
            width=120,
            height=80,
            mask='auto'
        )
    except:
        pass


    # =========================
    # 🎨 BORDA PROFISSIONAL
    # =========================
    pdf.setStrokeColorRGB(0.78, 0.64, 0.13)
    pdf.setLineWidth(6)
    pdf.rect(25, 25, width - 50, height - 50)

    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.setLineWidth(1.5)
    pdf.rect(45, 45, width - 90, height - 90)


    # =========================
    # 🎓 TÍTULO
    # =========================
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width/2, height - 140, "CERTIFICADO DE CONCLUSÃO")

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(width/2, height - 190, "Escola Bíblica Dominical")


    # =========================
    # 👤 NOME
    # =========================
    pdf.setFont("Helvetica-Bold", 40)
    pdf.setFillColorRGB(0.05, 0.25, 0.12)
    pdf.drawCentredString(width/2, height/2 + 20, nome)
    pdf.setFillColorRGB(0, 0, 0)


    # =========================
    # 📜 TEXTO
    # =========================
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width/2,
        height/2 - 40,
        "Certificamos que concluiu com êxito as atividades da Escola Bíblica Dominical"
    )


    # =========================
    # ✍️ ASSINATURAS
    # =========================
    pdf.line(120, 120, 320, 120)
    pdf.drawString(180, 95, "Professor")

    pdf.line(width - 320, 120, width - 120, 120)
    pdf.drawString(width - 270, 95, "Pastor")


    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        download_name=f"certificado_{nome}.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )


# =========================
# 📌 CERTIFICADOS EM LOTE
# =========================
@app.route("/certificado/lote")
def certificado_lote():

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))

    width, height = landscape(A4)

    for a in alunos:

        nome = a["nome"]

        # 🌫️ MARCA D’ÁGUA
        try:
            watermark = ImageReader(urlopen(WATERMARK_URL))
            pdf.saveState()
            pdf.translate(width/2, height/2)
            pdf.setFillAlpha(0.10)
            pdf.drawImage(watermark, -350, -250, width=700, height=500, mask='auto')
            pdf.restoreState()
        except:
            pass

        # 🟡 LOGO
        try:
            logo = ImageReader(urlopen(LOGO_URL))
            pdf.drawImage(logo, width/2 - 60, height - 110, 120, 80, mask='auto')
        except:
            pass

        # 🎨 BORDA
        pdf.setStrokeColorRGB(0.78, 0.64, 0.13)
        pdf.setLineWidth(6)
        pdf.rect(25, 25, width - 50, height - 50)

        pdf.setStrokeColorRGB(0, 0, 0)
        pdf.setLineWidth(1.5)
        pdf.rect(45, 45, width - 90, height - 90)

        # 🎓 TEXTO
        pdf.setFont("Helvetica-Bold", 26)
        pdf.drawCentredString(width/2, height - 140, "CERTIFICADO DE CONCLUSÃO")

        pdf.setFont("Helvetica", 18)
        pdf.drawCentredString(width/2, height - 190, "Escola Bíblica Dominical")

        pdf.setFont("Helvetica-Bold", 34)
        pdf.setFillColorRGB(0.05, 0.25, 0.12)
        pdf.drawCentredString(width/2, height/2 + 20, nome)
        pdf.setFillColorRGB(0, 0, 0)

        pdf.setFont("Helvetica", 14)
        pdf.drawCentredString(
            width/2,
            height/2 - 40,
            "Concluiu com êxito as atividades da Escola Bíblica Dominical"
        )

        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        download_name="certificados_lote.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 🚀
if __name__ == "__main__":
    app.run()
# 🚀
if __name__ == "__main__":
    app.run()
