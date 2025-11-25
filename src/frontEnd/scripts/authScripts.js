//POST login

async function sendLogin() {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-senha").value;

        const resposta = await fetch("http://localhost:8000/login", {
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


