//POST login

async function sendLogin() {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-senha").value;

        const resposta = await fetch("http://localhost:3000/login", {
                method: "POST",
                        headers: {
                        "Content-Type": "application/json"
                        },
                body: JSON.stringify({
                        email: email,
                        password: password
                        })
        });

        const dados = await resposta.json();
        console.log(dados);

        if(resposta.ok){
                
                localStorage.setItem("cliente", JSON.stringify({
                        id: dados.usuario_id,
                        isAdmin: dados.isAdmin,
                        nome: dados.nome
                }));

              window.location.href = "homePage.html";  

        }else {
            alert("Erro no login: " + (dados.detail || "Credenciais inválidas"));
        }

}

//POST signup
async function sendSignup() {

        const email = document.getElementById("signup-email").value;
        const name = document.getElementById("name").value;
        const cpf = document.getElementById("cpf").value;
        const password = document.getElementById("password").value;
        const isAdmin = document.getElementById("isAdmin").value;
        const filial = document.getElementById("filial").value;
        const numeroTel = document.getElementById("numeroTel").value;
        const wallet = document.getElementById("wallet").value;
        
        const resposta = await fetch("http://localhost:3000/signup", {
                method: "POST",
                        headers: {
                        "Content-Type": "application/json"
                        },
                body: JSON.stringify({
                        email: email,
                        nome: name,
                        CPF: cpf,
                        password: password,
                        isAdmin: isAdmin,
                        filial: filial,
                        numeroTel: numeroTel,
                        wallet: wallet
                        })
        });

        const dados = await resposta.json();
        console.log(dados);
}

//POST cadastroLugar
async function sendNewPlace() {

        const cadastroEspacoNumero = document.getElementById("cadastroEspacoNumero").value;
        const cadastroEspacoLoc = document.getElementById("cadastroEspacoLoc").value;
        const cadastroEspacoNome = document.getElementById("cadastroEspacoNome").value;
        const cadastroEspacoValor = document.getElementById("cadastroEspacoValor").value;
        const cadastroEspacoCapacidade = document.getElementById("cadastroEspacoCapacidade").value;

        const resposta = await fetch("http://localhost:3000/properties/create", {
                method: "POST",
                        headers: {
                        "Content-Type": "application/json"
                        },
                body: JSON.stringify({
                        address: cadastroEspacoLoc,
                        contact: cadastroEspacoNumero,
                        property_name: cadastroEspacoNome,
                        value_per_day: Number(cadastroEspacoValor),
                        capacity: Number(cadastroEspacoCapacidade)
                        })
        });

        //const dados = await resposta.json();
        //console.log(dados);

}

async function carregarEspacosRemocao() {
    try {
        const resposta = await fetch("http://localhost:3000/properties/get/all");

        if (!resposta.ok) {
            console.error("Erro:", resposta.status);
            return;
        }

        const espacos = await resposta.json();
        const tabela = document.getElementById("listaEspacos");

        tabela.innerHTML = ""; // limpa a tabela

        espacos.forEach(espaco => {
            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${espaco.id}</td>
                <td>${espaco.property_name}</td>
                <td>${espaco.address}</td>
                <td>${espaco.contact}</td>
                <td>R$ ${espaco.value_per_day}</td>
                <td>${espaco.capacity}</td>
                <td>
                    <button onclick="removerEspaco(${espaco.id})">
                        Remover
                    </button>
                </td>
            `;

            tabela.appendChild(linha);
        });

    } catch (erro) {
        console.error("Erro ao carregar espaços:", erro);
    }
}

async function removerEspaco(id){

        try {
        const resposta = await fetch(`http://localhost:3000/properties/delete/${id}`, {
            method: "DELETE"
        });

        if (!resposta.ok) {
            console.error("Erro ao deletar espaço:", resposta.status);
            return;
        }

        // Recarrega a lista automaticamente
        carregarEspacosRemocao();

    } catch (erro) {
        console.error("Erro no request DELETE:", erro);
        alert("Erro ao remover espaço!");
    }


}

async function atualizarEspaco() {
        const id = document.getElementById("updId").value;

        if (!id) {
                alert("Digite o ID do espaço!");
                return;
        }

        const data = {};

        const nome = document.getElementById("updNome").value;
        const contato = document.getElementById("updContato").value;
        const valor = document.getElementById("updValor").value;
        const capacidade = document.getElementById("updCapacidade").value;

        if (nome !== "") data.property_name = nome;
        if (contato !== "") data.contact = contato;
        if (valor !== "") data.value_per_day = Number(valor);
        if (capacidade !== "") data.capacity = Number(capacidade);

        if (Object.keys(data).length === 0) {
                alert("Nenhum campo para atualizar.");
                return;
        }

        const resposta = await fetch(`http://localhost:3000/properties/update/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
        });

        if (!resposta.ok) {
                alert("Erro ao atualizar espaço.");
                return;
        }
}

async function carregarEspacosReserva() {
    try {
        const resposta = await fetch("http://localhost:3000/properties/get/all");

        if (!resposta.ok) {
            console.error("Erro:", resposta.status);
            return;
        }

        const espacos = await resposta.json();
        const tabela = document.getElementById("listaEspacosReserva");

        tabela.innerHTML = ""; // limpa a tabela

        espacos.forEach(espaco => {
            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${espaco.id}</td>
                <td>${espaco.property_name}</td>
                <td>${espaco.address}</td>
                <td>${espaco.contact}</td>
                <td>R$ ${espaco.value_per_day}</td>
                <td>${espaco.capacity}</td>
            `;

            tabela.appendChild(linha);
        });

    } catch (erro) {
        console.error("Erro ao carregar espaços:", erro);
    }
}

async function reservarEspacoManual() {

    // pega o usuário logado do localStorage
    const cliente = JSON.parse(localStorage.getItem("cliente"));

    if (!cliente || !cliente.id) {
        alert("Você precisa estar logado para fazer uma reserva.");
        return;
    }

    const renterId = cliente.id;

    const id = document.getElementById("reservaId").value;
    const inicio = document.getElementById("reservaInicio").value;
    const fim = document.getElementById("reservaFim").value;

    if (!id || !inicio || !fim) {
        alert("Preencha todos os campos!");
        return;
    }

    const body = {
        renter_id: renterId,      // <- AGORA VAI JUNTO
        property_id: Number(id),
        initTime: inicio,
        endTime: fim
    };

    const resposta = await fetch("http://localhost:3000/reserve/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!resposta.ok) {
        alert("Erro ao reservar.");
        return;
    }

    alert("Reserva criada com sucesso!");
}

async function carregarMinhasReservas() {
    try {
        // pega o usuário logado do localStorage
        const cliente = JSON.parse(localStorage.getItem("cliente"));

        if (!cliente || !cliente.id) {
            alert("Você precisa estar logado para ver suas reservas.");
            return;
        }

        const renterId = cliente.id;

        // chama o endpoint passando o renter_id
        const resposta = await fetch(`http://localhost:3000/reserve/get/${renterId}`);

        if (!resposta.ok) {
            console.error("Erro:", resposta.status);
            alert("Erro ao carregar reservas.");
            return;
        }

        const reservas = await resposta.json();
        const tabela = document.getElementById("listaMinhasReservas");

        tabela.innerHTML = ""; // limpa tabela

        reservas.forEach(r => {
            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${r.id}</td>
                <td>${r.property_id}</td>
                <td>${r.initTime}</td>
                <td>${r.endTime}</td>
                <td>${r.capacity}</td>
            `;

            tabela.appendChild(linha);
        });

    } catch (erro) {
        console.error("Erro ao carregar reservas:", erro);
    }
}

async function deletarReserva() {
    const id = document.getElementById("deleteReservaId").value;

    if (!id) {
        alert("Digite o ID da reserva!");
        return;
    }

    const resposta = await fetch(`http://localhost:3000/reserve/delete/${id}`, {
        method: "DELETE"
    });

    if (!resposta.ok) {
        alert("Erro ao deletar reserva.");
        console.error("Status:", resposta.status);
        return;
    }

    alert("Reserva deletada com sucesso!");

    // opcional: atualizar tabela automaticamente
    carregarMinhasReservas();
}